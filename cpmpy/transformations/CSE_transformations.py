from cpmpy.expressions.variables import NegBoolView
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

def horn_clauses(cpm_cons):
    new_expr_list = []

    for expr in cpm_cons:
        if isinstance(expr, Operator) and expr.name == 'or':
            pos_vars = sorted([arg for arg in expr.args if not isinstance(arg, NegBoolView)], key=str)
            
            if len(pos_vars) == 1:
                neg_vars = [~arg for arg in expr.args if isinstance(arg, NegBoolView)]
                lhs = Operator('and', neg_vars)
                new_expr = Operator('->', [lhs, pos_vars[0]])
                new_expr_list.append(new_expr)
            else:
                rhs = pos_vars[0]
                pos_vars.pop(0)
                neg_vars = [~arg for arg in expr.args if isinstance(arg, NegBoolView)] + [~arg for arg in pos_vars]
                lhs = Operator('and', neg_vars)
                new_expr = Operator('->', [lhs, rhs])
                new_expr_list.append(new_expr)
        else:
            new_expr_list.append(expr)
    return new_expr_list
    