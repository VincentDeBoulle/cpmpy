from ..expressions.core import Comparison

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