import math
import secrets

import please
import table
import vocation
import a_persona_record

import outputs
import mutations
from mutations import *


def anthro_workflow() -> None: 
    """
    player persona vs referee persona vs updating existing persona
    """
    # clearance for Clarence
    please.clear_console()

    workflow_function_map = {
        "AAA#Fresh Anthro (new player)":fresh_anthro,
        "Bespoke Anthro":bespoke_anthro,
        "Random Anthro":random_anthro,
        "Maintenance":please.do_referee_maintenance
    }
    choice_comment = "Choose anthro workflow? "
    choices= list(workflow_function_map.keys())
    anthro_record_type = please.choose_this(choices, choice_comment)

    if anthro_record_type in workflow_function_map:
        workflow_function_map[anthro_record_type]()


####################################
# FRESH ANTHRO FUNCTIONS
####################################

def anthro_attributes_fresh(persona_record:dict):
    """
    hit points max (HPM) depends on CON and is generated separately
    """

    fresh_dict = {
        key: value["dice"]
        for (key, value) in table.suggested_anthro_attribute_ranges.items()
        if key != "HPM" and key != "EXPS"
    }

    for attribute in fresh_dict:
        die_roll = please.roll_this(fresh_dict[attribute])
        setattr(persona_record, attribute, die_roll)

    return


def anthro_hit_points_fresh(object):
    """
    calculates HPM based on CON
    prints out with list of other fresh attributes from anthro_attributes_fresh
    """
    con = object.CON
    dice = math.ceil(con / 2)
    die_roll = str(dice) + "d8+" + str(con)
    hpm = please.roll_this(die_roll)

    object.HPM = hpm

    return


def adjust_mstr_by_int(object):
    """
    alters MSTR based on persona's fresh INT
    """

    intel = object.INT
    old_mstr = object.MSTR
    mstr_adjustment = table.mstr_adjusted_by_int[intel]
    mstr = old_mstr + mstr_adjustment
    mstr = mstr if mstr > 0 else 1  # prevent death by MSTR
    object.MSTR = mstr

    return


def list_eligible_anthro_types(object):
    """
    makes list of eligible anthro types based on attributes
    """
    anthro_type_choices = []

    for anthro_type in table.anthro_type_attribute_requirements:
        anthro_type_flag = True

        for attribute_name in table.anthro_type_attribute_requirements[anthro_type]:
            persona_attribute_value = getattr(object, attribute_name)
            required_attribute_value = table.anthro_type_attribute_requirements[
                anthro_type
            ][attribute_name]
            if persona_attribute_value < required_attribute_value:
                anthro_type_flag = False
        if anthro_type_flag:
            anthro_type_choices.append(anthro_type)

    return anthro_type_choices


def anthro_type_fresh(object):
    """
    pick from the eligible anthro types
    """
    choices = list_eligible_anthro_types(object)
    choice_comment = "Which anthro type do you want?"
    type_choice = please.choose_this(choices, choice_comment)
    object.FAMILY_TYPE= type_choice

    return


def anthro_sub_type_selection(object):
    """
    allow user to select an anthro sub type by choice, random or bespoke
    """

    choices = ["Generalis (none)", "Choose", "Bespoke", "Random"]
    choice_comment = "Choose method to select anthro SUB-type?"
    method_of_selection = please.choose_this(choices, choice_comment)

    if method_of_selection == "Choose":
        choices = table.anthro_sub_types[object.Anthro_Type]
        list_comment = "Choose your anthro subtype: "
        sub_type = please.choose_this(choices, list_comment)

    elif method_of_selection == "Bespoke":
        sub_type = input(f"Carefully input subtype for the {object.Anthro_Type}: ")

    elif method_of_selection == "Random":
        die_type = len(table.anthro_sub_types[object.Anthro_Type])
        rando = secrets.randbelow(die_type)
        sub_type = table.anthro_sub_types[object.Anthro_Type][rando]

    elif method_of_selection == "Generalis (none)":
        sub_type = "Generalis"

    object.Anthro_Sub_Type = sub_type
    # print(f"Persona is a {object.Anthro_Type} {object.Anthro_Sub_Type}")
    return


