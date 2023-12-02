"""
Transformations regarding linearization of constraints.

Linearized constraints have one of the following forms:


Linear comparison:
------------------
- LinExpr == Constant
- LinExpr >= Constant
- LinExpr <= Constant

    LinExpr can be any of:
        - NumVar
        - sum
        - wsum

Indicator constraints:
----------------------
- BoolVar -> LinExpr == Constant
- BoolVar -> LinExpr >= Constant
- BoolVar -> LinExpr <= Constant

- BoolVar -> GenExpr                    (GenExpr.name in supported, GenExpr.is_bool())
- BoolVar -> GenExpr >= Var/Constant    (GenExpr.name in supported, GenExpr.is_num())
- BoolVar -> GenExpr <= Var/Constant    (GenExpr.name in supported, GenExpr.is_num())
- BoolVar -> GenExpr == Var/Constant    (GenExpr.name in supported, GenExpr.is_num())

Where BoolVar is a boolean variable or its negation.

General comparisons or expressions
-----------------------------------
- GenExpr                               (GenExpr.name in supported, GenExpr.is_bool())
- GenExpr == Var/Constant               (GenExpr.name in supported, GenExpr.is_num())
- GenExpr <= Var/Constant               (GenExpr.name in supported, GenExpr.is_num())
- GenExpr >= Var/Constant               (GenExpr.name in supported, GenExpr.is_num())


"""
import copy
import numpy as np
from cpmpy.transformations.normalize import toplevel_list
import functools

from .flatten_model import flatten_constraint, get_or_make_var
from .get_variables import get_variables
from ..exceptions import TransformationNotImplementedError

from ..expressions.globalfunctions import Abs
from ..expressions.core import Comparison, Operator, BoolVal
from ..expressions.globalconstraints import GlobalConstraint, DirectConstraint, alldifferent
from ..expressions.utils import is_any_list, is_num, eval_comparison, is_bool

from ..expressions.variables import _BoolVarImpl, boolvar, NegBoolView, _NumVarImpl

