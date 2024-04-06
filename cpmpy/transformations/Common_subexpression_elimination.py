from ast import Expression
import copy
from cpmpy.expressions.core import Comparison, Operator, _wsum_make, _wsum_should
from cpmpy.expressions.utils import is_any_list, is_num
from cpmpy.expressions.variables import _BoolVarImpl, _IntVarImpl, _NumVarImpl
from cpmpy.transformations.flatten_model import get_or_make_var_or_list, normalized_boolexpr, normalized_numexpr


def apply_CSE(cpm_cons, expr_dict=None):

    if expr_dict is None:
        expr_dict = dict()

    newlist = []

    for expr in cpm_cons:

        if isinstance(expr, Comparison):

            exprname = expr.name
            lexpr, rexpr = expr.args
            rewritten = False

            # Rewrite 'Var == Expr' to normalized 'Expr == Var'
            if (expr.name == '==' or expr.name == '!=') \
                    and __is_flat_var(lexpr) and not __is_flat_var(rexpr):
                lexpr, rexpr = rexpr, lexpr
                rewritten = True

            # Rewrite 'BoolExpr != BoolExpr' to normalized 'BoolExpr == ~BoolExpr'
            if exprname == '!=' and lexpr.is_bool() and rexpr.is_bool():
                exprname = '=='
                rexpr = ~rexpr
                rewritten = True
            
            # already flat?
            if all(__is_flat_var(arg) for arg in [lexpr, rexpr]):
                if not rewritten:
                    newlist.append(expr)  # original
                else:
                    newlist.append(Comparison(exprname, lexpr, rexpr))
                continue
            
            # ensure rhs is var
            (rvar, rcons) = get_or_make_var(rexpr, expr_dict)
            # Reification (double implication): Boolexpr == Var
            if exprname == '==' and lexpr.is_bool():
                if rvar.is_bool():
                    # this is a reification
                    (lhs, lcons) = normalized_boolexpr(lexpr)
                else:
                    # integer comparison
                    (lhs, lcons) = get_or_make_var(lexpr, expr_dict)
            else:
                (lhs, lcons) = normalized_numexpr(lexpr, expr_dict)
            if lhs in expr_dict:
                if str(expr_dict[lhs]) != str(rvar):
                    lhs = expr_dict[lhs]
            elif lhs not in expr_dict and not isinstance(lhs, int) and exprname == "==":
                expr_dict[lhs] = rvar
                
            if not isinstance(lhs, int):
                newlist.append(Comparison(exprname, lhs, rvar))
            else:
                newlist.append(Comparison(exprname, rvar, lhs))
            newlist.extend(lcons)
            newlist.extend(rcons)

        else:
            # any other case, pass as is
            newlist.append(expr)

    return newlist


def __is_flat_var(arg):
    """ True if the variable is a numeric constant, or a _NumVarImpl (incl subclasses)
    """
    return is_num(arg) or isinstance(arg, _NumVarImpl)

def get_or_make_var(expr, expr_dict=None):
    """
        Must return a variable, and list of flat normal constraints
        Determines whether this is a Boolean or Integer variable and returns
        the equivalent of: (var, normalize(expr) == var)
    """
    if __is_flat_var(expr):
        return (expr, [])

    if is_any_list(expr):
        raise Exception(f"Expected single variable, not a list for: {expr}")
    
    if expr_dict is None:
        expr_dict = dict()
    if expr in expr_dict:
        return expr_dict[expr], []

    if expr.is_bool():
        # normalize expr into a boolexpr LHS, reify LHS == bvar
        (flatexpr, flatcons) = normalized_boolexpr(expr)

        if isinstance(flatexpr,_BoolVarImpl):
            #avoids unnecessary bv == bv or bv == ~bv assignments
            return flatexpr,flatcons
        bvar = _BoolVarImpl()
        if flatexpr in expr_dict:
            return expr_dict[flatexpr], []
        else:
            expr_dict[flatexpr] = bvar
        return (bvar, [flatexpr == bvar]+flatcons)

    else:
        # normalize expr into a numexpr LHS,
        # then compute bounds and return (newintvar, LHS == newintvar)
        (flatexpr, flatcons) = normalized_numexpr(expr, expr_dict)

        lb, ub = flatexpr.get_bounds()
        ivar = _IntVarImpl(lb, ub)
        if flatexpr in expr_dict:
            return expr_dict[flatexpr], []
        else:
            expr_dict[flatexpr] = ivar
        return (ivar, [flatexpr == ivar]+flatcons)
    
