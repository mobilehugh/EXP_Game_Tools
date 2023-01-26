# little tester to determine percent chance of save success
# using 3d6 for attributes and 1d20 for save roll
# looking for inorganic base number for 60% chance success
# attribute 10 v base 18 = 60%
# attribute 10 v base 19 = 55%
# attribute 10 v base 24 = 29%
# attribute 10 v base 32 = 0%
# attribute 11 v base 32 = 0%
# attribute 18 v base 32 = 30%


# attribute 10 v 18 = 59%
# attribute 12 v 18 = 70%
# attribute 14 v 18 = 80%
# attribute 16 v 18 = 90%
# attribute 18 v 18 = 99%


import math, random, please

# base save is in if statement
# choose attribute vs 3d6 vs 4d4
total = saver = attributer = success = 0
ranger = 10000
for __ in range(1, ranger):
    save = please.roll_this("1d20")
    saver += save
    attribute = please.roll_this("3d6")
    # attribute = 18
    if (save + attribute) > 18:
        success += 1
    attributer += attribute
    total = total + (save + attribute)
    print(
        f"attribute {attribute} save {save} both = {attribute + save} total = {total}"
    )


print(
    f"attribute {attributer/ranger} save {saver/ranger} both = {(attributer + saver)/ranger} total = {total/ranger}"
)
print(f"success = {success/ranger}")
