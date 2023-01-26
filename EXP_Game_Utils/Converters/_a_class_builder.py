"""
who says we don't have class

"""

import os, re, sys

sys.path.insert(0, "C:\\Users\mobil\OneDrive\Documents\Persona Record\EXP_Game_Tools")
import please

os.system("cls")

source_function = """
def illusion_generation(object):

    mutation_data = {
        "type": "Illusion Generation",
        "kind": "combat",
        "CR": "+5",
        "desc": "Put illusions into the target's mind.",
        "link": "#_illusion_generation",
    }
"""

# regex out what is possible
func_name = re.search("def (.*)\(", source_function).group(1)
mutation_kind = re.search('"kind"\: "(.*)"', source_function).group(1)
combat_ratio = re.search('"CR"\: "(.*)"', source_function).group(1)
desc = re.search('"desc"\: "(.*)"', source_function).group(1)


# confirmation of healthy regex
if please.say_yes_to(f"{func_name} -- is a good  func_name?"):
    class_name = func_name.split("_")
    mutation_name = " ".join(class_name).title()
    class_name = "".join(map(lambda x: x.title(), class_name))

else:
    func_name = input("\n the right func_name ")
    class_name = func_name.split("_")
    mutation_name = " ".join(class_name).title()
    class_name = "".join(map(lambda x: x.title(), class_name))


# mental mutation or not
mutation_type = True if please.say_yes_to("Mental Mutation? ") else False


# RANGE AKA DISTANCE
range_choices = ["Special", "Persona Only", "Touch", "Same Hex", "Unique", "Calculated"]
range_comment = "RANGE of the mutation: "
mutation_distance = please.choose_this(range_choices, range_comment)

if mutation_distance == "Unique":
    mutation_distance = input("\nEnter the unique RANGE descriptor: ")

if mutation_distance == "Calculated":
    stattribute = input("\nWhat is the range ATTRIBUTE? ")
    units = input("What are the range UNITS (hexes)? ")
    divisor = float(input("What is the range DIVISOR? "))
    mutation_distance = (stattribute, units, divisor)

if isinstance(mutation_distance, str):
    mutation_distance = f'self.distance = "{mutation_distance}"'
elif isinstance(mutation_distance, tuple):
    mutation_distance = f"self.distance = {mutation_distance}"

# DURATION
duration_choices = [
    "Special",
    "Until Dead",
    "Constant",
    "Permanent",
    "Unique",
    "Calculated",
]
duration_comment = "DURATION of the mutation: "
mutation_duration = please.choose_this(duration_choices, duration_comment)

if mutation_duration == "Unique":
    mutation_duration = input("\nEnter the unique DURATION descriptor: ")

if mutation_duration == "Calculated":
    stattribute = input("\nWhat is the duration ATTRIBUTE? ")
    units = input("What are the duration UNITS (units)? ")
    divisor = float(input("What is the duration divisor? "))
    mutation_duration = (stattribute, units, divisor)

if isinstance(mutation_duration, str):
    mutation_duration = f'self.duration = "{mutation_duration}"'
elif isinstance(mutation_duration, tuple):
    mutation_duration = f"self.duration = {mutation_duration}"

# FREQUENCY
frequency_choices = [
    "Special",
    "As Needed",
    "Constant",
    "Permanent",
    "Unique",
    "Calculated",
]
frequency_comment = "FREQUENCY of the mutation: "
mutation_frequency = please.choose_this(frequency_choices, frequency_comment)

if mutation_frequency == "Unique":
    mutation_frequency = input("\nEnter the unique FREQUENCY descriptor: ")

if mutation_frequency == "Calculated":
    stattribute = input("\nWhat is the frequency ATTRIBUTE? ")
    units = input("What are the frequency UNITS (per day)? ")
    divisor = float(input("What is the frequency DIVISOR? "))
    mutation_frequency = (stattribute, units, divisor)

if isinstance(mutation_frequency, str):
    mutation_frequency = f'self.frequency = "{mutation_frequency}"'
elif isinstance(mutation_frequency, tuple):
    mutation_frequency = f"self.frequency = {mutation_frequency}"


# ROLL Bonuses
if please.say_yes_to("Are there ROLL bonuses? "):
    roll_bonus = input("What are the persona ROLL bonuses? ")
else:
    roll_bonus = None

if isinstance(roll_bonus, str):
    roll_bonus = f'self.roll_bonus = "{roll_bonus}"'
elif isinstance(roll_bonus, tuple) or roll_bonus is None:
    roll_bonus = f"self.roll_bonus = {roll_bonus}"

# ATTRIBUTE Bonuses
if please.say_yes_to("Are there ATTRIBUTE adjustments? "):
    stattribute = input("What is the ATTRIBUTE? ")
    units = int(input("What is the ADJUSTMENT? "))
    attribute_bonus = (stattribute, units)

else:
    attribute_bonus = None

attribute_bonus = f"self.attribute_bonus = {attribute_bonus}"


if please.say_yes_to("Is there a bespoke table? "):
    mutation_table = input("What is the table name? ")
    mutation_table = "table." + mutation_table
else:
    mutation_table = None


# perm complexity if at all

perm_complexity = [
    "NO calc NO perm -- desc only",
    "LIVE calc NO perm -- desc + calc",
    "No calc YES perm -- desc + perm",
    "Live calc YES perm -- desc + calc + perm",
    "It's complicated -- complex perm, attribute changes etc.",
]
perm_comment = "What is the nature of the perm value? "
perm_type = please.choose_this(perm_complexity, perm_comment)

some_thing = some_thing_else = 42

### NO CALC NO PERM ###
if perm_type == "NO calc NO perm -- desc only":
    desco = input("\nEnter the mutation DESCRIPTION: ")

    description = f"""
        self.add_mutation()
        
    def build_desc(self):
        return f"{desco}"
    """


### LIVE CALC NO PERM ###
elif perm_type == "LIVE calc NO perm -- desc + calc":
    description = f"""
        self.add_mutation()
    
    def build_desc(self):
        some_thing = 42
        return f'blah blah {{some_thing}}' """


### NO CALC YES PERM ###
elif perm_type == "No calc YES perm -- desc + perm":
    description = f"""
        self.add_mutation()
        
    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        return f'blah blah  blah.{{some_thing}}' """


### LIVE CALC YES PERM ###
elif perm_type == "Live calc YES perm -- desc + calc + perm":
    description = f"""
        self.add_mutation()
    
    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        some_thing_else = 42
        return f'blah   {{some_thing_else}} {{some_thing}}' """


elif perm_type == "It's complicated -- complex perm, attribute changes etc.":
    description = f"""
        # self.add_mutation() removed for complex perm
        
        #
        # calculation work
        #
        
        # assign perm
        
        # Check to avoid repeats 
        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = self.perm # equivalent of add_mutation()          
    
    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        some_thing_else = 42
        return f'bla {{some_thing_else}} {{some_thing}}'

    """


print(
    f"""
    
class {class_name}(Mutation): 
    def __init__(self, object):
        self.is_mental = {mutation_type}       
        self.object = object
        self.name = "{mutation_name}"
        self.kind = "{mutation_kind}"
        {mutation_distance}
        {mutation_duration}
        {mutation_frequency}
        self.CR = "{combat_ratio}"
        {roll_bonus}
        {attribute_bonus}
        self.table_name = {mutation_table}
        self.link = "#_{func_name}"
        {description}




new_mutation = {class_name}(test_me)
    """
)