def adjust_attributes_by_anthro_type(object):
    """
    each anthro type has a set of attributes that are adjusted by the anthro type
    """

    anthro_type = object.Anthro_Type
    MSTR_printed = False
    # print(f"\nAdjusting attributes for {anthro_type}")

    for attribute in table.attribute_adjustment_by_anthro_type[anthro_type]:
        if (
            (attribute != "CON")
            and (attribute != "INT")
            and not (attribute == "MSTR" and MSTR_printed)
        ):
            old_attribute = getattr(object, attribute)
            adjustment = table.attribute_adjustment_by_anthro_type[anthro_type][
                attribute
            ]
            new_attribute = old_attribute + adjustment
            # print(f"{attribute} adjustment is {old_attribute} -> {new_attribute}")
            setattr(object, attribute, new_attribute)

        elif attribute == "CON":
            old_attribute = getattr(object, attribute)
            adjustment = table.attribute_adjustment_by_anthro_type[anthro_type][
                attribute
            ]
            new_attribute = old_attribute + adjustment
            # print(f"{attribute} adjustment is {old_attribute} -> {new_attribute}")
            setattr(object, attribute, new_attribute)

            if adjustment > 0:
                old_HPM = object.HPM
                adjustment_HPM = please.roll_this(
                    "1d8+1"
                )  # 1d8+1 based on only possible increase for anthro CON
                object.HPM = old_HPM + adjustment_HPM
                # print("CON alters HPM")
                # print(f"HPM adjustment is {old_HPM} -> {object.HPM}")

        elif attribute == "INT":
            old_attribute = getattr(object, attribute)
            adjustment = table.attribute_adjustment_by_anthro_type[anthro_type][
                attribute
            ]
            new_attribute = old_attribute + adjustment
            # print(f"{attribute} adjustment is {old_attribute} -> {new_attribute}")
            setattr(object, attribute, new_attribute)

            if adjustment > 0:
                old_MSTR = object.MSTR
                old_MSTR_adjustment = table.mstr_adjusted_by_int[old_attribute]
                new_mstr_adjustment = (
                    table.mstr_adjusted_by_int[new_attribute] - old_MSTR_adjustment
                )
                object.MSTR = old_MSTR + new_mstr_adjustment
                # print("INT may alter MSTR")
                # print(f"MSTR adjustment is {old_MSTR} -> {object.MSTR}")
                MSTR_printed = True

    return


def anthro_size_fresh(object):

    anthro_type = object.Anthro_Type

    # choose anthro size
    choices = ["Smaller", "Larger"]
    choice_comment = "Pick an anthro size."
    anthro_size_choice = please.choose_this(choices, choice_comment)

    if anthro_size_choice == "Smaller":
        size_table_chosen = table.small_anthro_sizes

    else:
        size_table_chosen = table.large_anthro_sizes

    base = size_table_chosen[anthro_type]["Base"]
    Hite = please.roll_this(size_table_chosen[anthro_type]["Hite"])
    Wate = math.ceil((Hite / base) * size_table_chosen[anthro_type]["Wate"])

    object.Hite = Hite
    object.Wate = Wate
    object.Anthro_Size = "Medium"  # correct anthro size to actual size of medium
    return


def anthro_size_rando(object):

    anthro_type = object.Anthro_Type

    # choose anthro size
    anthro_size_choice = secrets.choice(["Smaller", "Larger"])

    if anthro_size_choice == "Smaller":
        size_table_chosen = table.small_anthro_sizes

    else:
        size_table_chosen = table.large_anthro_sizes

    base = size_table_chosen[anthro_type]["Base"]
    Hite = please.roll_this(size_table_chosen[anthro_type]["Hite"])
    Wate = math.ceil((Hite / base) * size_table_chosen[anthro_type]["Wate"])

    object.Hite = Hite
    object.Wate = Wate
    object.Anthro_Size = "Medium"  # correct anthro size to actual size of medium
    return


def determine_anthro_wate_allowance(object):
    """
    PSTR determines wate allowance
    """
    object.WA = table.wate_allowance_and_PSTR[object.PSTR]
    # print(f"Persona's wate allowance is {object.WA} kgs")

    return


