import math
from secrets import choice
from dataclasses import dataclass

import please
import table
import vocation
import core

import outputs
import mutations

# set up AnthroRecord
@dataclass
class AnthroRecord(table.Anthropic):
    pass


def anthro_workflow() -> None: 
    """
    player persona vs referee persona vs updating existing persona
    """
    # clearance for Clarence
    please.clear_console()

    print('This is a ANTHRO Build')
    nom_de_bom = please.input_this("\nPlease input your MUNDANE TERRAN NAME: ")

    workflow_function_map = {
        "Fresh Anthro (new player)":lambda: fresh_anthro(nom_de_bom),
        "Bespoke Anthro":lambda: bespoke_anthro(nom_de_bom),
        "Random Anthro":lambda:random_anthro(nom_de_bom),
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

def adjust_mstr_by_int(minding:AnthroRecord) -> AnthroRecord:
    """
    alters MSTR based on persona's INT
    """
    adjusted_MSTR = minding.MSTR + table.mstr_adjusted_by_int[minding.INT]
    minding.MSTR = adjusted_MSTR if adjusted_MSTR > 0 else 1 
    return minding # altered by side effect

def anthro_type_by_attribute(making_anthro_list: AnthroRecord) -> list:
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

    return anthro_type_choices

def anthro_type_choose(choosey: AnthroRecord) -> AnthroRecord:
    """
    pick from the eligible anthro types
    """
    if choosey.Fallthrough or choosey.Bespoke:
        choices = please.list_table_choices(table.anthro_types_list)
    else:
        choices = anthro_type_by_attribute(choosey)

    choosey.FAMILY_TYPE = please.choose_this(choices, "Choose an anthro TYPE.", choosey)

    return choosey # altered by side effect

# todo there is some sloppy stuff here 
def anthro_sub_choose(subway: AnthroRecord) -> AnthroRecord:
    """
    select the sub_type for the anthro type
    """
    choices = choices = table.anthro_sub_types[subway.FAMILY_TYPE]

    if subway.Fallthrough:
        subway.FAMILY_SUB = please.choose_this(choices,"Choose anthro SUB TYPE.", subway)
        return subway # modified by side effect

    if please.say_yes_to("Do you want to create your own SUB TYPE"):
        sub_type = please.input_this(f"Carefully input a SUB TYPE for the family {subway.FAMILY_TYPE}: ")
    else:
        sub_type = please.choose_this(choices,"Choose anthro SUB TYPE.", subway)

    subway.FAMILY_SUB = sub_type

    return subway # altered by side effect

def adjust_attributes_by_anthro_type(anthro_type_attributes_adjust: AnthroRecord) -> AnthroRecord:
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

def anthro_hite_wate_calc(size_this:AnthroRecord, sizer: str) -> AnthroRecord:
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

def anthro_size_chooser(size_me:AnthroRecord) -> AnthroRecord:
    '''player chooses a size for her persona, all size_cat are medium'''

    choices = ["Smaller", "Larger"]
    choice_comment = f'Choose the SIZE of your {size_me.FAMILY_TYPE.upper()}. '
    anthro_size_choice = please.choose_this(choices, choice_comment,size_me)
    anthro_hite_wate_calc(size_me, anthro_size_choice)

    return size_me # is modified by side effects in anthro_hite_wate_calc


# todo crappy aging logic
def anthro_age_calc(years_old: AnthroRecord, ager: str) -> AnthroRecord:
    '''add the anthro age and age_cat to the persona record'''
    anthro_type = years_old.FAMILY_TYPE
    age_categories = [val for val  in table.anthro_random_age_category.values() if val != "1d100"]
    die_roll = table.anthro_ages_by_category_and_type[anthro_type][age_categories.index(ager)]
    age_years = please.roll_this(die_roll)

    years_old.Age = age_years

    return years_old # modified by side effect

# todo anthro mutations requires a code review
def anthro_mutations_rando(randomly_mutating: AnthroRecord) -> AnthroRecord:
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

def anthro_return_age_cat(years_old: AnthroRecord) -> str:
    """
    allow user to select an anthro age category
    """
    option_list = ["Child", "Adolescent", "Adult", "Elder", "Aged"]
    list_comment = "Choose a bespoke age range."
    age_cat = please.choose_this(option_list, list_comment, years_old)

    return age_cat

# todo code review this mess
def role_play_RP_arc() -> str:
    """
    return referee person arc in relation to expedition now
    """
    past = please.get_table_result(table.role_play_RP_arc_past)
    present = please.get_table_result(table.role_play_RP_arc_present)
    goal = please.get_table_result(table.role_play_RP_arc_goal)

    return f"Past: {past}, Present: {present}, Goal: {goal}."

def role_play_RP_beliefs() -> str:
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

def role_play_RP_personality()->str:
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

def build_RP_role_play(player:AnthroRecord) -> AnthroRecord:
    """
    create all the fun role_play elements for a referee persona
    """

    print("Building the role playing components of the referee persona")
    player.RP_Fun = []
    player.RP_Fun.append(f"Arc: {role_play_RP_arc()}")
    player.RP_Fun.append(
        f"Dress: {please.get_table_result(table.referee_persona_dress)} Hygiene: {please.get_table_result(table.referee_persona_hygiene)} Odor: {please.get_table_result(table.alien_biology_aroma)}"
    )
    player.RP_Fun.append(
        f"Personality: {role_play_RP_personality()} Voice: {please.get_table_result(table.laban)} Move: { please.get_table_result(table.laban)} "
    )
    player.RP_Fun.append(f"{role_play_RP_beliefs()}")

    return

#####################################
# build a FRESH anthro persona
#####################################

def fresh_anthro(player_name) -> AnthroRecord:
    """
    builds the anthro record for a fresh persona
    """

    please.clear_console()
    print("\nYou are generating a fresh ANTHRO PERSONA")

    ### set up the object for Anthro persona
    fresh = AnthroRecord()
    fresh.RP = True if please.say_yes_to("Do you want role playing cues? ") else False

    # todo proper  input_this with cyclic 
    fresh.Player_Name = player_name
    core.initial_attributes(fresh)
    fresh.HPM = core.hit_points_max(fresh)
    adjust_mstr_by_int(fresh)
    anthro_type_choose(fresh)
    anthro_sub_choose(fresh)
    adjust_attributes_by_anthro_type(fresh)
    anthro_size_chooser(fresh)
    core.movement_rate(fresh)
    core.base_armour_rating(fresh)
    core.wate_allowance(fresh)
    fresh.Age_Cat = "Adolescent"
    anthro_age_calc(fresh, fresh.Age_Cat)
    mental_amount, physical_amount = mutations.biologic_mutations_number(fresh)
    mutations.mutation_assignment(fresh, mental_amount, physical_amount,"any")

    fresh.Vocation = please.choose_this(vocation.attribute_determined(fresh), "Choose a VOCATION")

    vocation.set_up_first_time(fresh)
    outputs.anthro_screen(fresh)
    core.assign_persona_name(fresh)
    outputs.anthro_screen(fresh)
    please.assign_id_and_file_name(fresh)
    please.record_storage(fresh)
    
    return fresh # built with side effects mostly

#####################################
# build a BESPOKE anthro persona
#####################################

def bespoke_anthro(player_name):
    """
    building a bespoke anthro persona typically a referee persona
    """

    # clearance for Clarence
    please.clear_console()
    print("\nYou are generating a bespoke ANTHRO PERSONA.")

    ### set up the object for Anthro persona
    bespoke = AnthroRecord()
    bespoke.Bespoke = True
    bespoke.RP = True if please.say_yes_to("Do you want referee persona cues? ") else False

    bespoke.Player_Name = player_name
    core.initial_attributes(bespoke)
    bespoke.HPM = core.hit_points_max(bespoke) 
    adjust_mstr_by_int(bespoke)
    core.movement_rate(bespoke)
    core.base_armour_rating(bespoke)
    core.wate_allowance(bespoke)

    anthro_type_choose(bespoke)
    anthro_sub_choose(bespoke)
    anthro_size_chooser(bespoke)
    adjust_attributes_by_anthro_type(bespoke)

    # todo  bespoke and random mutation
    core.mutations_bespoke(bespoke)

    if please.say_yes_to("Do you want attribute selected VOCATION"):
        bespoke.Vocation = please.choose_this(vocation.attribute_determined(bespoke), "Choose a VOCATION")
    else:
        bespoke.Vocation = please.choose_this(table.vocation_list, "Choose VOCATION type.",bespoke)
 
    vocation.set_up_first_time(bespoke)
    vocation.exps_level_picker(bespoke)
    bespoke.EXPS = 42 if bespoke.Level == 1 else vocation.convert_levels_to_exps(bespoke)

    if bespoke.Level > 1:
        bespoke.Interests.extend(vocation.update_interests(bespoke, (bespoke.Level - 1)))
        bespoke.Skills.extend(vocation.update_skills(bespoke, (bespoke.Level - 1)))

    if please.say_yes_to("Do you want adjust attributes by VOCATION? (recommended)"):
        vocation.attributes_to_vocation(bespoke)

    if please.say_yes_to("Do you want to adjust attributes by DESCRIPTION?"):
        core.descriptive_attributes(bespoke)

    if please.say_yes_to("Use table AGE CATEGORY?"):
        bespoke.Age_Cat = please.get_table_result(table.anthro_random_age_category)
    else:
        bespoke.Age_Cat = anthro_return_age_cat(bespoke)

    anthro_age_calc(bespoke, bespoke.Age_Cat)
    
    # todo RP level impact  on: attributes mutations vocation gifts, interests, and skills combat table EXPS amount

    ### generate RP Fun
    build_RP_role_play(bespoke)

    ### generate RP storage data including temporary name
    outputs.anthro_screen(bespoke)
    core.assign_persona_name(bespoke)   
    please.assign_id_and_file_name(bespoke)
    outputs.anthro_screen(bespoke)
    please.record_storage(bespoke)
    return

#####################################
# build a RANDOM anthro persona
#####################################

def random_anthro(player_name):
    """
    building a RANDOM anthro persona, typically a referee persona
    """

    # clearance for Clarence
    please.clear_console()
    print("\nYou are generating a RANDOM ANTHRO PERSONA.")

    ### set up the object for Anthro persona
    rando = AnthroRecord()
    rando.RP = True if please.say_yes_to("Do you want role playing cues? ") else False
    rando.Fallthrough = True

    ### get mundane terran name of the player
    rando.Player_Name = player_name

    ### build list of functions
    core.initial_attributes(rando)
    rando.HPM = core.hit_points_max(rando)
    adjust_mstr_by_int(rando)
    rando.FAMILY_TYPE = choice(table.anthro_types_list)
    rando.FAMILY_SUB = choice(table.anthro_sub_types[rando.FAMILY_TYPE])
    adjust_attributes_by_anthro_type(rando)
    anthro_size_chooser(rando)
    core.movement_rate(rando)
    core.base_armour_rating(rando)
    core.wate_allowance(rando)
    anthro_mutations_rando(rando)
    rando.Vocation = choice(table.vocation_list)
    vocation.set_up_first_time(rando)
    rando.Level = please.get_table_result(table.random_EXPS_levels_list)
    rando.EXPS = vocation.convert_levels_to_exps(rando)
    if rando.Level > 1:
        rando.Interests.extend(vocation.update_interests(rando, (rando.Level - 1)))
        rando.Skills.extend(vocation.update_skills(rando, (rando.Level - 1)))

    vocation.attributes_to_vocation(rando)
    rando.Age_Cat = please.get_table_result(table.anthro_random_age_category)    
    anthro_age_calc(rando, rando.Age_Cat)
    if rando.RP:
        build_RP_role_play(rando)

    ### generate RP storage data including temporary name
    
    rando.Persona_Name = f"{rando.Player_Name}y Mac{rando.Player_Name}face"
    please.assign_id_and_file_name(rando)
    outputs.anthro_screen(rando)

    ### ultimate persona disposition
    please.record_storage(rando)
    return
