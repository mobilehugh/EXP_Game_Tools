import json
import math
import os
import sys
import re
import subprocess
from secrets import choice, randbelow
import time
from typing import Union, List
from itertools import islice
from collections import Counter
from dataclasses import dataclass

import a_persona_record
import core
import exp_tables
import vocation
import outputs
import mutations
import toy

import alien
from anthro import anthro_nomenclature
from robot import robot_nomenclature

@dataclass 
class AllRecords(exp_tables.AllThings):
    pass

""" 
Please contains several functions that respond to please.<whatever>
These are helper functions that are used by all record types
"""


###########################################
#
# dice rolling functions
#
###########################################

def explode_this(all_dice:list, die_type:int) -> int:
    ''' takes a list of dice and explodes 'em'''
    result = sum(all_dice)
    while die_type in all_dice:
        explodes = all_dice.count(die_type)
        all_dice = []
        for _ in range(explodes):
            new_die = f'1d{str(die_type)}'
            all_dice.append(roll_this(new_die))
        result += sum(all_dice)
        
    return result

def roll_this(die_roll_string: str) -> int:
    """
    die roll must be in the format of "xdy+z", returns integer result
    if die roll request does not compute a str is returned
    """
    # in a type violation returns a string instead of an integer when there  is a dice error
    dice_error = f"Oops! {die_roll_string} Does not compute. \nparams = [1-99]d[1-1000][+|-|*|D][0-9999] \nExamples: 2d6+2, 1d1000, 6d6E (explode on 6), 4d6D1 (drop lowest)"


    # pulling die parts 1 d 6 + 1 ect from the die_roll_string string
    die_parts = re.compile(r"(\d{1,4})d(\d{1,5})(\+|\-|\*|D|E)*(\d{1,5})*").search(
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
    all_dice = sorted([randbelow(die_type) + 1 for _ in range(die_amount)], reverse=True)

    # die_mod processing and error checks
    if die_mod == "D":
        if mod_amount >= len(all_dice):
            return dice_error
        result = sum(all_dice[:-mod_amount])

    elif die_mod == "E":
        if die_type not in all_dice:
            return sum(all_dice)
        else:
           return explode_this(all_dice, die_type)

    elif die_mod is None:
        result = sum(all_dice)

    elif die_mod == "+":
        result = sum(all_dice) + mod_amount

    elif die_mod == "-":
        result = sum(all_dice) - mod_amount

    elif die_mod == "*":
        result = sum(all_dice) * mod_amount
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

def toxic(safer:str) -> bool:
    '''bad letters or too short letters '''

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

    if too_short_word(safer) or evil_characters(safer):
        return True
    else:
        return False
    
def input_this(message: str) -> str:
    ''' protects input data and returns str '''
    safer = input(message)
    safer = int(safer) if safer.isdigit() else safer

    while toxic(safer):
        print(f'Too short, too long, or knotty characters.')
        safer = input(message)
        safer = int(safer) if safer.isdigit() else safer

    if say_yes_to(f'Are you okay with {safer}:'):
        return safer
    else:
        # clear_console()
        return input_this(message)

def choose_this(choices: list, comment: str, choosy: AllRecords = None) -> str:
    """
    Choose from a list of choices and return the chosen item
    [default] element for list choices[0]
    quit or restart or chastise the user
    also auto return if Fallthrough is true
    """
    # if fallthrough skip choosing part

    if choosy:
        if choosy.Fallthrough:
            return choice(choices)
    
    if choosy:
        if choosy.Bespoke:
            if say_yes_to(f'Would you like randomize -> {comment.upper()}'):   
                return choice(choices)

    # [0] is default, sort, reinsert default and add directions
    default = choices.pop(0)
    choices.sort()
    choices.insert(0,default)

    while True:
        # if only one choice on list return that choice automatically
        # the option to reset or quit is no given 

        # present the comment and options
        print(f"\n{comment}")

        if "Yes" in choices and len(choices) < 3: # keeps yes/no to a one line list
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


###########################################
#
# dict and list manipulations
#
###########################################

def show_me_your_dict(dinkie: AllRecords) -> None:
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


# todo should be one function for table and list result
def get_table_result(random_table: dict) -> str:
    """
    return a single result from a random table
    this is the deranged version using tuples that are more table like 
    """
    roll_result = roll_this(random_table["die_roll"])

    result = ""

    random_table = {key: val for key, val in random_table.items() if key not in ["name","die_roll","number", "title"]}

    for item_range in random_table.keys():
        if roll_result in range(item_range[0],item_range[1]+1): # correct for normal tables (90,100) -> (90,101)
            result = random_table[item_range]
            break

    if not result:
        input(f'there is an error in the table {repr(random_table)}\n return to go on' )

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

def enumerate_this(list_title: str, number_me: list, sort_it:bool = True) -> None:
    '''prints out a list numbered with a title '''
    
    if sort_it:
        number_me.sort()

    print(f'{list_title}', end="")
    if len(number_me) < 1:
        print("None")
        return
    print("")
    for x, attack in enumerate(number_me,1):
        print(f"{x}) {attack}")

    return


##############################################
#
# persona record storage and manipulations
#
##############################################

def store_this(record_to_store: AllRecords) -> None:
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
    if record_to_store.FAMILY == "Toy":
        store_here = "Toy"
    else:
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

def record_storage(record_to_store: AllRecords) -> None:
    """
    organizes what to do with a record and prints it out
    """
    print(f'{record_to_store.File_Name}')

    option_list = ["Save", "Copy Out","Bin"]

    list_comment = f"What do you want to do with {record_to_store.Persona_Name}?"
    storage_chosen = choose_this(option_list, list_comment)

    if storage_chosen == "Copy Out":
        store_this(record_to_store)
        clear_console()
        print("\n\nCOPY JSON BELOW for TRANSFER (include curly brackets {})")
        print(json.dumps(record_to_store.__dict__))
        print("\n\n")
        input("\nPress Enter to continue...")
        return

    elif storage_chosen == "Save":
        store_this(record_to_store)
        return

    elif storage_chosen == "Bin":
        record_to_store.Bin = True
        store_this(record_to_store)        
        return


def assign_file_name(persona_record: AllRecords) -> None:
    """
    Assigns a File_name to persona_record for the very first time. like a version...
    I think this is only used once per record
    """
    if persona_record.FAMILY == "Toy":
        front = persona_record.Perms["Desc"].replace(" ", "_").upper()

    elif persona_record.RP and persona_record.FAMILY != "Toy": 
        front = persona_record.Persona_Name.replace(" ", "_").upper()

    elif not persona_record.RP and persona_record.FAMILY != "Toy":
        front = persona_record.Player_Name.replace(" ", "_").upper()

    back = f'{persona_record.FAMILY.lower()}_{persona_record.FAMILY_TYPE.replace(" ", "_").lower()}_{persona_record.FAMILY_SUB.replace(" ", "_").lower()}'
    vocay = "" if persona_record.Vocation in ["Alien","Robot","Toy"] else f'_{persona_record.Vocation.lower()}'
    unix_time = f'_{str(math.ceil(time.time()))}'


    ## assign File_Name
    persona_record.File_Name = f'{front}_{back}{vocay}{unix_time}.jsonl'

    ## assign Date_Created first time
    if persona_record.Date_Created in ["Unevolved", "Soon", "Unborn", "Unmade"]:
        persona_record.Date_Created = time.strftime("%a-%d-%b-%Y(%H:%M)", time.gmtime())
    
    ## assign Date_Updated first time 
    persona_record.Date_Updated = time.strftime("%a-%d-%b-%Y(%H:%M)", time.gmtime())

def collect_desired_record() -> AllRecords:
    """
    generates a list of required records, user selects one
    """
    clear_console()
    record_type = choose_this(["Players", "Alien", "Anthro", "Robot", "Toy", "Ref", "Bin"], "What directory to search?")    
    
    # finder for long list of hard to type file names
    if record_type == "Toy":
        directory_to_search = "./Records/Toys/"

    elif record_type == "Players":
        directory_to_search = "./Records/Players/"

    elif record_type in ["Alien", "Anthro", "Robot", "Ref"]:
        directory_to_search = "./Records/Referee/"

    elif record_type == "Bin":
        directory_to_search = ".Records/Bin/"

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

    record_to_return = AllRecords()
    for key, value in data_pairs.items():
        setattr(record_to_return, key, value)
    return record_to_return


# todo add move file to maintenance 
def do_referee_maintenance():
    """
    things that referee's need to access and do
    """
    persona = collect_desired_record()

    operations = {
    "EXPS": vocation.update_persona_exps,
    "Level": vocation.update_persona_exps,
    "Screen": lambda persona: outputs.outputs_workflow(persona, "screen"),
    "PDF <- off service": lambda persona: outputs.outputs_workflow(persona, "screen"), # todo change back when PDF working
    "Attributes": lambda persona: core.manual_persona_update(persona),
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

def fix_robot_MSTR(mr_int: AllRecords) -> int:
    '''swap robot INT for MSTR where needed'''
    return mr_int.MSTR if mr_int.FAMILY != "Robot" else mr_int.INT

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

def setup_persona(choosy:AllRecords)-> AllRecords:
    '''initial setup for personas'''

    # clearance for Clarence
    clear_console()

    if choosy.Bespoke:
        kindof = "BESPOKE"
    elif choosy.Fallthrough:
        kindof = "RANDOM"
    else:
        kindof = "FRESH"
    
    print(f"\nHello {choosy.Player_Name}. You are generating a {kindof} {choosy.FAMILY.upper()} persona.")  

    if choosy.Bespoke or choosy.Fallthrough:
        choosy.RP = True if say_yes_to("Are you generating a REFEREE PERSONA?") else False
    choosy.RP_Cues = True if say_yes_to("Would you like role-playing cues? ") else False
    return choosy # altered by side effects

def get_kind_of(kindy:AllRecords) -> str:
    ''' returns FRESH, BESPOKE or RANDO for wrap up'''
    if kindy.Bespoke:
        kindof = "BESPOKE"
    elif kindy.Fallthrough:
        kindof = "RANDOM"
    else:
        kindof = "FRESH"
        
    return kindof


def screen_this(screeny:AllRecords) -> None:
    ''' directs person to correct screening type based on FAMILY'''
    ## determine show on screen function by FAMILY
    function_map_reviews = {
        "Alien": outputs.alien_screen,
        "Anthro": outputs.anthro_screen,
        "Robot": outputs.robot_screen,
        "Toy": outputs.toy_screen,
    }
    screen_func = function_map_reviews[screeny.FAMILY]
    screen_func(screeny)


def persona_nomenclature(avatar_name: AllRecords) -> None:
    """
    direct to correct naming func by FAMILY
    """

    ### get mundane terran name of the player
    nomenclature_map ={
        "Alien": alien.alien_nomenclature,
        "Anthro": anthro_nomenclature,
        "Robot": robot_nomenclature,
        "Toy": outputs.toy_screen,
    }

    nomenclature_func = nomenclature_map[avatar_name.FAMILY]   
    nomenclature_func(avatar_name)


def wrap_up_persona(wrappy:AllRecords)->AllRecords:
    '''review, name and file the persona'''

    clear_console()
    input(f'\n{wrappy.Player_Name} has created a {get_kind_of(wrappy)} {wrappy.FAMILY.upper()} persona.\nHit RETURN to review..')
    screen_this(wrappy)
    print(f'\nYou may need to SCROLL UP to fully review...')
    input(f'Hit RETURN when ready to NAME your {get_kind_of(wrappy)} {wrappy.FAMILY.upper()}...')
    persona_nomenclature(wrappy)
    assign_file_name(wrappy)
    clear_console()
    screen_this(wrappy)
    print(f'\nYou may need to SCROLL UP to fully review...')
    record_storage(wrappy)

    return wrappy # modified by side effects