def anthro_move(object):
    """
    dexterity determines movement rate
    """

    if "Move" in object.__dict__:
        pass
        # print(f"Persona's move is {object.Move}")
    else:
        object.Move = table.anthro_movement_rate_and_DEX[object.DEX]
        # print(f"Persona's move is {object.Move} h/u")
    return


def anthro_base_AR(object):
    """
    dexterity determines armour rating for anthros
    """
    object.AR = 500 + (6 * object.DEX)
    # print(f"Persona's base armour rating is {object.AR}")

    return


def anthro_age_fresh(object):
    """
    generates the persona age at level one start
    """
    AnthroType = object.Anthro_Type
    object.Age_Cat = "Young"
    object.Age = please.roll_this(table.anthro_starting_ages[AnthroType])

    return


def anthro_mutations_fresh(object):
    """
    check for mutations based on player desire and anthro type
    """

    # determine the chance of mutations based on anthro type
    anthro_type = object.Anthro_Type
    mentchance = table.anthro_type_mutation_chance[anthro_type]["mentchance"]
    physchance = table.anthro_type_mutation_chance[anthro_type]["physchance"]

    # create the mutations dict
    object.Mutations = {}

    # mutation chances increase if desired
    mutate_yes = please.say_yes_to("Do you want to mutate?")

    if mutate_yes and anthro_type != "Humanoid":
        mentchance = mentchance * 2
        physchance = physchance * 2

    elif mutate_yes and anthro_type == "Humanoid":
        mentchance = 100
        physchance = 100

    ##### Mental Mutation chance, number and generation
    # percent chance mentchance
    if please.do_1d100_check(mentchance):
        mutation_number = please.roll_this(
            table.anthro_type_mutation_chance[anthro_type]["mentnumber"]
        )

        fresh_amount = 0
        while fresh_amount < mutation_number:
            working_mutation = please.get_table_result(table.mental_mutation_random)[1](
                object
            )
            print(working_mutation)
            fresh_amount += 1

            if working_mutation.kind == "defect" and object.FAMILY_TYPE== "Purestrain":
                print("\nYou are a purestrain, you cannot have a defect mutation.")
                fresh_amount -= 2
                object.Mutations.pop(working_mutation.name)

            if working_mutation.kind == "defect" and object.FAMILY_TYPE!= "Purestrain":
                if please.say_yes_to("A Defect DOES NOT count as a mutation? "):
                    fresh_amount -= 1

    else:
        print(f"Persona has no mental mutations.")

    ##### Physical Mutation chance, number and generation
    # percent chance physchance
    if please.do_1d100_check(physchance):
        mutation_number = please.roll_this(
            table.anthro_type_mutation_chance[anthro_type]["physnumber"]
        )

        fresh_amount = 0
        # number of mutations is random based on anthro type
        while fresh_amount < mutation_number:
            working_mutation = please.get_table_result(table.physical_mutation_random)[
                1
            ](object)
            print(working_mutation)
            fresh_amount += 1

            if working_mutation.kind == "defect" and object.FAMILY_TYPE== "Purestrain":
                print("\nYou are a purestrain, you cannot have a defect mutation.")
                fresh_amount -= 2
                object.Mutations.pop(working_mutation.name)

            if working_mutation.kind == "defect" and object.FAMILY_TYPE!= "Purestrain":
                if please.say_yes_to("A Defect DOES NOT count as a mutation? "):
                    fresh_amount -= 2

    else:
        print(f"Persona has no physical mutations.")


