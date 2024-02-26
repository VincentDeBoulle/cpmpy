import functools
import numpy as np
from cpmpy.expressions.core import Comparison, Operator
from cpmpy.expressions.globalconstraints import GlobalConstraint, alldifferent
from cpmpy.expressions.globalfunctions import Abs
from cpmpy.expressions.utils import eval_comparison
from cpmpy.expressions.variables import _BoolVarImpl, _NumVarImpl


def order_constraint(lst_of_expr):
    """
    This function takes a list of constraints and orders them internally alphabetically.
    For example: [B + A + C == D; (B + A)**2] --> [A + B + C == D; (A + B)**2]
    """

    newlist = []
    
    for cpm_expr in lst_of_expr:

        if isinstance(cpm_expr, Comparison):
            lhs, rhs = cpm_expr.args

            if cpm_expr.name in {"==", "!="}:
                lhs = order_constraint(lhs) if isinstance(lhs, Comparison) else lhs
                rhs = order_constraint(rhs) if isinstance(rhs, Comparison) else rhs

            if isinstance(lhs, Operator):
                lhs = create_sorted_expression(lhs.name, lhs.args)
            if isinstance(rhs, Operator):
                rhs = create_sorted_expression(rhs.name, rhs.args)
            if isinstance(lhs, Abs):
                lhs = abs(order_expression_arg(lhs.args[0]))
            if isinstance(rhs, Abs):
                rhs = abs(order_expression_arg(rhs.args[0]))

            newlist.append(eval_comparison(cpm_expr.name, lhs, rhs))

        elif isinstance(cpm_expr, Operator):
            if cpm_expr.name in {"or", "and"}:
                ordered_expr = sorted([order_constraint([expr])[0] for expr in cpm_expr.args], key=str)
                combined_expr = functools.reduce(lambda x, y: x | y if cpm_expr.name == "or" else x & y, ordered_expr)
                newlist.append(combined_expr)
            elif cpm_expr.name in {"pow", "->", "mod", "not"}:
                newlist.append(Operator(cpm_expr.name, order_constraint(cpm_expr.args)))
            else:
                newlist.append(cpm_expr)

        elif isinstance(cpm_expr, GlobalConstraint) and cpm_expr.name == "alldifferent":
            newlist.append(alldifferent(sorted(cpm_expr.args, key=str)))

        else: # rest of expressions
            newlist.append(cpm_expr)

    return newlist


def create_sorted_expression(op, args):
    """
    Orders an expression alphabetically
    """
    if op == "-":
        if isinstance(args[0], (_NumVarImpl)):
            return Operator(op, args)
        return Operator(op, [create_sorted_expression(args[0].name, args[0].args)])
    elif op == "sum":
        new_args = sorted([order_expression_arg(arg) if not isinstance(arg, (_BoolVarImpl, _NumVarImpl, np.int64, Comparison)) else arg for arg in args], key= str)
        return Operator(op, new_args)
    elif op == "pow":
        return Operator(op, [order_expression_arg(args[0]), args[1]])
    elif op == "mul":
        return order_expression_arg(args[0] * args[1])
    elif op == "div":
        return order_expression_arg(args[0]) // order_expression_arg(args[1])
    elif op == "mod":
        return order_expression_arg(args[0]) % order_expression_arg(args[1])
    elif op == "wsum":
        new_args = [order_expression_arg(arg) if not isinstance(arg, (_BoolVarImpl, _NumVarImpl)) else arg for arg in args[1]]
        str_var = [str(s) + str(e) for s, e in zip(args[0], new_args)]
        mapping = {s: [args[0][i], new_args[i]] for i, s in enumerate(str_var)}
        str_var = sorted(str_var)
        args = [mapping[s][1] for s in str_var]
        new_weights = [mapping[s][0] for s in str_var]
        new_args = [new_weights, args]
        return Operator(op, new_args)
    return Operator(op, args)

def order_expression_arg(expr):
    """
    Orders an expressions arguments alphabetically
    """
    if isinstance(expr, (_BoolVarImpl, _NumVarImpl, int, float)):
            return expr
    if expr.name == "-":
        if isinstance(expr.args[0], (_BoolVarImpl, _NumVarImpl)):
            return expr
        else:
            ord_expr = order_expression_arg(expr.args[0])
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