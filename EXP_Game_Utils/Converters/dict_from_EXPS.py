import re

table = """TTable 5.26 Robotic Experience
Experience points required to achieve levels for the robot.

0-2000	1
2001-4000	2
4001-8000	3
8001-18000	4
18001-35000	5
35001-70000	6
70001-125000	7
125001-250000	8
250001-500000	9
500001-800000	10"""
# 310000 point	per level above 10th

# collect read only data from book
top_amount = input("Top Amount ")
top_level = input("Top Level ")
rate = input("Rate ")

# give the dictionary it's name and print out
pattern = re.compile(
    r"Table\s(\d+.\d+)\s(\w+\s\w+\s*\w*)"
)
matches = pattern.finditer(table)
nomatch = True
for match in matches:
    nomatch = False
    number, title = match.group(1, 2)
    name = title.replace(" ", "")
    print(name + " = {")

if nomatch:
    print("header title no match")

# give the dictionary it's ranges and print
pattern = re.compile(
    r"(\d+)-(\d+)[\s ]*(\d+)")

matches = pattern.finditer(table)
nomatch = True

for match in matches:
    nomatch = False
    lower, upper, lvl = match.group(1, 2, 3)

    # bump up upper
    upper = int(upper) + 1

    # build the range line
    print(f'range({lower}, {upper}): {lvl},')
    # print(match)
if nomatch:
    print("table content matches not found")

# give the dict it's deets and then print out

print(f"\"name\": \"{title}\",")
print(f"\"number\": {number},")
print(f"\"top_amount\": {top_amount},")
print(f"\"top_level\": {top_level},")
print(f"\"rate\": {rate}}}")