def anthro_mutations_rando(object):
    """
    check for mutations based on player desire and anthro type
    """

    # determine the chance of mutations based on anthro type
    anthro_type = object.Anthro_Type
    mentchance = table.anthro_type_mutation_chance[anthro_type]["mentchance"] * 2
    physchance = table.anthro_type_mutation_chance[anthro_type]["physchance"] * 2

    # create the mutations dict
    object.Mutations = {}

    if anthro_type == "Humanoid":
        mentchance = 100
        physchance = 100

    ##### Mental Mutation chance, number and generation
    # percent chance mentchance
    if please.do_1d100_check(mentchance):
        mutation_number = please.roll_this(
            table.anthro_type_mutation_chance[anthro_type]["mentnumber"]
        )

        fresh_amount = 0
        while fresh_amount < mutation_number:
            working_mutation = please.get_table_result(table.mental_mutation_random)[1](
                object
            )
            fresh_amount += 1

            ### defects do not count as mutations
            if working_mutation.kind == "defect":
                print("\nYou are a purestrain, you cannot have a defect mutation.")
                fresh_amount -= 1

    else:
        print(f"blerp bloop blap.")

    ##### Physical Mutation chance, number and generation
    # percent chance physchance
    if please.do_1d100_check(physchance):
        mutation_number = please.roll_this(
            table.anthro_type_mutation_chance[anthro_type]["physnumber"]
        )

        fresh_amount = 0
        # number of mutations is random based on anthro type
        while fresh_amount < mutation_number:
            working_mutation = please.get_table_result(table.physical_mutation_random)[
                1
            ](object)
            fresh_amount += 1

            if working_mutation.kind == "defect":
                print("\nYou are a purestrain, you cannot have a defect mutation.")
                fresh_amount -= 1

    else:
        print(f"glib glorp glap.")


def anthro_vocations_fresh(object):
    choices = vocation.list_eligible_vocations(object)
    choice_comment = "Which VOCATION do you want?"
    type_choice = please.choose_this(choices, choice_comment)
    object.Vocation = type_choice

    return


def anthro_persona_name_fresh(object):
    """
    I know it is only only one line, but I want to make build_show work
    """
    persona_name = input("\nPlease input a PERSONA NAME for your anthro? ")

    if persona_name == "quit" or persona_name == "Quit":
        if please.say_yes_to("Do you want to QUIT the program"):
            print("\n*** program terminated")
            exit()

    object.Persona_Name = persona_name

    return


####################################
# BESPOKE ANTHRO FUNCTIONS
####################################


def bespoke_anthro_attribute_ranges(object):
    """
    input specific desired attribute scores
    rolled or by hand
    """

    print("Manually inputting bespoke attributes")

    if object.FAMILY == "Anthro":
        ranges_table = table.suggested_anthro_attribute_ranges

    elif object.FAMILY == "Alien":
        ranges_table = table.alien_attribute_ranges

    for attribute, attribute_data in ranges_table.items():
        attribute_value = "new attribute value"
        break_flag = False

        while (
            isinstance(attribute_value, str)
            or int(attribute_value) < attribute_data["minimum"]
            or int(attribute_value) > attribute_data["start_max"]
        ):

            # print(f'\nInputting {attribute_data["long_name"]}:')
            suggested = getattr(object, attribute)

            if please.say_yes_to(
                f'Accept {attribute} of {suggested} from {attribute_data["dice"]}?'
            ):
                attribute_value = suggested
                break_flag = True

            else:
                attribute_value = input(f"Enter new {attribute_data['long_name']}: ")
                break_flag = True

            attribute_value = int(attribute_value)

            if attribute_value > attribute_data["start_max"]:

                if please.say_yes_to(
                    f"{attribute_value} seems high for {attribute}. Is this correct?"
                ):
                    break_flag = True
                    break  # do I need this break? not sure

            if break_flag:
                break

            if attribute_value < attribute_data["minimum"]:
                print(
                    f" {attribute_value} for {attribute}. Is not compatible with existence.\n Correcting to minimum of {attribute_data['minimum']}"
                )
                attribute_value = attribute_data["minimum"]
                break

        setattr(object, attribute, attribute_value)

    return


