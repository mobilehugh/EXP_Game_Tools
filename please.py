import json
import math
import os
import re
import secrets
import time
from typing import Union

import a_persona_record
import table
import toy
import vocation


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

def choose_this(choices: list, message: str) -> str:
    """
    Choose from a list of choices and return the chosen item
    list can force default choice with AAA# prefix to element
    quit or restart or chastise the user
    """

    restart_commands = ["back", "reset", "restart", "RESET"]
    quit_commands = ["quit", "q", "exit", "QUIT"]

    # sets up choices identifying default AAA# element, alpha order and adding BACK QUIT
    choices.sort()
    if "AAA#" in choices[0]:
        choices[0] = choices[0].split('#')[1]
    choices.extend(["RESET","QUIT"])

    while True:

        # if only one choice on list return that choice automatically
        # the option to reset or quit is no given 
        if len(choices) < 4:
            choice = choices[0]
            break

        # present the message and options
        print(f"\n{message}")
        for idx, option in enumerate(choices, start=1):
            print(f"{idx}) {option}")

        choice = input(f"Please choose from above [{choices[0]}]: ")

        if not choice:
            choice = "1"

        if choice.isdigit():
            choice = int(choice)
            if 0 < choice <= len(choices):
                choice = choices[choice - 1] 
            else:
                print("\nPlease select a valid number.", end="")
                continue

        if choice in quit_commands:
            say_goodnight_marsha()
            break

        if choice in restart_commands:
            a_persona_record.record_chooser()
            break

        if choice in choices:
            break

        if choice not in choices:
            print("\nPlease select a valid choice.", end="")
            continue

    return choice


def say_yes_to(question: str) -> bool:
    """
    question string with boolean return
    """
    choice = choose_this(["AAA#Yes", "No"], question)
    return True if choice == "Yes" else False



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

    option_list = ["AAA#Random", "Bespoke", "Create New"]
    choice = choose_this(option_list, f"What do you want to do with {table_name}?")
    table_choice = "something malfed up here"

    if choice == "Random":
        table_choice = secrets.choice(table_choices_list)
    elif choice == "Bespoke":
        table_choice = choose_this(table_choices_list, "Choose from the table below:")
    elif choice == "Create New":
        print(f"Please carefully input a new element for {table_name}.")
        table_choice = input("New Element: ")

    return table_choice



###########################################
#
# dict and list manipulations
#
###########################################


def show_me_your_dict(dinkie: dict) -> None:
    """
    print out the dict that you want to see
    """

    if type(dinkie) == dict:
        print(f"\n{dinkie}")
        return

    new_liner = 0
    for key, value in dinkie.__dict__.items():
        this_pair = f"{key}: {value}   "
        new_liner += len(this_pair)
        print(f"{this_pair}", end="")
        if new_liner > 60:
            new_liner = 0
            print("")

    return


def colour_my_whirled(*args):
    pass