def linearize_constraint(lst_of_expr, supported={"sum","wsum"}, reified=False, expr_dict=None):
    """
    Transforms all constraints to a linear form.
    This function assumes all constraints are in 'flat normal form' with only boolean variables on the lhs of an implication.
    Only apply after 'cpmpy.transformations.flatten_model.flatten_constraint()' 'and only_bv_implies()'.

    `AllDifferent` has a special linearization and is decomposed as such if not in `supported`.
    Any other unsupported global constraint should be decomposed using `cpmpy.transformations.decompose_global.decompose_global()`

    """

    newlist = []
    if expr_dict is None:
        expr_dict = dict()

    for cpm_expr in lst_of_expr:

        # boolvar
        if isinstance(cpm_expr, _BoolVarImpl):
            newlist.append(sum([cpm_expr]) >= 1)

        # Boolean operators
        elif isinstance(cpm_expr, Operator) and cpm_expr.is_bool():
            # conjunction
            if cpm_expr.name == "and":
                newlist.append(sum(cpm_expr.args) >= len(cpm_expr.args))

            # disjunction
            elif cpm_expr.name == "or":
                newlist.append(sum(cpm_expr.args) >= 1)

            # xor
            elif cpm_expr.name == "xor" and len(cpm_expr.args) == 2:
                newlist.append(sum(cpm_expr.args) == 1)

            # reification
            elif cpm_expr.name == "->":
                # determine direction of implication
                cond, sub_expr = cpm_expr.args
                assert isinstance(cond, _BoolVarImpl), f"Linearization of {cpm_expr} is not supported, lhs of implication must be boolvar. Apply `only_bv_implies` before calling `linearize_constraint`"

                if isinstance(cond, _BoolVarImpl) and isinstance(sub_expr, _BoolVarImpl):
                    # shortcut for BV -> BV, convert to disjunction and apply linearize on it
                    newlist.append(1 * cond + -1 * sub_expr <= 0)

                # BV -> LinExpr
                elif isinstance(cond, _BoolVarImpl):
                    lin_sub = linearize_constraint([sub_expr], supported=supported, reified=True, expr_dict=expr_dict)
                    newlist += [cond.implies(lin) for lin in lin_sub]
                    # ensure no new solutions are created
                    new_vars = set(get_variables(lin_sub)) - set(get_variables(sub_expr))
                    newlist += linearize_constraint([(~cond).implies(nv == nv.lb) for nv in new_vars], reified=reified, expr_dict=expr_dict)


        # comparisons
        elif isinstance(cpm_expr, Comparison):
            lhs, rhs = cpm_expr.args

            if lhs.name == "sub":
                # convert to wsum
                lhs = sum([1 * lhs.args[0] + -1 * lhs.args[1]])
                cpm_expr = eval_comparison(cpm_expr.name, lhs, rhs)

            # linearize unsupported operators
            elif isinstance(lhs, Operator) and lhs.name not in supported: # TODO: add mul, (abs?), (mod?), (pow?)

                if lhs.name == "mul" and is_num(lhs.args[0]):
                    lhs = Operator("wsum",[[lhs.args[0]], [lhs.args[1]]])
                    cpm_expr = eval_comparison(cpm_expr.name, lhs, rhs)
                else:
                    raise TransformationNotImplementedError(f"lhs of constraint {cpm_expr} cannot be linearized, should be any of {supported | set(['sub'])} but is {lhs}. Please report on github")

            elif isinstance(lhs, GlobalConstraint) and lhs.name not in supported:
                raise ValueError("Linearization of `lhs` not supported, run `cpmpy.transformations.decompose_global.decompose_global() first")

            [cpm_expr] = canonical_comparison([cpm_expr])  # just transforms the constraint, not introducing new ones
            lhs, rhs = cpm_expr.args

            # now fix the comparisons themselves
            if cpm_expr.name == "<":
                new_rhs, cons = get_or_make_var(rhs - 1, expr_dict=expr_dict) # if rhs is constant, will return new constant
                newlist.append(lhs <= new_rhs)
                newlist += linearize_constraint(cons, expr_dict=expr_dict)
            elif cpm_expr.name == ">":
                new_rhs, cons = get_or_make_var(rhs + 1, expr_dict=expr_dict) # if rhs is constant, will return new constant
                newlist.append(lhs >= new_rhs)
                newlist += linearize_constraint(cons, expr_dict=expr_dict)
            elif cpm_expr.name == "!=":
                # Special case: BV != BV
                if isinstance(lhs, _BoolVarImpl) and isinstance(rhs, _BoolVarImpl):
                    newlist.append(lhs + rhs == 1)

                if reified or (isinstance(lhs, (Operator, GlobalConstraint)) and lhs.name not in {"sum","wsum"}):
                    # lhs is sum/wsum and rhs is constant OR
                    # lhs is GenExpr and rhs is constant or var
                    #  ... what requires less new variables?
                    # Big M implementation
                    # M is chosen so that
                    # lhs - rhs + 1 <= M*z
                    # rhs - lhs + 1 <= M*~z
                    # holds
                    z = boolvar()
                    # Calculate bounds of M = |lhs - rhs| + 1
                    _, M1 = (lhs - rhs + 1).get_bounds()
                    _, M2 = (rhs - lhs + 1).get_bounds()
                    cons = [lhs + -M1*z <= rhs-1, lhs  + -M2*z >= rhs-M2+1]
                    newlist += linearize_constraint(flatten_constraint(cons), supported=supported, reified=reified, expr_dict=expr_dict)

                else:
                    # introduce new indicator constraints
                    z = boolvar()
                    constraints = [z.implies(lhs < rhs), (~z).implies(lhs > rhs)]
                    newlist += linearize_constraint(constraints, supported=supported, reified=reified, expr_dict=expr_dict)
            else:
                # supported comparison
                newlist.append(eval_comparison(cpm_expr.name, lhs, rhs))

        elif cpm_expr.name == "alldifferent" and cpm_expr.name in supported:
            newlist.append(cpm_expr)
        elif cpm_expr.name == "alldifferent" and cpm_expr.name not in supported:
            """
                More efficient implementations possible
                http://yetanothermathprogrammingconsultant.blogspot.com/2016/05/all-different-and-mixed-integer.html
                This method avoids bounds computation
                Introduces n^2 new boolean variables
            """
            # TODO check performance of implementation
            # Boolean variables
            lb, ub = min(arg.lb for arg in cpm_expr.args), max(arg.ub for arg in cpm_expr.args)
            # Linear decomposition of alldifferent using bipartite matching
            sigma = boolvar(shape=(len(cpm_expr.args), 1 + ub - lb))

            constraints = [sum(row) == 1 for row in sigma]  # Each var has exactly one value
            constraints += [sum(col) <= 1 for col in sigma.T]  # Each value is assigned to at most 1 variable

            for arg, row in zip(cpm_expr.args, sigma):
                constraints += [sum(np.arange(lb, ub + 1) * row) + -1*arg == 0]

            newlist += constraints

        elif isinstance(cpm_expr, (DirectConstraint, BoolVal)):
            newlist.append(cpm_expr)

        elif isinstance(cpm_expr, GlobalConstraint) and cpm_expr.name not in supported:
            raise ValueError(f"Linearization of global constraint {cpm_expr} not supported, run `cpmpy.transformations.decompose_global.decompose_global() first")

    return newlist


