import re

table = """Table 5.A Android
The anthro appearing robot type of all low budget robot movies.
Attribute Levels:	CON 4; DEX 4; INT 4; PSTR 4
Attributes	Special
Attacks:	Special
Defences:	Special
Hit Points (HPS):	Special
Random:	Special
Adaptability:	1%
Value:	100000000
Size:	Special"""


# give the dictionary it's name, title and dice
pattern = re.compile(
    r"Table\s(\d+\.\d+)\s*(\w+\s*\w*)[\nA-Za-z? ,.?'\n]*\((\d+)d(\d+)")
matches = pattern.finditer(table)
nomatch = True
for match in matches:
    nomatch = False
    number, name, die_amount, die_type = match.group(1, 2, 3, 4)
    title = match.group(2)
    name = name.replace(" ", "")
    print(name + " = {")

if nomatch:
    print("dict title no match")

# give the dictionary it's ranges and print 
pattern = re.compile(
    r"^(\d+)\-?(\d*)\s*(\w+ *\w* *\w*)", flags=re.MULTILINE
)

matches = pattern.finditer(table)
nomatch = True

for match in matches:
    nomatch = False
    lower, upper, result = match.group(1, 2, 3)
    table_top = die_type

    if lower == "00":
        lower = die_type

    if lower[0] == "0":
        lower = lower[1]

    if not upper:
        upper = lower

    if title == "Ref's Own Table":
        upper = table_top
 
    upper = upper.replace("-", "")
    upper = str(int(upper)+1)

    # build the range line
    print(f'range({lower}, {upper}): "{result}",')
    # print(match)
if nomatch:
    print("no matches found")

# give the dict it's deets and then print out


print(f'"name": "{title}",')
print(f'"number": "{number}",')
print(f'"die_roll": "{die_amount}d{die_type}"}}')
    
if nomatch:
    print("header no matches found")

