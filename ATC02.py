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
and_states = []
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
    #print("new_map = ", map)
    table.append(row)
    return table


def parse_not(exp, n):
    print("Inside Not with exp = ", exp)
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
    ch = 0
    exp1 = exp.arg(0)
    exp2 = exp.arg(1)
    not_index = []
    if(exp1.decl().name() == "not"):
        ch = ch - 1
    if (exp2.decl().name() == "not"):
        ch = ch + 2
    if ch == 0:
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
        #print(table2)
        print_table(table2)
        res_exp1 = get_result(exp1, exp1_variable_index, 0, RHS1)
        print("result exp1 = ", res_exp1)
        res_exp2 = get_result(exp2, exp1_variable_index, 1, RHS2)
        print("result exp2 = ", res_exp2)
        final_res = res_exp1 and res_exp2
        print("final result of And = ", final_res)
        #resultant_and_table = combine_and_table(table1, table2, coef_variable_map_table[0].keys(), coef_variable_map_table[1].keys())
        #print_table(resultant_and_table)
        #print(resultant_and_table)

    if ch == -1:
        exp_with_not = exp.arg(0)
        table = parse_not(exp.arg(0), n)
        var_index = []
        for i in range(n):
            var_index.append(i)
            exp_without_not = exp_with_not.arg(0)
        not_result = get_result(exp_without_not, var_index, 0, int(str(exp_without_not.arg(1))))
        #print("resut of exp without Not = ", not_result)
        not_result = not (not_result)
        res_exp1 = not_result
        #print(print("result of exp = ", str(exp.arg(0)), ", with Not applied is = ", not_result))

        RHS2 = int(str(exp2.arg(1)))
        n2 = len(coef_variable_map_table[1])
        table2 = get_automata_table(exp2, n2)
        # print(table2)
        print_table(table2)
        res_exp2 = get_result(exp2, exp1_variable_index, 1, RHS2)
        print("result exp2 = ", res_exp2)
        final_res = res_exp1 and res_exp2
        print("final result of And = ", final_res)

    if ch == 2:
        exp_with_not = exp.arg(1)
        table = parse_not(exp.arg(1), n)
        var_index = []
        for i in range(n):
            var_index.append(i)
            exp_without_not = exp_with_not.arg(0)
        not_result = get_result(exp_without_not, var_index, 0, int(str(exp_without_not.arg(1))))
        # print("resut of exp without Not = ", not_result)
        not_result = not (not_result)
        res_exp2 = not_result
        print(print("result of exp = ", str(exp.arg(0)), ", with Not applied is = ", not_result))

        RHS1 = int(str(exp1.arg(1)))
        exp1_variable_index = get_variable_coef_map(exp1)
        n1 = len(coef_variable_map_table[0])
        table1 = get_automata_table(exp1, n1)
        print_table(table1)
        res_exp1 = get_result(exp1, exp1_variable_index, 1, RHS1)
        print("result exp1 = ", res_exp1)
        final_res = res_exp1 and res_exp2
        print("final result of And = ", final_res)

    if ch == 1:
        exp_with_not = exp.arg(0)
        table = parse_not(exp.arg(0), n)
        var_index = []
        for i in range(n):
            var_index.append(i)
            exp_without_not = exp_with_not.arg(0)
        not_result = get_result(exp_without_not, var_index, 0, int(str(exp_without_not.arg(1))))
        # print("resut of exp without Not = ", not_result)
        not_result = not (not_result)
        res_exp1 = not_result
        # print(print("result of exp = ", str(exp.arg(0)), ", with Not applied is = ", not_result))

        exp_with_not = exp.arg(1)
        table = parse_not(exp.arg(1), n)
        var_index = []
        for i in range(n):
            var_index.append(i)
            exp_without_not = exp_with_not.arg(0)
        not_result = get_result(exp_without_not, var_index, 0, int(str(exp_without_not.arg(1))))
        # print("resut of exp without Not = ", not_result)
        not_result = not (not_result)
        res_exp2 = not_result
        print(print("result of exp = ", str(exp.arg(0)), ", with Not applied is = ", not_result))
        final_res = res_exp1 and res_exp2
        print("final result of And = ", final_res)








