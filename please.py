import re
import secrets
import os
import json
import math
import time

import toy
import vocation
import a_persona_record
import table

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
    """

    dice_error = f"\nDICE ERROR: {die_roll_string} \nPlease check your die roll.\nExamples: 2d6+2, 1d1000, 4d6D1 (drop lowest)\n"

    # pulling die parts 1 d 6 + 1 ect from the die_roll_string string
    die_parts = re.compile(r"(\d{1,4})d(\d{1,5})(\+|\-|D)*(\d{1,5})*").search(
        die_roll_string
    )

    if die_parts:

        die_amount, die_type, die_mod, mod_amount = die_parts.group(1, 2, 3, 4)

        # cleaning up the die data Nones and missing parts
        if not die_mod or not mod_amount:
            mod_amount = 0
        die_amount, die_type, mod_amount = (
            int(die_amount),
            int(die_type),
            int(mod_amount),
        )

        # die_amount error checking and int conversion
        if die_amount < 1 or die_amount > 99:
            print(dice_error)
            return False

        # die_type error checking and int conversion
        if die_type < 1 or die_type > 1000 or mod_amount > 9999:
            print(dice_error)
            return False

        # create a list of the die rolls
        all_dice = []
        for __ in range(die_amount):
            new_roll = secrets.randbelow(die_type) + 1
            all_dice.append(new_roll)
            all_dice = sorted(all_dice, reverse=True)

        # die_mod processing and error check
        if die_mod == "D":
            if mod_amount >= len(all_dice):
                # print(dice_error)
                return False

            for __ in range(mod_amount):
                all_dice.pop()
            result = sum(all_dice)

        elif die_mod is None:
            result = sum(all_dice)

        elif die_mod == "+":
            result = sum(all_dice) + mod_amount

        elif die_mod == "-":
            result = sum(all_dice) - mod_amount
        else:
            print("this error should never happen")
            print(dice_error)
            return False

    else:
        result = False
        print(dice_error)

    return result


def do_1d100_check(number: int) -> bool:
    """
    Checks to see if 1d100 is less than or equal to the argument
    """
    if roll_this("1d100") <= number:
        return True
    else:
        return False


###########################################
#
# user choice functions
#
###########################################


def choose_this(choices: list, message: str) -> str:
    """
    Choose from a list of choices and return the chosen item
    quit or restart or chastise the user
    """
    if len(choices) < 2:
        return choices[0]

    print(f"\n{message}")
    for x, option in enumerate(choices):
        print(f"{x + 1}) {option}")

    choice = input("Please choose from above (ret -> 1): ")

    if choice == "":
        choice = "1"

    if choice.isdigit():
        choice = int(choice)
        if choice > 0 and choice <= len(choices):
            return choices[choice - 1]
        else:
            print("Please choose valid option.")
            return choose_this(choices, message)

    ### restart detection ###
    if choice in ["back", "Back", "reset", "Reset", "restart", "Restart"]:
        a_persona_record.record_chooser()

    ### quit detection ###
    if choice in ["quit", "Quit", "q", "Q", "exit", "Exit"]:
        say_goodnight_marsha()

    #### error detection ####
    if choice not in choices:
        print("Your choice is out of range. ")
        return choose_this(choices, message)
    print("")

    return choice


def say_yes_to(question: str) -> bool:
    """
    Returns True for Yes and False for No
    """
    choice = choose_this(["Yes", "No"], question)
    if choice in ["Yes", "yes", "Y", "y", ""]:
        return True
    elif choice in ["No", "no", "N", "n"]:
        return False


def bespokify_this_table(table_chosen: dict) -> str:
    """
    return a string either chosen, randomized or created
    """

    # create the list to work from (can be dict or list)
    table_choices_list = list_table_choices(table_chosen)

    # does the table have a name?
    if type(table_chosen) == dict:
        has_name = True if "name" in table_chosen.keys() else False
        if has_name:
            table_name = f'the {table_chosen["name"]} Table'
        else:
            table_name = "this list"

    elif type(table_chosen) == list:
        table_name = "this list"

    else:
        print("ERROR: table_chosen is not a dict or list")

    option_list = ["Random", "Bespoke", "Create New"]
    choice = choose_this(option_list, f"What do you want to do with {table_name}?")
    print(f"{choice = }")
    table_choice = "something malfed up here"

    if choice == "Random":
        table_choice = secrets.choice(table_choices_list)

    elif choice == "Bespoke":
        table_choice = choose_this(table_choices_list, "Choose from the table below:")

    elif choice == "Create New":
        print(f"Please carefully input a new element for the {table_name} Table.")
        table_choice = input("New Element: ")

    else:
        print("bespokify_this_table malfed up")

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


def list_table_choices(table_chosen: dict) -> list:
    """
    uses list comprehension to return a list of the table values
    excluding table dict control and data info.
    """

    if type(table_chosen) == dict:
        choices = [
            value
            for key, value in table_chosen.items()
            if value not in ["Choose", "Extra Roll", "Secondary"]
            and key not in ["name", "die_roll", "title"]
        ]
    elif type(table_chosen) == list:
        choices = table_chosen

    else:
        print("bad table type in list table choices")

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
        print("\n*** ERROR: no files found")
        quit()

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





def clear_console():
    """
    Clears the console on different OSs
    """
    os.system("cls" if os.name == "nt" else "clear")

def say_goodnight_marsha():
    clear_console()
    print("".center(31, "*"))
    print("* Thank you for your service. *")
    print("".center(31, "*"))
    print()
    quit()