def only_positive_bv(lst_of_expr, expr_dict=None):
    """
        Replaces constraints containing NegBoolView with equivalent expression using only BoolVar.
        cpm_expr is expected to be linearized. Only apply after applying linearize_constraint(cpm_expr)

        Resulting expression is linear.
    """
    newlist = []
    if expr_dict is None:
        expr_dict = dict()

    for cpm_expr in lst_of_expr:

        if isinstance(cpm_expr, Comparison):
            lhs, rhs = cpm_expr.args
            new_cons = []

            if isinstance(lhs, _NumVarImpl):
                if isinstance(lhs,NegBoolView):
                    lhs, rhs = Operator("wsum",[[-1], [lhs._bv]]), 1 - rhs

            if lhs.name == "sum" and any(isinstance(a, NegBoolView) for a in lhs.args):
                lhs = Operator("wsum",[[1]*len(lhs.args), lhs.args])

            if lhs.name == "wsum":
                weights, args = lhs.args
                idxes = {i for i, a in enumerate(args) if isinstance(a, NegBoolView)}
                nw, na = zip(*[(-w,a._bv) if i in idxes else (w,a) for i, (w,a) in enumerate(zip(weights, args))])
                lhs = Operator("wsum", [nw, na]) # force making wsum, even for arity = 1
                rhs -= sum(weights[i] for i in idxes)

            if isinstance(lhs, Operator) and lhs.name not in {"sum","wsum"}:
            # other operators in comparison such as "min", "max"
                lhs = copy.copy(lhs)
                for i,arg in enumerate(list(lhs.args)):
                    if isinstance(arg, NegBoolView):
                        new_arg, cons = get_or_make_var(1 - arg, expr_dict=expr_dict)
                        lhs.args[i] = new_arg
                        new_cons += cons

            newlist.append(eval_comparison(cpm_expr.name, lhs, rhs))
            newlist += linearize_constraint(new_cons, expr_dict=expr_dict)

        # reification
        elif cpm_expr.name == "->":
            cond, subexpr = cpm_expr.args
            assert isinstance(cond, _BoolVarImpl), f"{cpm_expr} is not a supported linear expression. Apply `linearize_constraint` before calling `only_positive_bv`"
            if isinstance(cond, _BoolVarImpl): # BV -> Expr
                subexpr = only_positive_bv([subexpr], expr_dict=expr_dict)
                newlist += [cond.implies(expr) for expr in subexpr]


        elif isinstance(cpm_expr, (GlobalConstraint, BoolVal, DirectConstraint)):
            newlist.append(cpm_expr)

        else:
            raise Exception(f"{cpm_expr} is not linear or is not supported. Please report on github")

    return newlist

