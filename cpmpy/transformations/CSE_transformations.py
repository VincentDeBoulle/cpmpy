
from cpmpy.expressions.core import Comparison



def apply_CSE(cpm_cons):
    expr_dict = dict()

    newlist = []

    for expr in cpm_cons:
        if isinstance(expr, Comparison):
            print("expr: ", expr)
            lhs, rhs = expr.args
            exprname = expr.name

            if lhs in expr_dict:
                lhs = expr_dict[lhs]
            else:
                expr_dict[lhs] = rhs
        
            if isinstance(lhs, int):
                newlist.append(Comparison(exprname , rhs, lhs))
            else:
                newlist.append(Comparison(exprname, lhs, rhs))
        else:
            newlist.append(expr)


    return newlist