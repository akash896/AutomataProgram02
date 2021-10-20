from z3 import *
from math import *
import copy
from prettytable import PrettyTable

binary = []  # contains the binary combinations for transitions in each state
left_variables_array = []
coefficients = []
values = []
map = {}
n = 0
RHS = 0
exp
coefficient_table = []
value_map = {}
coef_variable_map_table = []


def get_automata_table(exp, n):
    global binary, coefficients
    coefficients = []
    left_variables = []
    table = []
    binary = []
    #print("n = ", n)
    print("expression = ", str(exp))
    # generating the binary combinations
    for i in range(2 ** n):
        binary.append(padded_bin(i, n)[2:])

    # creating heading of the table
    row = []
    row.append("State")
    for bits in binary:
        row.append(str(bits))
    table.append(row)
    LHS = exp.arg(0)  # contains LHS of expression
    RHS = exp.arg(1)  # contains RHS of expression

    # getting 3*x1, 2*x2 in list left_variables
    childs = exp.children()
    for i in range(n - 1):
        childs = childs[0].children()
        left_variables.insert(0, childs[1])
    left_variables.insert(0, childs[0])

    # extracting coefficients of the variables
    for variables in left_variables:
        if variables.decl().name() == '*':
            coef = int(str(variables.arg(0)))
            coefficients.append(int(str(coef)))
        else:
            coefficients.append(int(1))
    coefficient_table.append(coefficients)

    if exp.decl().name() == "<=":
        table = create_table(RHS, table, "<=", n)
    if exp.decl().name() == "=":
        table = create_table(RHS, table, "=", n)
    return table


def create_table(RHS, table, operator, n):
    print("in create table ", RHS)
    global map
    map = {}
    map[int(str(RHS))] = 1
    map_copy  = {}
    while True:
        flag = -1
        for key in map:
            if key in map_copy:
                continue
            else:
                map_copy[key] = 1
        #print("map_copy = ", map_copy)
        for state in map_copy:
            if map_copy[state] == 1:
                map_copy[state] = 0
                if operator == "=":
                    table = update_table_equals_equals(state, table, n, RHS)
                if operator == "<=":
                    table = update_table_less_than_equals(state, table, n, RHS)
                flag = 1
        if flag == -1:
            break
    return table


def update_table_equals_equals(state, table, n, RHS):
    row = []
    if state == -100:  # for error state
        row.append(str(-100))
        for terminals in binary:
            row.append(str(-100))
        table.append(row)
        map[-100] = 0
        return table

    if state == 0:  # for final state
        row.append(str(state) + "F")
    else:
        if state == int(str(RHS)):  # for Initial state
            row.append(str(state) + "I")
        else:
            row.append(str(state))
    for terminals in binary:
        sum = 0
        for j in range(n):
            sum = sum + (int(terminals[j]) * coefficients[j])
        new_state = state - sum
        if new_state % 2 != 0:
            new_state = -100
        else:
            new_state = new_state // 2
        row.append(str(new_state))
        if not (new_state in map):
            map[new_state] = 1
    table.append(row)
    return table


def update_table_less_than_equals(state, table, n, RHS):
    row = []
    global map
    if int(str(RHS)) >= state >= 0:
        if state == RHS:
            row.append(str(state) + "IF")
        else:
            row.append(str(state) + "F")
    else:
        row.append(str(state))
    for terminals in binary:
        sum = 0
        for j in range(n):
            sum = sum + (int(terminals[j]) * coefficients[j])
        new_state = state - sum
        new_state = math.floor(new_state / 2)
        row.append(str(new_state))
        if not (new_state in map):
            map[new_state] = 1
    print("new_map = ", map)
    table.append(row)
    return table


def parse_not(exp, n):
    print("Inside Not")
    #print(exp.children())
    exp1 = exp.arg(0)  # getting the expression without Not keyword
    n = len(get_variable_coef_map(exp1))
    table = get_automata_table(exp1, n)
    print("table without Not = ")
    print_table(table)
    new_table = (create_table_for_NOT(table))
    print("Table with Not")
    print_table(new_table)


def create_table_for_NOT(table):
    new_table = []
    for row in table:
        if row[0][-1] != "F" and row!="State":
            row[0] = row[0] + "F"
        else:
            row[0] = row[0].replace("F", "")

    return table


