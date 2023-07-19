import math
import secrets

import please
import table
import vocation
import core

import outputs
import mutations

def anthro_workflow() -> None: 
    """
    player persona vs referee persona vs updating existing persona
    """
    # clearance for Clarence
    please.clear_console()

    workflow_function_map = {
        "Fresh Anthro (new player)":fresh_anthro,
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

def adjust_mstr_by_int(mind_adjusting:table.PersonaRecord) -> table.PersonaRecord:
    """
    alters MSTR based on persona's INT
    """
    old_mstr = mind_adjusting.MSTR
    mstr_adjustment = table.mstr_adjusted_by_int[mind_adjusting.INT]
    mstr = (old_mstr + mstr_adjustment) if (old_mstr + mstr_adjustment) > 0 else 1
    mind_adjusting.MSTR = mstr

    return mind_adjusting # altered by side effect

def list_eligible_anthro_types(making_anthro_list) -> list:
    """
    returns a list of eligible anthro types based on attributes
    """
    anthro_type_choices = []

    for anthro_type in table.anthro_type_attribute_requirements:
        anthro_type_flag = True

        for attribute_name in table.anthro_type_attribute_requirements[anthro_type]:
            persona_attribute_value = getattr(making_anthro_list, attribute_name)
            required_attribute_value = table.anthro_type_attribute_requirements[
                anthro_type
            ][attribute_name]
            if persona_attribute_value < required_attribute_value:
                anthro_type_flag = False
        if anthro_type_flag:
            anthro_type_choices.append(anthro_type)

    return anthro_type_choices # altered by side effect

def anthro_type_fresh(choosing_anthro_type: table.PersonaRecord) -> table.PersonaRecord:
    """
    pick from the eligible anthro types
    """
    choices = list_eligible_anthro_types(choosing_anthro_type)
    choice_comment = "Please choose an anthro type? "
    type_choice = please.choose_this(choices, choice_comment)
    choosing_anthro_type.FAMILY_TYPE= type_choice

    return choosing_anthro_type # altered by side effect

def anthro_sub_type_selection(selecting_sub_type: table.PersonaRecord) -> table.PersonaRecord:
    """
    select the sub_type for the anthro type
    """

    choices = ["Generalis (none)", "Choose", "Bespoke", "Random"]
    choice_comment = f"How would you like to pick your {selecting_sub_type.FAMILY_TYPE} subtype? "
    method_of_selection = please.choose_this(choices, choice_comment)

    if method_of_selection == "Choose":
        choices = table.anthro_sub_types[selecting_sub_type.FAMILY_TYPE]
        list_comment = f"Choose your {selecting_sub_type.FAMILY_TYPE} subtype: "
        sub_type = please.choose_this(choices, list_comment)

    elif method_of_selection == "Bespoke":
        sub_type = input(f"Carefully input subtype for the {selecting_sub_type.FAMILY_TYPE}: ")

    elif method_of_selection == "Random":
        die_type = len(table.anthro_sub_types[selecting_sub_type.FAMILY_TYPE])
        rando = secrets.randbelow(die_type)
        sub_type = table.anthro_sub_types[selecting_sub_type.FAMILY_TYPE][rando]

    elif method_of_selection == "Generalis (none)":
        sub_type = "Generalis"

    selecting_sub_type.FAMILY_SUB = sub_type

    return selecting_sub_type # altered by side effect

def adjust_attributes_by_anthro_type(anthro_type_attributes_adjust: table.PersonaRecord) -> table.PersonaRecord:
    """
    adjust the persona's attributes according to the persona type
    """
    anthro_type = anthro_type_attributes_adjust.FAMILY_TYPE
    anthro_line = table.attribute_adjustment_by_anthro_type[anthro_type]
    changes_string = {attribute : change for attribute, change in anthro_line.items() if change != 0}

    for attribute,change in changes_string.items():

        # CON special case, adjusts the HPM
        if attribute == "CON":
            anthro_line["HPM"] = please.roll_this(f'1d8+{change}')

        # INT special case, may adjust the MSTR
        elif attribute == "INT":
            old_change = table.mstr_adjusted_by_int[anthro_type_attributes_adjust.INT]
            new_change = table.mstr_adjusted_by_int[anthro_type_attributes_adjust.INT + change]
            new_MSTR = anthro_type_attributes_adjust.MSTR + (new_change - old_change)
            change_MSTR = (new_change - old_change) if (new_MSTR) > 0 else 0
            anthro_line["MSTR"] = change_MSTR

    for attribute,change in anthro_line.items():
        old_attribute = getattr(anthro_type_attributes_adjust, attribute)
        change = 0 if change<0 and not anthro_type_attributes_adjust.RP and attribute != "CHA"else change # protects players from -ve adjustments
        new_attribute = (old_attribute + change)
        new_attribute = 1 if new_attribute < 1 and attribute != "CHA" else new_attribute
        setattr(anthro_type_attributes_adjust, attribute, new_attribute)

    return anthro_type_attributes_adjust # adjusted by side effect

def anthro_hite_wate_calc(size_this:table.PersonaRecord, sizer: str) -> table.PersonaRecord:
    '''calculates hite and wate for persona based on smaller or larger '''
    anthro_type = size_this.FAMILY_TYPE

    size_table_chosen = table.small_anthro_sizes if sizer == "Smaller" else table.large_anthro_sizes
    base = size_table_chosen[anthro_type]["Base"]
    Hite = please.roll_this(size_table_chosen[anthro_type]["Hite"])
    Wate = math.ceil((Hite / base) * size_table_chosen[anthro_type]["Wate"])

    size_this.Hite = Hite
    size_this.Wate = Wate
    size_this.Size_Cat = "Medium"  # correct anthro size to actual size of medium

    return size_this # is modified by side effects

def anthro_size_chooser(choosing_size:table.PersonaRecord) -> table.PersonaRecord:
    '''player chooses a size for her persona'''
    choices = ["Smaller", "Larger"]
    choice_comment = f'Choose the size of your {choosing_size.FAMILY_TYPE}, {choosing_size.FAMILY_SUB}. '
    anthro_size_choice = please.choose_this(choices, choice_comment)
    anthro_hite_wate_calc(choosing_size, anthro_size_choice)

    return choosing_size # is modified by side effects in anthro_hite_wate_calc

def anthro_size_rando(rando_size):
    '''chooses a random size for anthro persona'''
    anthro_size_choice = secrets.choice(["Smaller", "Larger"])
    anthro_hite_wate_calc(rando_size, anthro_size_choice)
    return rando_size # is modified by side effects in anthro_hite_wate_calc

def anthro_age_calc(years_old: table.PersonaRecord, ager: str) -> table.PersonaRecord:
    '''add the anthro age and age_cat to the persona record'''
    anthro_type = years_old.FAMILY_TYPE
    age_categories = [val for val  in table.anthro_random_age_category.values() if val != "1d100"]
    die_roll = table.anthro_ages_by_category_and_type[anthro_type][age_categories.index(ager)]
    age_years = please.roll_this(die_roll)

    years_old.Age_Cat = ager
    years_old.Age = age_years

    return years_old # modified by side effect


def anthro_mutations_rando(randomly_mutating: table.PersonaRecord) -> table.PersonaRecord:
    """
    assigns mutations to persona record by side effect in the mutation class
    """

    # determine the chance of mutations based on anthro type
    anthro_type = randomly_mutating.FAMILY_TYPE
    mentchance = table.anthro_type_mutation_chance[anthro_type]["mentchance"]
    physchance = table.anthro_type_mutation_chance[anthro_type]["physchance"]

    # create the mutations dict
    randomly_mutating.Mutations = {}

    ##### Mental Mutation chance, number and generation
    # percent chance mentchance
    if please.do_1d100_check(mentchance):
        mutation_number = please.roll_this(
            table.anthro_type_mutation_chance[anthro_type]["mentnumber"]
        )

        fresh_amount = 0
        while fresh_amount < mutation_number:
            working_mutation = please.get_table_result(mutations.mental_mutation_random)[1](
                randomly_mutating
            )
            fresh_amount += 1

            ### defects do not count as mutations
            if working_mutation.kind == "defect":
                print("\nYou are a purestrain, you cannot have a defect mutation.")
                fresh_amount -= 1


    ##### Physical Mutation chance, number and generation
    # percent chance physchance
    if please.do_1d100_check(physchance):
        mutation_number = please.roll_this(
            table.anthro_type_mutation_chance[anthro_type]["physnumber"]
        )

        fresh_amount = 0
        # number of mutations is random based on anthro type
        while fresh_amount < mutation_number:
            working_mutation = please.get_table_result(mutations.physical_mutation_random)[
                1
            ](randomly_mutating)
            fresh_amount += 1

            if working_mutation.kind == "defect":
                fresh_amount -= 1

    return randomly_mutating # record is adjusted by side effect in a mutation subclass method


def anthro_vocations_fresh(get_a_job: table.PersonaRecord) -> table.PersonaRecord:
    choices = vocation.list_eligible_vocations(get_a_job)
    choice_comment = "Choose a VOCATION: "
    type_choice = please.choose_this(choices, choice_comment)
    get_a_job.Vocation = type_choice

    return get_a_job # modified by side effect


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

def anthro_attributes_bespoke(attribute_adjusting: table.PersonaRecord) -> table.PersonaRecord:
    '''allows player to adjust attributes of their persona'''

    # creates the attributes to mess with 
    core.initial_attributes(attribute_adjusting)
    core.hit_points_max(attribute_adjusting) 
    adjust_mstr_by_int(attribute_adjusting)
    core.movement_rate(attribute_adjusting)
    core.base_armour_rating(attribute_adjusting)
    core.wate_allowance(attribute_adjusting)

    methods = ["Random", "Manual", "Descriptive"]
    choice_comment = "Choose a method for ATTRIBUTES? "
    choice = please.choose_this(methods, choice_comment)

    if choice == "Manual":
        core.manual_persona_update(attribute_adjusting)

    elif choice == "Random":
        pass

    elif choice == "Descriptive":
        core.descriptive_attributes(attribute_adjusting)

    return attribute_adjusting # is modified by side effect in other functions

def improve_attributes_by_anthro_type(object):
    """
    bestow improved attributes based on anthro type
    """
    anthro_type = object.FAMILY_TYPE
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

def anthro_mutations_bespoke(mutate_RP: table.PersonaRecord) -> table.PersonaRecord:

    ### determine RP anthro mutations
    choices = ["Anthro Type Determined", "Bespoke", "Random"]
    choice_comment = "What selection method do you want for MUTATIONS?"
    method_type_selection = please.choose_this(choices, choice_comment)

    if method_type_selection == "Anthro Type Determined":
        mental_amount, physical_amount = mutations.biologic_mutations_number(mutate_RP)
        mutations.mutation_assignment(mutate_RP,mental_amount, physical_amount,"Any")

    elif method_type_selection == "Bespoke":
        mutations.pick_bespoke_mutation(mutate_RP)

    # todo exit get's sorted because choose this sorts it
    elif method_type_selection == "Random":
        plan_desired = "plan 9"
        while plan_desired != "Exit":
            option_list = ["Get a mutation", "Exit"]
            list_comment = "Would you like to: "
            plan_desired = please.choose_this(option_list, list_comment)

            if plan_desired == "Get a Mutation":
                mutations.single_random_mutation(object)
        return
    return mutate_RP # altered by side effect at functions outside this function

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

def anthro_choose_age_cat(years_old: table.PersonaRecord) -> table.PersonaRecord:
    """
    allow user to select an anthro age category
    """
    option_list = ["Child", "Adolescent", "Adult", "Elder", "Aged"]
    list_comment = "Choose a bespoke age range."
    age_cat = please.choose_this(option_list, list_comment)

    anthro_age_calc(years_old, age_cat)
    return

def random_anthro_age_category(years_old: table.PersonaRecord) -> table.PersonaRecord:
    """
    randomly generate age category and actual age
    """
    random_age_range = please.get_table_result(table.anthro_random_age_category)
    anthro_age_calc(years_old,random_age_range)

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
# choices within the context of rolls
#####################################

def fresh_anthro() -> table.PersonaRecord:
    """
    builds the anthro record for a fresh persona
    """

    please.clear_console()
    print("\nYou are generating a fresh ANTHRO PERSONA")

    ### set up the object for Anthro persona
    fresh = table.PersonaRecord()


    ### get mundane terran name of the player
    # fix still not screening input and choice properly
    #name_safe = please.input_this(f'\nPlease input your MUNDANE TERRAN NAME: ')
    #fresh.Player_Name = please.choose_this(name_safe,"Are you happy with your name? ")
    fresh.Player_Name = please.input_this(f'\nPlease input your MUNDANE TERRAN NAME: ')


    core.initial_attributes(fresh)
    core.hit_points_max(fresh)
    adjust_mstr_by_int(fresh)
    anthro_type_fresh(fresh)
    anthro_sub_type_selection(fresh)
    adjust_attributes_by_anthro_type(fresh)
    anthro_size_chooser(fresh)
    core.movement_rate(fresh)
    core.base_armour_rating(fresh)
    core.wate_allowance(fresh)
    anthro_age_calc(fresh, "Adolescent")
    mental_amount, physical_amount = mutations.biologic_mutations_number(fresh)
    mutations.mutation_assignment(fresh, mental_amount, physical_amount,"any")
    #anthro_mutations_fresh(fresh)
    anthro_vocations_fresh(fresh)
    vocation.set_up_first_time(fresh)
    outputs.anthro_screen(fresh)
    core.assign_persona_name(fresh)
    outputs.anthro_screen(fresh)
    please.assign_id_and_file_name(fresh)
    please.record_storage(fresh)
    
    return fresh # built with side effects mostly

#####################################
# build a BESPOKE anthro persona
# choices that reflect story needs
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
    bespoke.Player_Name = str(please.input_this("\nPlease input your MUNDANE TERRAN NAME: "))


    ### build list of functions
    anthro_attributes_bespoke(bespoke)
    anthro_type_bespoke(bespoke)
    anthro_sub_type_selection(bespoke)
    anthro_size_chooser(bespoke)
    vocation.exps_level_picker(bespoke)
    anthro_mutations_bespoke(bespoke)
    anthro_vocation_bespoke(bespoke)
    vocation.set_up_first_time(bespoke)
    bespoke.EXPS = (
        42 if bespoke.Level == 1 else vocation.convert_levels_to_exps(bespoke)
    )

    ### add additional interests and skills (gifts are dynamic )
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
        anthro_choose_age_cat(bespoke)
    else:
        random_anthro_age_category(bespoke)

    ### anthro AR if not already there
    hack = 42 if hasattr(bespoke, "AR") else core.base_armour_rating(bespoke)

    ### anthro  Move if not already there
    hack = 42 if hasattr(bespoke, "Move") else core.base_armour_rating(bespoke)

    ###
    core.wate_allowance(bespoke)

    ### impact of level on:
    # attributes
    # mutations
    # vocation gifts, interests, and skills
    # combat table
    # EXPS amount

    ### generate RP Fun
    build_RP_role_play(bespoke)

    ### generate RP storage data including temporary name
    core.assign_persona_name    
    please.assign_id_and_file_name(bespoke)
    outputs.anthro_screen(bespoke)

    ### ultimate RP disposition
    please.record_storage(bespoke)
    return

#####################################
# build a RANDOM anthro persona
# does not stop uses RP flag
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
    rando.Fallthrough = True

    ### get mundane terran name of the player
    rando.Player_Name = input("\nPlease input your MUNDANE TERRAN NAME: ")

    ### build list of functions
    core.initial_attributes(rando)
    core.hit_points_max(rando)
    adjust_mstr_by_int(rando)
    rando.Anthro_Type = secrets.choice(
        [x for x in table.anthro_ages_by_category_and_type]
    )
    rando.FAMILY_SUB = secrets.choice(table.anthro_sub_types[rando.Anthro_Type])

    adjust_attributes_by_anthro_type(rando)
    anthro_size_rando(rando)
    core.movement_rate(rando)
    core.base_armour_rating(rando)
    core.wate_allowance(rando)
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
    core.wate_allowance(rando)

    if rando.RP:
        build_RP_role_play(rando)

    ### generate RP storage data including temporary name
    rando.Persona_Name = f"{rando.Player_Name} Mac{rando.Player_Name}"
    please.assign_id_and_file_name(rando)
    outputs.anthro_screen(rando)

    ### ultimate persona disposition
    please.record_storage(rando)
    return