def canonical_comparison(lst_of_expr):

    lst_of_expr = toplevel_list(lst_of_expr)               # ensure it is a list

    newlist = []
    for cpm_expr in lst_of_expr:

        if isinstance(cpm_expr, Operator) and cpm_expr.name == '->':    # half reification of comparison
            lhs, rhs = cpm_expr.args
            if isinstance(rhs, Comparison):
                rhs = canonical_comparison(rhs)[0]
                newlist.append(lhs.implies(rhs))
            elif isinstance(lhs, Comparison):
                lhs = canonical_comparison(lhs)[0]
                newlist.append(lhs.implies(rhs))

        if isinstance(cpm_expr, Comparison):
            lhs, rhs = cpm_expr.args
            if isinstance(lhs, Comparison) and cpm_expr.name == "==":  # reification of comparison
                lhs = canonical_comparison(lhs)[0]
            elif is_num(lhs) or isinstance(lhs, _NumVarImpl) or (isinstance(lhs, Operator) and lhs.name in {"sum", "wsum"}):
                # bring all vars to lhs
                lhs2 = []
                if isinstance(rhs, _NumVarImpl):
                    lhs2, rhs = [-1 * rhs], 0
                elif isinstance(rhs, Operator) and rhs.name == "sum":
                    lhs2, rhs = [-1 * b if isinstance(b, _NumVarImpl) else 1 * b.args[0] for b in rhs.args
                                 if isinstance(b, _NumVarImpl) or isinstance(b, Operator)], \
                                 sum(b for b in rhs.args if is_num(b))
                elif isinstance(rhs, Operator) and rhs.name == "wsum":
                    lhs2, rhs = [-a * b for a, b in zip(rhs.args[0], rhs.args[1])
                                    if isinstance(b, _NumVarImpl)], \
                                    sum(-a * b for a, b in zip(rhs.args[0], rhs.args[1])
                                    if not isinstance(b, _NumVarImpl))
                if isinstance(lhs, Operator) and lhs.name == "sum":
                    lhs, rhs = sum([1 * a for a in lhs.args] + lhs2), rhs
                elif isinstance(lhs, _NumVarImpl) or (isinstance(lhs, Operator) and lhs.name == "wsum"):
                    lhs, rhs = lhs + lhs2, rhs
                else:
                    raise ValueError(
                        f"unexpected expression on lhs of expression, should be sum,wsum or intvar but got {lhs}")

                assert not is_num(lhs), "lhs cannot be an integer at this point!"

                # bring all const to rhs
                if lhs.name == "sum":
                    new_args = []
                    for i, arg in enumerate(lhs.args):
                        if is_num(arg):
                            rhs -= arg
                        else:
                            new_args.append(arg)
                    lhs = Operator("sum", new_args)

                elif lhs.name == "wsum":
                    new_weights, new_args = [], []
                    for i, (w, arg) in enumerate(zip(*lhs.args)):
                        if is_num(arg):
                            rhs -= w * arg
                        else:
                            new_weights.append(w)
                            new_args.append(arg)
                    lhs = Operator("wsum", [new_weights, new_args])

            newlist.append(eval_comparison(cpm_expr.name, lhs, rhs))
        else:   # rest of expressions
            newlist.append(cpm_expr)

    return newlist    

