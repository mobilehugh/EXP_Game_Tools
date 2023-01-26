import math

"""
Proficiencies = {
"Nomad": {{"A":[1, 3, 6, 9, 12]}, {"B":[3, 4, 7, 10, 12]},{"C":[1, 5, 8, 11, 14]}},
"Spie": {{"A":[1, 2, 4, 6, 8]}, {"B":[1, 2, 4, 6, 8]},{"C":[1, 2, 4, 6, 8]}},
"Veterinarian": {{"A":[1, 3, 6, 9, 12]}, {"B":[	1, 5, 8, 11, 14]},{"C":[1, 4, 7, 10, 13]}}
}"""


table = {"A": [1, 3, 6, 9, 12], "B": [1, 5, 8, 11, 14], "C": [1, 4, 7, 10, 13]}

level = int(input("persona level? "))
# level = object.Level
proficients = ""
for key in table:
    prof_number = 0
    proficients = proficients + "Type " + key + " = "
    lvl_list = table[key]

    for lvl in range(0, len(lvl_list)):
        if level >= lvl_list[lvl]:
            prof_number += 1
        # print(str(lvl_list[lvl]) + " ", end='')
    proficients = proficients + str(prof_number) + " "

print(proficients)

print(math.ceil(level / 3))