def anthro_descriptive_attributes(object):
    """
    referee persona attribute shifts based on descriptive words
    """

    if object.FAMILY == "Anthro":
        descript_table = table.anthro_descriptive_attributes_list
    elif object.FAMILY == "Alien":
        descript_table = table.alien_descriptive_attributes_list

    altering_descriptor = "Start"
    while altering_descriptor != "Exit":
        choices = [key for key in descript_table]
        choice_comment = "What attribute descriptor do you want?"
        altering_descriptor = please.choose_this(choices, choice_comment)

        # Slow, Fast, Delicate, Resilient and QUIT need special handling
        if altering_descriptor == "Slow":
            # slow decreases object.Move
            attribute_altered = "Move"
            die_roll = please.roll_this("1d3") - 1
            setattr(object, "Move", die_roll)

        elif altering_descriptor == "Fast":
            # fast increases object.Move
            attribute_altered = "Move"
            anthro_move(object)
            old_move = getattr(object, "Move")
            die_roll = please.roll_this("1d3") + 8
            die_roll = old_move if die_roll < old_move else die_roll
            setattr(object, "Move", die_roll)

        elif altering_descriptor == "Delicate":
            # delicate decreases object.HPM
            attribute_altered = "HPM"
            die_roll = please.roll_this("2d6")
            setattr(object, "HPM", die_roll)

        elif altering_descriptor == "Resilient":
            # resilient increases object.HPM
            attribute_altered = "HPM"
            old_HPM = getattr(object, "HPM")
            die_roll = please.roll_this("1d30") + 70
            die_roll = old_HPM if die_roll < old_HPM else die_roll
            setattr(object, "HPM", die_roll)

        elif altering_descriptor == "Exit":
            return

        else:
            # typical randomly generated altering_descriptor
            die_roll = please.roll_this(
                table.anthro_descriptive_attributes_list[altering_descriptor][1]
            )
            attribute_altered = table.anthro_descriptive_attributes_list[
                altering_descriptor
            ][0]
            setattr(object, attribute_altered, die_roll)

        # printout down_shift and it's effect
        print(
            f"You made the persona {altering_descriptor}, {attribute_altered} is now {die_roll}"
        )

    return


def anthro_attributes_bespoke(object):

    methods = ["Random", "Bespoke", "Descriptive"]
    choice_comment = "Choose a method for ATTRIBUTES?"
    choice = please.choose_this(methods, choice_comment)

    if choice == "Bespoke":
        anthro_attributes_fresh(object)
        anthro_hit_points_fresh(object)
        bespoke_anthro_attribute_ranges(object)
        anthro_move(object)
        anthro_base_AR(object)
        determine_anthro_wate_allowance(object)

    elif choice == "Random":
        anthro_attributes_fresh(object)
        anthro_hit_points_fresh(object)
        anthro_move(object)
        anthro_base_AR(object)
        determine_anthro_wate_allowance(object)

    elif choice == "Descriptive":
        anthro_attributes_fresh(object)
        anthro_hit_points_fresh(object)
        anthro_move(object)
        anthro_descriptive_attributes(object)
        anthro_base_AR(object)
        determine_anthro_wate_allowance(object)
    else:
        print("error in bespoke_anthro_attribute methods")

    return


def improve_attributes_by_anthro_type(object):
    """
    bestow improved attributes based on anthro type
    """
    anthro_type = object.Anthro_Type
    if anthro_type not in table.attribute_improve_by_anthro_type:
        print(f"No bespoke attributes for {anthro_type}")
        return

    attribute_to_adjust = table.attribute_improve_by_anthro_type[anthro_type][0]

    old_attribute = getattr(object, attribute_to_adjust)
    die_roll = please.roll_this(table.attribute_improve_by_anthro_type[anthro_type][1])
    die_roll = old_attribute if die_roll < old_attribute else die_roll
    setattr(object, attribute_to_adjust, die_roll)
    return


def anthro_type_bespoke(object):

    ### choose RP anthro type
    choices = ["Attribute Determined", "Bespoke", "Random"]
    choice_comment = "Choose a method for ANTHRO TYPE?"
    method_type_selection = please.choose_this(choices, choice_comment)

    all_anthro_types = [key for key in table.anthro_sub_types.keys()]

    if method_type_selection == "Attribute Determined":
        type_options = list_eligible_anthro_types(object)
        comment = "Which ANTHRO TYPE do you want?"
        type_choice = please.choose_this(type_options, comment)
        object.FAMILY_TYPE= type_choice

    elif method_type_selection == "Bespoke":
        type_options = all_anthro_types
        comment = "Which anthro type do you want?"
        type_choice = please.choose_this(type_options, comment)
        object.FAMILY_TYPE= type_choice

    elif method_type_selection == "Random":
        type_choice = all_anthro_types[
            (please.roll_this("1d" + str(len(all_anthro_types))) - 1)
        ]  ### -1 to avoid indexing error
        object.FAMILY_TYPE= type_choice

    else:
        print("\nYou have not selected a valid anthro type selection method")

    if please.say_yes_to("Do you want to adjust attributes by anthro type?"):
        improve_attributes_by_anthro_type(object)

    return