def parse_and(exp, n):
    print("And")
    exp1 = exp.arg(0)
    exp2 = exp.arg(1)
    not_index = []
    if(exp1.decl().name() == "not"):
        not_index.append(1)
    if (exp2.decl().name() == "not"):
        not_index.append(2)
    if len(not_index) == 0:

        RHS1 = int(str(exp1.arg(1)))
        RHS2 = int(str(exp2.arg(1)))
        exp1_variable_index = get_variable_coef_map(exp1)
        #print("exp1 variables are ", exp1_variable_index)
        exp2_variable_index = get_variable_coef_map(exp2)
        #print("exp2 variables are ", exp2_variable_index)
        n1 = len(coef_variable_map_table[0])
        n2 = len(coef_variable_map_table[1])
        table1 = get_automata_table(exp1, n1)
        print_table(table1)
        table2 = get_automata_table(exp2, n2)
        print(table2)
        print_table(table2)
        res_exp1 = get_result(exp1, exp1_variable_index, 0, RHS1)
        print("result exp1 = ", res_exp1)
        res_exp2 = get_result(exp2, exp1_variable_index, 1, RHS2)
        print("result exp2 = ", res_exp2)
        final_res = res_exp1 and res_exp2
        print("final result of And = ", final_res)
        resultant_and_table = combine_and_table(table1, table2)
        #print_table(resultant_and_table)


def combine_and_table(table1, table2):
    print("inside combine and table")
    final_table = []
    if len(table1[0]) > len(table2[0]): # heading of table done
        final_table.append(table1[0])
    else:
        final_table.append(table2[0])

    initial_state = []
    state = table1[1][0]
    initial_state.append(state[0:state.find("I")])
    state = table2[1][0]
    initial_state.append(state[0:state.find("I")])
    print("Initial state = ", initial_state)


# ////////////////////////////////////////////////////////////////////  basic functions starts ///////////////////////////////////////////////////////////////////////////

def get_variable_coef_map(exp):  # return which variables are associated with the expression
    global coef_variable_map_table
    left_exp = str(exp.arg(0))
    coef_variable_map = {}
    #print(exp)
    var = left_exp.split("+")
    index = []
    #print("var = ", var)
    for variable in var:
        num_start = 1
        start = variable.find("x")
        #print("start = ", start)
        num_start_string = variable[0:start].strip()
        if len(num_start_string) == 0 or num_start_string == "" or num_start_string == " ":
            num_start = 1
        else:
            #print("string = ", num_start_string)
            num_start = int(num_start_string)
        num_end = int(variable[start+1:])
        index.append(num_end)
        coef_variable_map[num_end] = num_start

    #print("coef map = ", coef_variable_map)
    coef_variable_map_table.append(coef_variable_map)
    return index

def print_table(table):
    # print("left_variables are :", left_variables)
    # print("Coefficients are : ", coefficients)
    i = 0
    for rows in table:
        if i == 0:
            pretty_table = PrettyTable(rows)
            i = 1
        else:
            pretty_table.add_row(rows)
        # print(rows)
    print(pretty_table)


def get_result(exp, variable_index, coef_num,
               RHS):  # function to return if expression is satisfied for the given values
    global coef_variable_map_table, value_map

    #print(coef_variable_map_table)
    coef_map = coef_variable_map_table[coef_num]
    print("coef map = ", coef_map)
    res = 0
    print("value map => ", value_map)
    #print("coef of exp ", coef_num, " = ", coefficient_table[coef_num])
    for i in coef_map:
        print("val = ", value_map[i], " , coef = ", coef_map[i])
        res = res + coef_map[i] * value_map[i]
        #print("res = ", res)
    if exp.decl().name() == "=":
        if res == RHS and exp.decl().name() == "=":
            return True
    if exp.decl().name() == "<=":
        print("RHS ---", res)
        if res <= int(str(RHS)):
            return True

    return False

def padded_bin(i, width):
    s = bin(i)
    return s[:2] + s[2:].zfill(width)








def main():
    global exp, n, values, value_map
    print("Inside main")

    # ///////////////////////////////  user input starts ////////////////////////////////////////////////////////////
    n = 2  # input value of n
    X = [Int('x%s' % i) for i in range(n + 1)]
    exp = And(X[1] + X[2] <= 5, X[2] <= 2)  # input expression where write x1 = X[1] , x2 = X[2] , . . . . .
    #exp = Not(X[1] + X[2] <= 2)
    values = [3, -1]  # enter the values of the variables here

    # //////////////////////////////  user input ends /////////////////////////////////////////////////////////////////
    for i in range(1,n+1):
        value_map[i] = values[i-1]

    if exp.decl().name() == "and":
        table = parse_and(exp, n)
    else:
        if exp.decl().name() == "not":
            table = parse_not(exp, n)
            var_index = []
            for i in range(n):
                var_index.append(i)
                exp_without_not = exp.arg(0)
            not_result = get_result(exp_without_not, var_index, 0, int(str(exp_without_not.arg(1))))
            print("resut of exp without Not = ", not_result)
            not_result = not(not_result)
            print(print("result of exp = ", str(exp), ", with Not applied is = ", not_result))
        else:
            table = get_automata_table(exp, n)
            get_variable_coef_map(exp)
            print_table(table)
            var_index = []
            for i in range(n):
                var_index.append(i)
            result = get_result(exp, var_index, 0, int(str(
                exp.arg(1))))  # function which return True or False value of he expression with the input values
            print("result of exp = ", str(exp), ", is = ", result)


if __name__ == "__main__":
    main()