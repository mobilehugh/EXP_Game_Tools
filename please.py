import json
import math
import os
import sys
import re
import subprocess
import secrets
import time
from typing import Union, List
from itertools import islice
from collections import Counter

import a_persona_record
import core
import table
import vocation
import outputs
import mutations


""" 
Please contains several functions that respond to please.<whatever>
These are helper functions that are used by all record types
"""

###########################################
#
# dice rolling functions
#
###########################################

def roll_this(die_roll_string: str) -> int:
    """
    die roll must be in the format of "xdy+z", returns integer result
    if die roll request does not compute a str is returned
    """
    # in a type violation returns a string instead of an integer when there  is a dice error
    dice_error = f"Oops! {die_roll_string} Does not compute. Examples: 2d6+2, 1d1000, 4d6D1 (drop lowest)"


    # pulling die parts 1 d 6 + 1 ect from the die_roll_string string
    die_parts = re.compile(r"(\d{1,4})d(\d{1,5})(\+|\-|D)*(\d{1,5})*").search(
        die_roll_string
    )

    # if string not a die roll bail
    if not die_parts:
        return dice_error


    # assign values to the die roll parts 
    die_amount, die_type, die_mod, mod_amount = die_parts.group(1, 2, 3, 4)

    if not die_mod or not mod_amount:
        mod_amount = 0
    die_amount, die_type, mod_amount = (
        int(die_amount),
        int(die_type),
        int(mod_amount),
    )

    # die_amount error checking and int conversion
    if die_amount < 1 or die_amount > 99:
        return dice_error

    # die_type error checking and int conversion
    if die_type < 1 or die_type > 1000 or mod_amount > 9999:
        return dice_error

    # create a list of the die rolls
    all_dice = sorted([secrets.randbelow(die_type) + 1 for _ in range(die_amount)], reverse=True)

    # die_mod processing and error checks
    if die_mod == "D":
        if mod_amount >= len(all_dice):
            return dice_error
        result = sum(all_dice[:-mod_amount])

    elif die_mod is None:
        result = sum(all_dice)

    elif die_mod == "+":
        result = sum(all_dice) + mod_amount

    elif die_mod == "-":
        result = sum(all_dice) - mod_amount
    else:
        print("this error should never happen")
        return dice_error

    return result

def do_1d100_check(number: int) -> bool:
    """
    Checks to see if 1d100 is less than or equal to the argument
    """
    return roll_this("1d100") <= number

###########################################
#
# user choice functions
#
###########################################

# todo apply input_this to every input
# todo input_this needs to get for_a_list flag called 

def input_this(message: str, for_a_list: bool = False) ->  Union[str, List[str]]:
    ''' protects input data and returns str or list'''

    def evil_characters(is_input_evil:str) -> bool:
        '''are there any evil characters in the str? '''
        special_chars = ["%", "@", "#", "$", "(", ")", "<", ">", "&", "/", ";", "|"]

        if isinstance(is_input_evil, int):
            return False

        for char in special_chars:
            if char in is_input_evil:
                return True
        return False
    
    def too_short_word(is_too_short:str) -> bool:
        ''' allows for short digits for input but not short words'''
        if isinstance(is_too_short, int):
            return False
        if len(is_too_short) in range(3,30):
            return False
        else:
            return True


    safer = input(message)
    if safer.isdigit():
        safer = int(safer)

    while too_short_word(safer) or evil_characters(safer):
        print(f'Too short, too long or knotty characters.')
        safer = input(message)
        if safer.isdigit():
            safer = int(safer)

    if for_a_list:
        a_list = []
        a_list.append(safer)
    else:
        a_list = safer
    
    return a_list