def combine_and_table(table1, table2, index1, index2):
    print("args = ", index1, index2)
    global and_states
    and_states = []
    print("inside combine and table")
    final_table = []
    processed_states = {}
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
    exp1_bin_map, exp2_bin_map = (get_bin_comb_map(table1), get_bin_comb_map(table2))
    #print(exp1_bin_map, exp2_bin_map)
    exp1_state_map, exp2_state_map = (get_state_comb_map(table1), get_state_comb_map(table2))
    print(exp1_state_map, exp2_state_map)
    and_states.append(initial_state)
    and_states = get_list_of_string(and_states)

    while True:

        completed_flag = 1
        print("and states = ", and_states)
        for sta in and_states:

            if sta in processed_states:
                continue
            else:
                processed_states[sta] = 1
        print("processed states = ", processed_states)
        for states in processed_states:
            if processed_states[states] == 1:
                processed_states[states] = 0
                completed_flag = 0
                final_table = update_new_state_in_and(states, exp1_bin_map, exp2_bin_map, exp1_state_map, exp2_state_map, index1,index2, final_table, table1, table2 )
        if completed_flag == 1:
            break
    return final_table


def update_new_state_in_and(states, exp1_bin_map, exp2_bin_map, exp1_state_map, exp2_state_map, index1,index2, final_table, table1, table2):
    states = str(states).split(",")
    for col in final_table[0]:
        new_row = []
        new_state = []
        lookup1 = ""
        lookup2 = ""
        if col == "State":
            new_row.append(states)
            continue
        else:
            if len(index1) == len(col):
                lookup1 = col
            else:
                for i in index1:
                    lookup1 += col[i-1]
            if len(index2) == len(col):
                lookup2 = col
            else:
                for i in index2:
                    lookup2 += col[i-1]

            s1 = table1[int(states[0])][exp1_bin_map[lookup1]]
            new_state.append(s1)
            s2 = table2[int(states[1])][exp1_bin_map[lookup1]]
            new_state = s1+","+s2
            print("new states are = ", new_state)
            if not(new_state in and_states):
                and_states.append(new_state)
            new_row.append(new_state)
        final_table.append(new_row)
        return final_table

def get_list_of_string(list):
    col = ""
    string_list = []
    for item in list:
        print("item = ", item)
        col = item[0]+ "," + item[1]
        string_list.append(col)
    return string_list




def get_state_comb_map(table):
    exp_state_map = {}
    i = 1
    for row in table:
        state = row[0]
        if state == "State":
            continue
        else:
            if "I" in state or "F" in state:
                if "I" in state:
                    state_num = state[0:state.find("I")]
                    exp_state_map[state_num] = i
                    i += 1
                    continue
                else:
                    state_num = state[0:state.find("F")]
                    exp_state_map[state_num] = i
                    i += 1
            else:
                exp_state_map[state] = i
                i += 1
    return exp_state_map

def get_bin_comb_map(table): #creating binary combination map like (00, 1), (01, 2), (10, 3)...
    exp_bin_map = {}
    i=1
    for bin_comb in table[0]:
        if bin_comb == "State":
            continue
        else:
            exp_bin_map[bin_comb] = i
            i += 1
    return exp_bin_map







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
        #print("val = ", value_map[i], " , coef = ", coef_map[i])
        res = res + coef_map[i] * value_map[i]
        #print("res = ", res)
    if exp.decl().name() == "=":
        if res == RHS and exp.decl().name() == "=":
            return True
    if exp.decl().name() == "<=":
        if res <= int(str(RHS)):
            return True

    return False

def padded_bin(i, width):
    s = bin(i)
    return s[:2] + s[2:].zfill(width)

def Q1_atomic_expression():
    table = get_automata_table(exp, n)
    get_variable_coef_map(exp)
    print_table(table)
    # var_index = []
    # for i in range(n):
    #     var_index.append(i)
    # result = get_result(exp, var_index, 0, int(str(
    #     exp.arg(1))))  # function which return True or False value of he expression with the input values
    # print("result of exp = ", str(exp), ", is = ", result)

def Q5_solving_function():
    Q4_solving_function()



def Q4_solving_function():
    global exp, n, values, value_map
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

def main():
    global exp, n, values, value_map
    n = 1  # input value of n
    X = [Int('x%s' % i) for i in range(n + 1)]
    #exp = And(X[1] + X[2] <= 5, Not(X[1] + X[2] <= 2))  # input expression where write x1 = X[1] , x2 = X[2] , . . . . .
    # exp = Not(X[1] + X[2] <= 2)
    exp = X[1] <= 2
    values = [1]  # enter the values of the variables here

    #Q1 solving function
    Q1_atomic_expression()

    #q2 solving function
    # table1, table2, index1, index2 = ([], [], [], [])
    # combine_and_table(table1, table2, index1, index2)
    #index1 represent the x values which are used in table1 like if
    # table was for "x1+x2+x3  <= 5", then index1 = [1,2,3]

    # #Q3 solving function
    # table1 = []  # enter automata Table in form of list
    # create_table_for_NOT(table1)
    #
    # #Q4 solving function
    # Q4_solving_function()
    #
    # #Q5 solving
    Q5_solving_function()



if __name__ == "__main__":
    main()

