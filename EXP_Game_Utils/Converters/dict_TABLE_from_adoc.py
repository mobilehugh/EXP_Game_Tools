import re
import math

adoc_string = """
//a new table for 6.0
.*Heavy Combot Heavy Weapon*
[width="75%",cols="2*<"]
|===
2+<|Add PSTR to the 1d100 roll.

s|Die Roll (1d100)
s|Heavy Weapon

|01-27
|Popcorn Machine

|28-60
|Bomb only

|61-90
|Bomb/Missile

|91-110
|1 Artillery

|111-120
|1 Artillery +
1 Bomb only

|121-128
|1 Artillery +
1 Missile/Bomb

|>129
|Naval Artillery

s|Die Roll
s|Heavy Weapon
2+<| A popcorn machine makes a yummy snack from seeds. 
|===



"""

table_dict = {}

pattern = re.compile(r"(\.\*)([A-Za-z ]+)")
matches = pattern.finditer(adoc_string)

# find table title and open dictionary
if matches == None:
    print("No TITLE matches found.")
else:
    for match in matches:
        table_title = match.group(2)

print(table_title.replace(' ','_').lower() + " = {")

    
# build ranges and table results
pattern = re.compile(r"(\|)(\d\d)(-)?(\d\d)?\n(\|)([A-Za-z0-9' -]+)")
matches = pattern.finditer(adoc_string)

if matches == None:
    print("No NUMBER matches found.")
else:
    for match in matches:
        lower_bound = match.group(2)
        upper_bound = match.group(4)
        table_result = match.group(6)

        if lower_bound == "00":
            lower_bound = "100"
        if upper_bound == "00":
            upper_bound = "101"
        
        if upper_bound == None:
            upper_bound = str((int(lower_bound) + 1))
        else:
            upper_bound = str(int(upper_bound)+1)
        print(f'    range({int(lower_bound)}, {int(upper_bound)}): \"{table_result}\",')

# build die roll and close dictionary
pattern = re.compile(r"(Die Roll \()(\d+d\d+)")
matches = pattern.search(adoc_string)

if matches == None:
    print("No NUMBER matches found.")
else:
    print(f'    "die_roll":"{matches.group(2)}"')
    print("}")