def anthro_mutations_bespoke(object):

    ### determine RP anthro mutations
    choices = ["Anthro Type Determined", "Bespoke", "Random"]
    choice_comment = "What selection method do you want for MUTATIONS?"
    method_type_selection = please.choose_this(choices, choice_comment)

    if method_type_selection == "Anthro Type Determined":
        anthro_mutations_fresh(object)

    elif method_type_selection == "Bespoke":
        mutations.pick_bespoke_mutation(object)

    elif method_type_selection == "Random":
        plan_desired = "plan 9"
        while plan_desired != "Exit":
            option_list = ["Get a mutation", "Exit"]
            list_comment = "Would you like to: "
            plan_desired = please.choose_this(option_list, list_comment)

            if plan_desired == "Get a Mutation":
                mutations.single_random_mutation(object)
        return
    return


def anthro_vocation_bespoke(object: dict) -> None:
    """
    determine bespoke vocation type
    """

    ### choose RP anthro vocation
    choices = ["Attribute Determined", "Bespoke", "Random"]
    choice_comment = "Choose a method for VOCATION ?"
    method_type_selection = please.choose_this(choices, choice_comment)

    # create list of all vocations
    all_vocations = [key for key in table.attributes_improve_by_vocation.keys()]

    if method_type_selection == "Attribute Determined":
        anthro_vocations_fresh(object)

    elif method_type_selection == "Bespoke":
        choices = all_vocations
        choice_comment = "Please choose a VOCATION"
        object.Vocation = please.choose_this(choices, choice_comment)

    elif method_type_selection == "Random":
        object.Vocation = secrets.choice(all_vocations)

    else:
        print("\nYou have not selected a valid anthro vocation type selection method")


def choose_anthro_age_category(object):
    """
    allow user to select an anthro age category
    """
    option_list = ["Child", "Adolescent", "Adult", "Elder", "Aged"]
    list_comment = "Choose a bespoke age range."
    Bespoke_Age_Range = please.choose_this(option_list, list_comment)

    anthro_type = object.Anthro_Type
    numerical_age_range = option_list.index(Bespoke_Age_Range)

    die_roll = table.anthro_ages_by_category_and_type[anthro_type][numerical_age_range]
    age_years = please.roll_this(die_roll)

    object.Age_Cat = Bespoke_Age_Range
    object.Age = age_years
    print(f"Persona is {object.Age_Cat} and {object.Age} years old.")

    return


def random_anthro_age_category(object):
    """
    randomly generate age category and actual age
    """

    option_list = ["Child", "Adolescent", "Adult", "Elder", "Aged"]
    random_age_range = please.get_table_result(table.anthro_random_age_category)

    anthro_type = object.Anthro_Type
    numerical_age_range = option_list.index(random_age_range)

    die_roll = table.anthro_ages_by_category_and_type[anthro_type][numerical_age_range]
    age_years = please.roll_this(die_roll)

    object.Age_Cat = random_age_range
    object.Age = age_years
    print(f"Persona is {object.Age_Cat} and {object.Age} years old.")

    return


def role_play_RP_arc():
    """
    return referee person arc in relation to expedition now
    """
    past = please.get_table_result(table.role_play_RP_arc_past)
    present = please.get_table_result(table.role_play_RP_arc_present)
    goal = please.get_table_result(table.role_play_RP_arc_goal)

    return f"Past: {past}, Present: {present}, Goal: {goal}."


def role_play_RP_beliefs(object: dict) -> str:
    """
    add religion, philosophy, politics or not
    """
    complexity = please.get_table_result(table.role_play_RP_belief_complexity)

    if complexity[0]:
        religious = f"Religion: {please.get_table_result(table.role_play_RP_religion)}"
    else:
        religious = f"Religion: None"

    if complexity[1]:
        philosophy = (
            f"Philosophy: {please.get_table_result(table.role_play_RP_philosophy)}"
        )
    else:
        philosophy = f"Philosophy: None"

    if complexity[2]:
        politics = f"Politics: {please.get_table_result(table.role_play_RP_politics)}"
    else:
        politics = f"Politics: None"

    return f"Beliefs: {religious}, {philosophy}, {politics}."


