__author__ = 'gloryofrobots'


class PMCondition:
    def __init__(self, condition, children=None):
        pass


class PMAction:
    def __init__(self, action, children=None):
        pass



"""
match (a,b):
    case (1, false): 1 + 1 end
    case (2, false): 1 + 1 end
    case false : 2 end
    case _: nil end
end
"""
"""
$c0 =
if is_seq($):
    if length($) == 2:
        if $[0] == 1:
            if $[1] == false:
                method1
        if $[0] == 2:
            if $[1] == false:
                method2
elif $ is false:
    2
else true:
    nil

"""

"""
match (a,b):
    case (1, false): 1 + 1 end
    case (1, true): 1 + 1 end
    case (2, b): 1 + 1 end
    case (a, _): 1 + 1 end
    case (a, b): 1 + 1 end

    case (1, true, {name="Bob", age=(a,45)}): 1 + 1 end
    case false : 2 end
    case _: nil end
    case A : 2 end
end
"""
"""
function_call
if_condition
elif_condition
equals
[[TT_IF, TT_NAME]]

if is_seq($):
    if length($) == 2:
        if $[0] == 1:
            if $[1] == false:
                method1
elif is_seq($):
    if length($) == 2:
        if $[0] == 1:
            if $[1] == true:
                method2
elif is_seq($):
    if length($) == 2:
        if $[0] == 2:
            if true:
                b = $[1]
                method3
elif is_seq($):
    if length($) == 2:
        a = $[0]
        _ = $[1]
        method5
        //ERROR HERE
elif is_seq($):
    if length($) == 2:
        a = $[0]
        b = $[1]
        method4


case (1, true, {name="Bob", age=(a,45)}): 1 + 1 end
elif is_seq($):
    if length($) == 3:
        if $[0] == 1:
            if $[1] == true:
                if is_map($[2]):
                    if "name" in $[2]:
                        if $[2]["name"] == "Bob":
                            if age in $[2]:
                                if is_seq($[2][age]):
                                    if $[2][age][1] == 45:
                                        name = $[2]["name"]
                                        a = $[2][age][0]
                                        method5




"""
"""
if is_seq($):
    if length($) == 2:
        if $[0] == 1:
            if $[0] == false:
                method1
            elif $[0] == true:
                method2
        elif $[0] == 2:
            b = $[1]
            method3
        else:
            a = $[0]
            _ = $[1]
            method4
            method5
            //ERROR HERE
    elif length($) == 3:
        if $[0] == 1:
            if $[2] is true:
                if is_map($[3]):
                    if "name" in $[3]
                        if  $[3]["name"] == "Bob":
                            if "age" in $[3]:
                                if is_seq($[3]["age"]):
                                    if $[3]["age"][1] == 45:
                                        method 6
                                        name = $[3]["name"]
                                        a = $[3]["age"][0]
elif $ is false:
    method 7
elif true:
    method 8
    method 9
    //ERROR
"""


_ = \
["push", "dup", "is_seq,", "store $1", "load $1", ["test 1 ,2",
    ["1:", "push [0]", "dup", "push 1", "equals", "store $2", "load $2", ["test, 3, 4",
        ["3:", "push [1]", "dup", "push false", "strict equal", "store $3", "load $3", ["test", "method 1, 4"]],
        ["4:", "push 2", "equals", "store $4", "load $4", ["test 5, 2",
             ["5:", "load $3", "equals", ["test method 2, 2"]]]]]],

   ["2:", "dup", "push false", "equals", "store $5", "load 5", ["test method 3, 3"],
   ["3:", "dup", "store _", "method 4"]]]]