def get_table_result(table: dict) -> str:
    """
    return a single result from a random table
    """
    random = roll_this(table["die_roll"])
    for key in table:
        if random in key:
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
    """
    collated_list = []

    for item in skill_list:
        score = skill_list.count(item)
        collated_list.append(f"{item}-{str(score)}")

    send_list = list(set(collated_list))
    send_list.sort()

    return send_list


##############################################
#
# persona record storage and manipulations
#
##############################################


def store_locally(object: table.PersonaRecord) -> None:
    """
    takes chosen object and converts it to a JSONified dict and stores it locally
    """
    ### setting new Date_Updated
    object.Date_Updated = time.strftime("%a-%d-%b-%Y(%H:%M)", time.gmtime())

    ### retrieve file name and create JSON string
    file_name = object.File_Name
    record_to_store = json.dumps(object.__dict__)

    ### determine the directory based on FAMILY
    if object.FAMILY == "Toy":
        directory_to_use = "./Records/Toys/"
    else:
        directory_to_use = "./Records/Referee/" if object.RP else "./Records/Players/"

    with open(f"{directory_to_use}{file_name}", "a") as file:
        file.write(f"{record_to_store}\n")
    print(f"\n*** Record stored at ./Records/Personas/{file_name}")

    return


def record_storage(object: dict) -> None:
    """
    store as json in txt file, o/p JSON, create PDF
    """

    pivoteer = object.FAMILY

    option_list = [
        "Save Locally",
        "Copy Manually",
        "Nuke This Thing!",
    ]
    list_comment = f"\nWhat do you want to do with: {object.File_Name}?"
    storage_chosen = choose_this(option_list, list_comment)

    if storage_chosen == "Copy Manually":
        store_locally(object)
        table.output_pivot_table[pivoteer][1](object)
        print("\n\nFor JSON COPY BELOW including {}")
        print(json.dumps(object.__dict__))
        print("\n\n")
        input("\nPress Enter to continue...")
        return

    elif storage_chosen == "Save Locally":
        store_locally(object)
        table.output_pivot_table[pivoteer][0](object)
        return

    elif storage_chosen == "Nuke This Thing":
        clear_console()
        return


def attribute_manipulation(object: dict) -> None:
    """
    change almost any value in the persona record dict
    """

    if say_yes_to("you ain't cheatin are ya?"):
        a_persona_record.record_chooser()

    immutable_attributes = [
        "File_Name",
        "FAMILY",
        "ID",
        "Date_Create",
        "Mental_Mutations",
        "Physical_Mutations",
        "Interests",
        "Skills",
    ]

    for key, value in object.__dict__.items():
        if key not in immutable_attributes:
            choices = ["No", "Yes", "Exit"]
            choice_comment = f"{key} is {value} do you want to change this?"
            choice = choose_this(choices, choice_comment)
            if choice == "Yes":
                new_value = input(f"Please enter new value for {key}: ")
                if say_yes_to(
                    f"please confirm changing {key} from {value} to {new_value}?"
                ):
                    setattr(object, key, new_value)
            elif choice == "Exit":
                break

    store_locally(object)

    return


def assign_id_and_file_name(object: dict) -> None:
    """
    Assigns a file name to the object for the very first time. like a version...
    """
    linux_time = str(math.ceil(time.time()))  # unique time stamp

    if object.FAMILY == "Toy":
        print("\n*** There is no toy yet, so we'll make one for you.")
        file_name = "premature toy. please delete this file"
        return

    if (
        object.RP
    ):  # referee personas uppercase the persona_name have a simple unique_ident
        unique_ident = f"{linux_time}RP{object.FAMILY[:3]}"
        file_name = f'referee_{object.FAMILY.lower()}_{object.Player_Name.replace(" ", "_").lower()}_{object.Persona_Name.replace(" ", "_").upper()}_{object.Vocation.lower()}_{unique_ident}.txt'

    elif not object.RP:
        unique_ident = f"{linux_time}{object.Player_Name[:2].upper()}{object.FAMILY[:2].upper()}{object.Vocation[:2].upper()}"
        file_name = f'player_{object.FAMILY.lower()}_{object.Player_Name.replace(" ", "_").upper()}_{object.Persona_Name.replace(" ", "_").lower()}_{object.Vocation.lower()}_{unique_ident}.txt'

    setattr(object, "File_Name", file_name)
    setattr(object, "Date_Created", time.strftime("%a-%d-%b-%Y(%H:%M)", time.gmtime()))
    setattr(object, "Date_Updated", time.strftime("%a-%d-%b-%Y(%H:%M)", time.gmtime()))

    return


def collect_required_records(record_type: str) -> dict:
    """
    generates a list of required records, user selects one
    """
    object = table.PersonaRecord()
    print(f"please -- line 428 {type(object) = }")

    # finder for long list of hard to type file names
    if record_type == "Toy":
        directory_to_use = "./Records/Toys/"

    elif record_type == "Players":
        directory_to_use = "./Records/Players/"

    elif record_type in ["Alien", "Anthro", "Robot", "All"]:
        directory_to_use = "./Records/Referee/"
    else:
        print("\n*** ERROR: directory not found")
        quit()

    list_of_files = os.listdir(directory_to_use)

    ### clear any pdfs from the list
    list_of_files = [x for x in list_of_files if x[-3:] != "pdf"]

    if record_type in ["Alien", "Anthro", "Robot"]:
        list_of_files = [x for x in list_of_files if f"_{record_type.lower()}_" in x]

    if len(list_of_files) == 0:
        print(f"\n*** ERROR: no files found in {directory_to_use}")
        if say_yes_to("Would you like to continue?"):
            a_persona_record.record_chooser()
        else:
            say_goodnight_marsha()

    list_comment = "Choose the desired record."
    persona_record = choose_this(list_of_files, list_comment)

    # get latest record on persona (AKA last line of file)
    with open(directory_to_use + persona_record, "r") as f:
        file_data = f.readlines()[-1]

    dict_data = json.loads(file_data)

    object = table.PersonaRecord()
    for key, value in dict_data.items():
        setattr(object, key, value)

    return object


def do_referee_maintenance():
    """
    things that referee's need to access and do
    """

    if not say_yes_to("\nAre you a referee?"):  # referee check for fun 
        a_persona_record.record_chooser()

    record_type = choose_this(
        ["Players", "Alien", "Anthro", "Robot", "Toy", "All"], "What records to search?"
    )
    object = collect_required_records(record_type)

    maintenance_choice = "I like turtles"
    while maintenance_choice != "Exit":
        pivoteer = object.FAMILY

        item_list = [
            "EXPS Update",
            "Level Update",
            "Name Change",
            "Review On Screen",
            "PDF Update",
            "PDF On Screen",
            "PDF Backpage",
            "Attribute Manipulation",
            "Change Working Record",
            "Exit",
        ]
        item_comment = f"What are you doing to {object.Persona_Name}?"
        maintenance_choice = choose_this(item_list, item_comment)

        if maintenance_choice == "EXPS Update":
            vocation.update_persona_exps(object)
            store_locally(object)
            table.output_pivot_table[pivoteer][0](object)

        elif maintenance_choice == "Level Update":
            object.Level = int(input("\nPlease input your new Level value: "))
            # function call to update Level in record
            store_locally(object)
            table.output_pivot_table[pivoteer][0](object)

        elif maintenance_choice == "Name Change":
            new_name = input("\nPlease input your new PERSONA Name: ")

            print(f"The new name for {object.Persona_Name} is {new_name}")
            print(f"File name {object.File_Name} does NOT change")
            setattr(object, "Persona_Name", new_name)
            store_locally(object)
            table.output_pivot_table[pivoteer][0](object)

        elif maintenance_choice == "Review On Screen":
            table.output_pivot_table[pivoteer][1](object)

        elif maintenance_choice == "PDF Update":
            table.output_pivot_table[pivoteer][0](object)

        elif maintenance_choice == "PDF Backpage":
           table.output_pivot_table[pivoteer][3](object)


        elif maintenance_choice == "PDF On Screen":
            table.output_pivot_table[pivoteer][0](object)  # update the PDF
            table.output_pivot_table[pivoteer][2](object)

        elif maintenance_choice == "Attribute Manipulation":
            attribute_manipulation(object)

        elif maintenance_choice == "Change Working Record":
            record_type = choose_this(
                ["Players", "Alien", "Anthro", "Robot", "Toy", "All"],
                "What record type?",
            )
            object = collect_required_records(record_type)

    return





def clear_console() -> None:
    """
    Clears the console on different OSs
    """
    os.system("cls" if os.name == "nt" else "clear")

def say_goodnight_marsha() -> None:
    clear_console()
    print("".center(31, "*"))
    print("* Thank you for your service. *")
    print("".center(31, "*"))
    print()
    quit()