# todo connect choose this with clean this input
# todo what should R reset  do?
def choose_this(choices: list, message: str) -> str:
    """
    Choose from a list of choices and return the chosen item
    [default] element for list choices[0]
    quit or restart or chastise the user
    """

    # [0] is default, sort, reinsert default and add directions
    default = choices.pop(0)
    choices.sort()
    choices.insert(0,default)

    while True:
        # if only one choice on list return that choice automatically
        # the option to reset or quit is no given 

        # present the message and options
        print(f"\n{message}")

        if len(choices) == 2: # keeps say what ever to to one line list
            print (f'1) {choices[0]} 2) {choices[1]}')
        else:
            for idx, option in enumerate(choices, start=1):
                print(f"{idx}) {option}")

        chosen = input(f"Please choose from above [R-reset][Q-quit] [Ret->{choices[0]}]: ")

        if not chosen:
            chosen = "1"

        if chosen.isdigit():
            chosen = int(chosen)
            if 0 < chosen<= len(choices):
                chosen = choices[chosen- 1] 
            else:
                print("\nPlease select a valid number.", end="")
                continue

        if chosen == "Q":
            say_goodnight_marsha()
            break

        if chosen == "R":
            a_persona_record.record_chooser()
            break

        if chosen in choices:
            break

        if chosen not in choices:
            print("\nPlease select a valid choice.", end="")
            continue

    return chosen

def say_yes_to(question: str) -> bool:
    """
    question string with boolean return
    """
    chosen = choose_this(["Yes", "No"], question)
    return True if chosen == "Yes" else False

def say_no_to(question: str) -> bool:
    """
    question string with boolean return
    """
    chosen = choose_this(["No", "Yes"], question)
    return True if chosen == "No" else False    

def bespokify_this_table(table_chosen: Union[dict, list]) -> str:
    """
    return a string either chosen, randomized or created
    """
    # create the list to work from (can be dict or list)
    table_choices_list = list_table_choices(table_chosen)

    # get table name from dict or  call it this list
    if isinstance(table_chosen, dict):
        table_name = 'the ' + table_chosen.get('name', 'this list') + ' Table'
    elif isinstance(table_chosen, list):
        table_name = "this list"

    option_list = ["Random", "Bespoke", "Create New"]
    chosen = choose_this(option_list, f"What do you want to do with {table_name}?")
    table_chosen = "something malfed up here"

    if chosen == "Random":
        table_chosen = secrets.choice(table_choices_list)
    elif chosen == "Bespoke":
        table_chosen = choose_this(table_choices_list, "Choose from the table below:")
    elif chosen == "Create New":
        print(f"Please carefully input a new element for {table_name}.")
        table_choice = input("New Element: ")

    return table_choice

###########################################
#
# dict and list manipulations
#
###########################################

def show_me_your_dict(dinkie: table.PersonaRecord) -> None:
    """
    Prints out the dict or object's attribute dictionary.
    should this be deprecated
    """

    if isinstance(dinkie, dict):
        items = iter(dinkie.items())
    elif hasattr(dinkie, '__dict__'):
        items = iter(dinkie.__dict__.items())
    else:
        raise AttributeError("'dinkie' should be a dict or an object with a '__dict__'.")
    
    if "name" in dinkie:
        print(dinkie["name"].upper())
    else:
        print("this list".upper())

    while True:
        # Extracting 2 items at a time using islice
        batch = list(islice(items, 2))
        if not batch:
            break
        for key, value in batch:
            print(f"{key}: {value}", end='   ')
        print()  # Print newline after each batch

def colour_my_whirled(*args):
    pass

def get_table_result(table: dict) -> str:
    """
    return a single result from a random table
    this is the deranged version using tuples that are more table like 
    """
    random = roll_this(table["die_roll"])
    for key in table:
        chance_list = range(key[0],(key[1]+1))
        if random in chance_list:
            result = table[key]
            break
    return result



def list_table_choices(table_chosen:dict) -> list:
    """
    returns a list of elements stripped from a table dict or list
    Uses list comprehension and removes table labels from list
    """
    EXCLUDED_DICT_VALUES = ["Choose", "Extra Roll", "Secondary"]
    EXCLUDED_DICT_KEYS = ["name", "die_roll", "title"]

    if isinstance(table_chosen, dict):
        # If input is a dictionary, filter keys and values
        choices = [
            value
            for key, value in table_chosen.items()
            if value not in EXCLUDED_DICT_VALUES
            and key not in EXCLUDED_DICT_KEYS
        ]
    elif isinstance(table_chosen, list):
        # If input is a list, do nothing
        choices = table_chosen
    else:
        # If input is neither list nor dict, raise TypeError
        raise TypeError("Input to list_table_choices must be a list or a dictionary.")

    return choices