def role_play_RP_personality():
    """
    personality descriptor
    introvert, extrovert, insane
    """

    personality = please.get_table_result(table.extroverted_personality)

    if personality == "Introverted":
        personality = (
            please.get_table_result(table.introverted_personality) + ", Introverted"
        )

    elif personality == "Insane":
        personality = please.get_table_result(table.insane_personality) + ", Insane"

    else:
        personality = personality + ", Extroverted"

    return personality


def build_RP_role_play(object):
    """
    create all the fun role_play elements for a referee persona
    """

    print("Building the role playing components of the referee persona")
    object.RP_Fun = []
    object.RP_Fun.append(f"Arc: {role_play_RP_arc()}")
    object.RP_Fun.append(
        f"Dress: {please.get_table_result(table.referee_persona_dress)} Hygiene: {please.get_table_result(table.referee_persona_hygiene)} Odor: {please.get_table_result(table.alien_biology_aroma)}"
    )
    object.RP_Fun.append(
        f"Personality: {role_play_RP_personality()} Voice: {please.get_table_result(table.laban)} Move: { please.get_table_result(table.laban)} "
    )
    object.RP_Fun.append(f"{role_play_RP_beliefs(object)}")

    return


#####################################
# build a FRESH anthro persona
#####################################

def fresh_anthro():
    """
    builds the anthro object for a fresh persona
    """

    # clearance for Clarence
    please.clear_console()
    print("\nYou are generating a fresh ANTHRO PERSONA")

    ### set up the object for Anthro persona
    fresh = table.PersonaRecord()

    ### get mundane terran name of the player
    fresh.Player_Name = input("\nPlease input your MUNDANE TERRAN NAME: ")

    ### build list of functions
    anthro_attributes_fresh(fresh)
    anthro_hit_points_fresh(fresh)
    adjust_mstr_by_int(fresh)
    anthro_type_fresh(fresh)
    anthro_sub_type_selection(fresh)
    adjust_attributes_by_anthro_type(fresh)
    anthro_size_fresh(fresh)
    anthro_move(fresh)
    anthro_base_AR(fresh)
    determine_anthro_wate_allowance(fresh)
    anthro_age_fresh(fresh)
    anthro_mutations_fresh(fresh)
    anthro_vocations_fresh(fresh)
    vocation.set_up_first_time(fresh)
    outputs.anthro_review(fresh)
    anthro_persona_name_fresh(fresh)
    outputs.anthro_review(fresh)
    please.assign_id_and_file_name(fresh)
    please.record_storage(fresh)
    return


#####################################
# build a BESPOKE anthro persona
#####################################