def order_constraint(lst_of_expr):

    newlist = []
    for cpm_expr in lst_of_expr:
        if isinstance(cpm_expr, Comparison):
            lhs, rhs = cpm_expr.args
            if cpm_expr.name == "==":
                lhs = order_constraint(lhs) if isinstance(lhs, Comparison) else lhs
                rhs = order_constraint(rhs) if isinstance(rhs, Comparison) else rhs

            if isinstance(lhs, Operator):
                lhs = create_sorted_expression(lhs.name, lhs.args)
            if isinstance(rhs, Operator):
                rhs = create_sorted_expression(rhs.name, rhs.args)
            if isinstance(lhs, Abs):
                lhs = abs(order_expressions(lhs.args[0]))
            if isinstance(rhs, Abs):
                rhs = abs(order_expressions(rhs.args[0]))

            newlist.append(eval_comparison(cpm_expr.name, lhs, rhs))

        elif isinstance(cpm_expr, Operator):
            if cpm_expr.name in {"or", "and"}:
                ordered_expr = [order_constraint([expr])[0] for expr in cpm_expr.args]
                combined_expr = functools.reduce(lambda x, y: x | y if cpm_expr.name == "or" else x & y, ordered_expr)
                newlist.append(combined_expr)
            elif cpm_expr.name in {"pow", "->", "mod", "not"}:
                newlist.append(Operator(cpm_expr.name, order_constraint(cpm_expr.args)))
            else:
                newlist.append(cpm_expr)

        elif isinstance(cpm_expr, GlobalConstraint) and cpm_expr.name == "alldifferent":
            newlist.append(alldifferent(sorted(cpm_expr.args, key=str)))
            
        else:  # rest of expressions
            newlist.append(cpm_expr)

    return newlist

def create_sorted_expression(op, args):
    if op == "-":
        return Operator(op, [create_sorted_expression(args[0].name, args[0].args)])
    elif op == "sum":
        new_args = sorted([order_expressions(arg) if not isinstance(arg, (_BoolVarImpl, _NumVarImpl, np.int64, Comparison)) else arg for arg in args], key= str)
        return Operator(op, new_args)
    elif op == "pow":
        return Operator(op, [order_expressions(args[0]), args[1]])
    elif op == "mul":
        return order_expressions(args[0] * args[1])
    elif op == "div":
        return order_expressions(args[0]) // order_expressions(args[1])
    elif op == "mod":
        return order_expressions(args[0]) % order_expressions(args[1])
    elif op == "wsum":
        new_args = [order_expressions(arg) if not isinstance(arg, (_BoolVarImpl, _NumVarImpl)) else arg for arg in args[1]]
        str_var = [str(s) + str(e) for s, e in zip(args[0], new_args)]
        mapping = {s: [args[0][i], new_args[i]] for i, s in enumerate(str_var)}
        str_var = sorted(str_var)
        args = [mapping[s][1] for s in str_var]
        new_weights = [mapping[s][0] for s in str_var]
        new_args = [new_weights, args]
        return Operator(op, new_args)
    return Operator(op, args)

def order_expressions(expr):
    """
    Orders an expression alphabetically
    """
    if isinstance(expr, (_BoolVarImpl, _NumVarImpl, int)):
            return expr
    if expr.name == "-":
        if isinstance(expr.args[0], _BoolVarImpl) or isinstance(expr.args[0], _NumVarImpl):
            return expr
        else:
            ord_expr = order_expressions(expr.args[0])
            return Operator("-", [ord_expr])
    elif expr.name == "mul":
        lst = sorted(make_mul_list(expr), key=str)
        result = lst[0]
        for element in lst[1::]:
            result *= element
        return result
    else:
        return Operator(expr.name, sorted(expr.args, key=str))


def make_mul_list(expr):
    """
    Make a list of all arguments of a multiplication.
    E.g. A * B * (C * D) * E --> [A, B, C, D, E]
    """
    if isinstance(expr, (_NumVarImpl, int)):   # Base case multiplication
        return [expr]

    args = make_mul_list(expr.args[0])

    second_arg = expr.args[1]
    if isinstance(second_arg, Operator):
        if second_arg.name == "mul":
            args.extend(make_mul_list(second_arg))
        else:
            args.extend([second_arg])
    else:
        args.extend(make_mul_list(second_arg))
    return args

def remove_redundant(cpm_cons):
    """
    Removes redundant constraints:
        - 'True'
        - left side == right side
        - 2x the same constraint
    """
    constraints =  [i for i in list(set(cpm_cons)) if type(i) != bool or (type(i) == bool and i != True)]
    single_cons = []

    for cpm_expr in constraints:
        if isinstance(cpm_expr, Comparison):
            lhs, rhs = cpm_expr.args
            if str(lhs) == str(rhs):
                continue
        single_cons.append(cpm_expr)
    return single_cons