def collate_this(skill_list: list) -> list:
    """
    Collates a list by enumerating by total elements
    for example, mechanics-2 instead of ["mechanics", "mechanics"]
    """
    counter = Counter(skill_list)
    collated_list = [f"{item}-{count}" for item, count in counter.items()]
    collated_list.sort()

    return collated_list

##############################################
#
# persona record storage and manipulations
#
##############################################

def store_this(record_to_store: table.PersonaRecord) -> None:
    """
    takes chosen record_to_store and converts it to a JSONified dict and stores it locally
    """
    ### setting new Date_Updated
    record_to_store.Date_Updated = time.strftime("%a-%d-%b-%Y(%H:%M)", time.gmtime())

    ### retrieve file name
    file_name_to_use = record_to_store.File_Name

    ### create JSON to add to  file name
    json_to_add = json.dumps(record_to_store.__dict__)

    ### determine the directory to use
    # beware of the ternary for ./Records/Referee/ vs ./Records/Players/
    if record_to_store.FAMILY != "Toy":
        store_here = "Referee" if record_to_store.RP else "Player"
    if record_to_store.Bin:
        store_here = "Bin"

    where_to_store = {
        "Toy":"./Records/Toys/",
        "Player":"./Records/Players/",
        "Referee":"./Records/Referee/",
        "Bin":"./Records/Bin/",
    }
    directory_to_use = where_to_store[store_here]

    ### append to json lines .jsonl
    with open(f"{directory_to_use}{file_name_to_use}", "a") as file:
        file.write(f"{json_to_add}\n")

    input(f"\n*** Record stored at {directory_to_use}{file_name_to_use}. Continue? ")

def record_storage(record_to_store: table.PersonaRecord) -> None:
    """
    organizes what to do with a record and prints it out
    """
    option_list = [
        "Save",
        "Copy Out",
        "Bin",
    ]

    list_comment = f"\nWhat do you want to do with: {record_to_store.File_Name}?"
    storage_chosen = choose_this(option_list, list_comment)

    ### prep for outputs
    # no pdfs

    function_map_reviews = {
        "Alien": outputs.alien_screen,
        "Anthro": outputs.anthro_screen,
        "Robot": outputs.robot_screen,
    }
    review_screen = function_map_reviews[record_to_store.FAMILY]

    if storage_chosen == "Copy Out":
        store_this(record_to_store)
        review_screen(record_to_store) #prints out on screen
        print("\n\nCOPY JSON BELOW for TRANSFER include curly brackets {}")
        print(json.dumps(record_to_store.__dict__))
        print("\n\n")
        input("\nPress Enter to continue...")
        return

    elif storage_chosen == "Save":
        store_this(record_to_store)
        review_screen(record_to_store) #prints out on screen no more stored PDFs
        return

    elif storage_chosen == "Bin":
        record_to_store.Bin = True
        store_this(record_to_store)        
        clear_console()
        return


def assign_id_and_file_name(persona_record: table.PersonaRecord) -> None:
    """
    Assigns an ID and  File_name to persona_record for the very first time. like a version...
    I think this is only used once per record
    """
    try:
        if persona_record.FAMILY == "Toy":
            id_name = (
                f'{(persona_record.Persona_Name.replace(" ", "_").lower() + "_") if persona_record.Persona_Name != "Nobody" else ""}'
                f'{persona_record.FAMILY_TYPE.upper()}_{persona_record.FAMILY_SUB.replace(" ","_").upper()}_'
                f'{str(math.ceil(time.time()))}' # unique time stamp and file type
            )
        elif persona_record.RP and persona_record.FAMILY != "Toy":
            id_name = (
                f'{persona_record.Persona_Name.replace(" ", "_").upper()}_'
                f'{persona_record.FAMILY.lower()}_{persona_record.FAMILY_TYPE.lower()}_'
                f'{(persona_record.FAMILY_SUB.lower() + "_") if persona_record.FAMILY_SUB else ""}'
                f'{persona_record.Vocation.lower()}_'
                f'{str(math.ceil(time.time()))}' # unique time stamp and file type
            )
        else:
            id_name = (
                f'{persona_record.Player_Name.replace(" ", "_").upper()}_'
                f'{(persona_record.Persona_Name.replace(" ", "_").lower() + "_") if persona_record.Persona_Name != "Nobody" else ""}'
                f'{persona_record.FAMILY.lower()}_{persona_record.FAMILY_TYPE.lower()}_'
                f'{(persona_record.FAMILY_SUB.lower() + "_") if persona_record.FAMILY_SUB else ""}'
                f'{persona_record.Vocation.lower()}_'
                f'{str(math.ceil(time.time()))}' # unique time stamp and file type
            )
        persona_record.ID = id_name
        persona_record.File_Name = id_name + ".jsonl"

        if not persona_record.Date_Created or persona_record.Date_Created == "Soon":
            persona_record.Date_Created = time.strftime("%a-%d-%b-%Y(%H:%M)", time.gmtime())

        persona_record.Date_Updated = time.strftime("%a-%d-%b-%Y(%H:%M)", time.gmtime())
    except AttributeError as error:
        print(f"PersonaRecord doesn't have the necessary attributes. {error}")

