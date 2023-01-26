import re

table = """Table 8.18 Spie Martial Arts
Martial arts are an essential spie skill and improv with EXPS level.
EXPS Level	AR Adjustment	Attack Number	Attack Damage	Attack
Sequence
EXPS Level	AR Adjustment	Attack Number	Attack Damage	Attack
Sequence
1	40	1	d4	Normal
2	80	2	d4	Normal
3	120	2	d6	1 Before, 1 Normal
4	160	3	d6	1 Before, 2 Normal
5	200	3	d8	Before, During,
Normal
6	240	4	d8	Before, During,
2 Normal
7	280	4	d10	Before, 2 During,
Normal
8	320	5	d10	Before, 2 During,
2 Normal
9	360	5	d12	2 Before, 2 During,
Normal
10	400	6	d12	2 Before, 2 During,
2 Normal"""
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
    r"(\d+)\s+(\d+)\s+(\d+)\s+(\w+)\s+([a-zA-Z 0-9, ]+)")

matches = pattern.finditer(table)
nomatch = True

for match in matches:
    nomatch = False
    lvl, ar, number, die, order = match.group(1, 2, 3, 4, 5)

    # bump up upper


    # build the range line
    print(f"{lvl}: {{\"AR\": {ar}, \"freq\": {number}, \"Damage\": \"1{die}\", \"order\": \"{order}\"}},")
    # print(match)
if nomatch:
    print("table content matches not found")

# give the dict it's deets and then print out

print(f"\"name\": \"{title}\",")
print(f"\"number\": {number},")
print(f"\"top_amount\": {top_amount},")
print(f"\"top_level\": {top_level},")
print(f"\"rate\": {rate}}}")