def bespoke_anthro():
    """
    building a bespoke anthro persona typically a referee persona
    """

    # clearance for Clarence
    please.clear_console()
    print("\nYou are generating a bespoke ANTHRO PERSONA.")

    ### set up the object for Anthro persona
    bespoke = table.PersonaRecord()
    bespoke.RP = True if please.say_yes_to("Is this a referee persona? ") else False

    ### get mundane terran name of the player
    bespoke.Player_Name = input("\nPlease input your MUNDANE TERRAN NAME: ")

    ### build list of functions
    anthro_attributes_bespoke(bespoke)
    anthro_type_bespoke(bespoke)
    anthro_sub_type_selection(bespoke)
    anthro_size_fresh(bespoke)
    vocation.exps_level_picker(bespoke)
    anthro_mutations_bespoke(bespoke)
    anthro_vocation_bespoke(bespoke)
    vocation.set_up_first_time(bespoke)
    bespoke.EXPS = (
        42 if bespoke.Level == 1 else vocation.convert_levels_to_exps(bespoke)
    )

    ### add additional interests and skills (gifts are dynamically anthrod)
    if bespoke.Level > 1:
        print(f"You have {bespoke.Level - 1} extra interest(s) and skill(s) to add.")
        bespoke.Interests.extend(
            vocation.update_interests(bespoke, (bespoke.Level - 1))
        )
        bespoke.Skills.extend(vocation.update_skills(bespoke, (bespoke.Level - 1)))

    ### adjust RP attributes by vocation
    if please.say_yes_to("Do you want ADJUST RP attributes by VOCATION? (recommended)"):
        vocation.bespoke_anthro_attributes_by_vocation(bespoke)

    ### generate RP EXPS points
    bespoke.EXPS = (
        42 if bespoke.Level == 1 else vocation.convert_levels_to_exps(bespoke)
    )

    ### determine RP Age
    option_list = ["Bespoke", "Random"]
    list_comment = "Choose how to determine persona age."
    Method_Age_Method = please.choose_this(option_list, list_comment)

    if Method_Age_Method == "Bespoke":
        choose_anthro_age_category(bespoke)
    else:
        random_anthro_age_category(bespoke)

    ### anthro AR if not already there
    hack = 42 if hasattr(bespoke, "AR") else anthro_base_AR(bespoke)

    ### anthro  Move if not already there
    hack = 42 if hasattr(bespoke, "Move") else anthro_base_AR(bespoke)

    ###
    determine_anthro_wate_allowance(bespoke)

    ### impact of level on:
    # attributes
    # mutations
    # vocation gifts, interests, and skills
    # combat table
    # EXPS amount

    ### generate RP Fun
    build_RP_role_play(bespoke)

    ### generate RP storage data including temporary name
    bespoke.Persona_Name = input("\nPlease input a name for your anthro Persona? ")
    please.assign_id_and_file_name(bespoke)
    outputs.anthro_review(bespoke)

    # rename check
    if please.say_yes_to("Do you want to change the RP PERSONA NAME? "):
        bespoke.Persona_Name = input("Please re-name the RP: ")

    ### ultimage RP disposition
    please.record_storage(bespoke)
    return


#####################################
# build a RANDOM anthro persona
#####################################

def random_anthro():
    """
    building a RANDOM anthro persona, typically a referee persona
    """

    # clearance for Clarence
    please.clear_console()
    print("\nYou are generating a RANDOM ANTHRO PERSONA.")

    ### set up the object for Anthro persona
    rando = table.PersonaRecord()
    rando.RP = True if please.say_yes_to("Is this a referee persona? ") else False
    rando.Otto = True

    ### get mundane terran name of the player
    rando.Player_Name = input("\nPlease input your MUNDANE TERRAN NAME: ")

    ### build list of functions
    anthro_attributes_fresh(rando)
    anthro_hit_points_fresh(rando)
    adjust_mstr_by_int(rando)
    rando.Anthro_Type = secrets.choice(
        [x for x in table.anthro_ages_by_category_and_type]
    )
    rando.Anthro_Sub_Type = secrets.choice(table.anthro_sub_types[rando.Anthro_Type])

    adjust_attributes_by_anthro_type(rando)
    anthro_size_rando(rando)
    anthro_move(rando)
    anthro_base_AR(rando)
    determine_anthro_wate_allowance(rando)
    anthro_mutations_rando(rando)
    rando.Vocation = secrets.choice([x for x in table.vocations_gifts_pivot])
    vocation.set_up_first_time(rando)
    vocation.random_exps_level(rando)
    rando.EXPS = vocation.convert_levels_to_exps(rando)

    ### add additional interests and skills
    if rando.Level > 1:
        rando.Interests.extend(vocation.update_interests(rando, (rando.Level - 1)))
        rando.Skills.extend(vocation.update_skills(rando, (rando.Level - 1)))

    vocation.bespoke_anthro_attributes_by_vocation(rando)
    random_anthro_age_category(rando)
    determine_anthro_wate_allowance(rando)

    if rando.RP:
        build_RP_role_play(rando)

    ### generate RP storage data including temporary name
    rando.Persona_Name = f"{rando.Player_Name} Mac{rando.Player_Name}"
    please.assign_id_and_file_name(rando)
    outputs.anthro_review(rando)

    ### ultimage persona disposition
    please.record_storage(rando)
    return
