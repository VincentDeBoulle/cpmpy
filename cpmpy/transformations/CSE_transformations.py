import copy
from cpmpy.expressions.utils import is_any_list, is_num
from cpmpy.expressions.variables import _NumVarImpl, NegBoolView
from ..expressions.core import Comparison, Operator

def remove_redundant(cpm_cons):
    """
    Removes redundant constraints:
        - 'True'
        - LHS == RHS
        - 2x the same constraint
    """
    constraints = [i for i in list(set(cpm_cons)) if type(i) != bool or (type(i) == bool and i != True)]
    single_cons = []

    for cpm_expr in constraints:
        if isinstance(cpm_expr, Comparison):
            lhs, rhs = cpm_expr.args
            if (type(lhs) == type(rhs)) and (str(lhs) == str(rhs)):
                continue
        single_cons.append(cpm_expr)
    return list(set(single_cons))

def applydemorgan(cpm_expr):
    new_expr_list = []
    for expr in cpm_expr:
        if isinstance(expr, Operator) and all(__is_flat_var_or_list(arg) for arg in expr.args):
            if expr.name in {"or", "and"} and all(type(arg) == NegBoolView for arg in expr.args):
                newexpr = copy.copy(expr)
                newexpr.name = "or" if expr.name == "and" else "and"
                newexpr.args = [~a for a in expr.args]
                newexpr = ~newexpr
                new_expr_list.append(newexpr)
            else:
                new_expr_list.append(expr)
        else:
            new_expr_list.append(expr)
    return new_expr_list

def __is_flat_var_or_list(arg):
    """ True if the variable is a numeric constant, or a _NumVarImpl (incl subclasses)
        or a list of __is_flat_var_or_list
    """
    return is_num(arg) or isinstance(arg, _NumVarImpl) or \
           is_any_list(arg) and all(__is_flat_var_or_list(el) for el in arg)