def normalized_numexpr(expr, expr_dict=None):
    """
        all 'flat normal form' numeric expressions...

        Currently, this is the case for:

        - Operator (non-Boolean) with all args Var/constant (examples: +,*,/,mod,wsum)
                                                           (CPMpy class 'Operator', not is_bool())
        - Global constraint (non-Boolean) (examples: Max,Min,Element)
                                                           (CPMpy class 'GlobalConstraint', not is_bool()))

        output: (base_expr, base_cons) with:
            base_expr: same as 'expr', but all arguments are variables
            base_cons: list of flat normal constraints
    """
    if __is_flat_var(expr):
        return (expr, [])
    
    if expr_dict is None:
        expr_dict = dict()

    elif expr.is_bool():
        # unusual case, but its truth-value is a valid numexpr
        # so reify and return the boolvar
        return get_or_make_var(expr, expr_dict)

    elif isinstance(expr, Operator):
        # rewrite -a, const*a and a*const into a weighted sum, so it can be used as objective
        if expr.name == '-' or (expr.name == 'mul' and _wsum_should(expr)):
            return normalized_numexpr(Operator("wsum", _wsum_make(expr)), expr_dict)

        if all(__is_flat_var(arg) for arg in expr.args):
            return expr, []
            
        # pre-process sum, to fold in nested subtractions and const*Exprs, e.g. x - y + 2*(z+r)
        if expr.name == "sum" and \
           all(isinstance(a, Expression) for a in expr.args) and \
           any((a.name == "-" or _wsum_should(a)) for a in expr.args):
            we = [_wsum_make(a) for a in expr.args]
            w = [wi for w,_ in we for wi in w]
            e = [ei for _,e in we for ei in e]
            return normalized_numexpr(Operator("wsum", (w,e)), expr_dict)

        # wsum needs special handling because expr.args is a tuple of which only 2nd one has exprs
        if expr.name == 'wsum':
            weights, sub_exprs  = expr.args
            # while here, avoid creation of auxiliary variables for compatible operators -/sum/wsum
            i = 0
            while(i < len(sub_exprs)): # can dynamically change
                if isinstance(sub_exprs[i], Operator) and \
                    ((sub_exprs[i].name in ['-', 'sum'] and \
                        all(isinstance(a, Expression) for a in sub_exprs[i].args)) or \
                     (sub_exprs[i].name == 'wsum' and \
                        all(isinstance(a, Expression) for a in sub_exprs[i].args[1]))):  # TODO: avoid constants for now...
                    w,e = _wsum_make(sub_exprs[i])
                    # insert in place, and next iteration over same 'i' again
                    weights[i:i+1] = [weights[i]*wj for wj in w]
                    sub_exprs[i:i+1] = e
                else:
                    i = i+1

            # now flatten the resulting subexprs
            flatvars, flatcons = map(list, zip(*[get_or_make_var(arg, expr_dict) for arg in sub_exprs])) # also bool, reified...
            newexpr = Operator(expr.name, (weights, flatvars))
            return (newexpr, [c for con in flatcons for c in con])

        else: # generic operator
            # recursively flatten all children
            flatvars, flatcons = zip(*[get_or_make_var(arg, expr_dict) for arg in expr.args])

            newexpr = Operator(expr.name, flatvars)
            return (newexpr, [c for con in flatcons for c in con])
    else:
        # Globalfunction (examples: Max,Min,Element)

        # just recursively flatten args, which can be lists
        if all(__is_flat_var_or_list(arg) for arg in expr.args):
            return (expr, [])
        else:
            # recursively flatten all children
            flatvars, flatcons = zip(*[get_or_make_var_or_list(arg, expr_dict) for arg in expr.args])

            # take copy, replace args
            newexpr = copy.copy(expr) # shallow or deep? currently shallow
            newexpr.args = flatvars
            return (newexpr, [c for con in flatcons for c in con])

def __is_flat_var_or_list(arg):
    """ True if the variable is a numeric constant, or a _NumVarImpl (incl subclasses)
        or a list of __is_flat_var_or_list
    """
    return is_num(arg) or isinstance(arg, _NumVarImpl) or \
           is_any_list(arg) and all(__is_flat_var_or_list(el) for el in arg)