def collect_desired_record() -> table.PersonaRecord:
    """
    generates a list of required records, user selects one
    """
    record_type = choose_this(["Players", "Alien", "Anthro", "Robot", "Toy", "Ref"], "What directory to search?")    
    
    # finder for long list of hard to type file names
    if record_type == "Toy":
        directory_to_search = "./Records/Toys/"

    elif record_type == "Players":
        directory_to_search = "./Records/Players/"

    elif record_type in ["Alien", "Anthro", "Robot", "Ref"]:
        directory_to_search = "./Records/Referee/"
    else:
        print("\n*** ERROR: directory not found")
        say_goodnight_marsha()

    list_of_files = os.listdir(directory_to_search)

    ### clear any pdfs from the list
    list_of_files = [x for x in list_of_files if x[-3:] != "pdf"]

    if record_type in ["Alien", "Anthro", "Robot"]:
        list_of_files = [x for x in list_of_files if f"_{record_type.lower()}_" in x]

    if len(list_of_files) == 0:
        print(f"\n*** ERROR: no files found in {directory_to_search}")
        if say_yes_to("Would you like to continue?"):
            a_persona_record.record_chooser()
        else:
            say_goodnight_marsha()

    list_comment = "Choose the desired record."
    persona_record = choose_this(list_of_files, list_comment)

    # get latest record on persona (AKA last line of file)
    with open(directory_to_search + persona_record, "r") as f:
        file_data = f.readlines()[-1]

    data_pairs = json.loads(file_data)

    record_to_return = table.PersonaRecord()
    for key, value in data_pairs.items():
        setattr(record_to_return, key, value)
    return record_to_return

def do_referee_maintenance():
    """
    things that referee's need to access and do
    """
    persona = collect_desired_record()

    operations = {
    "EXPS": vocation.update_persona_exps,
    "Level": vocation.update_persona_exps,
    "Screen": lambda persona: outputs.outputs_workflow(persona, "screen"),
    "PDF": lambda persona: outputs.outputs_workflow(persona, "pdf"),
    "Attributes": lambda persona: core.manual_persona_update(),
    "Change Record": lambda persona: do_referee_maintenance(),}
    
    operation_list = [key for key in operations]

    maintenance_choice = "I like turtles"
    while maintenance_choice != "Exit":
        item_comment = f"What are you doing to {persona.Persona_Name.upper()}?"
        maintenance_choice = choose_this(operation_list, item_comment)

        operation = operations.get(maintenance_choice)
        if operation is not None:
            operation(persona)
            continue
        else:
            print("operation missing")
            say_goodnight_marsha()

    return

def clear_console() -> None:
    """
    Clears the console on different OSs
    """
    cmd = "cls" if os.name == "nt" else "clear"

    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to clear the console: {e}")


def say_goodnight_marsha() -> None:
    """
    Clears the console, prints a farewell message, and exits the program.
    """
    clear_console()
    print("".center(31, "*"))
    print("* Thank you for your service. *")
    print("".center(31, "*"), "\n") # "\n" added here to create a new line
    sys.exit()
