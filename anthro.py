import math
from secrets import choice
from dataclasses import dataclass

import please
import exp_tables
import vocation
import core

import outputs
import mutations

# set up AnthroRecord
@dataclass
class AnthroRecord(exp_tables.Anthropic):
    pass


def anthro_workflow() -> None: 
    """
    player persona vs referee persona vs updating existing persona
    """
    # clearance for Clarence
    please.clear_console()

    """
    "Fresh Anthro (new player)":lambda: fresh_anthro(nom_de_bom),
    "Bespoke Anthro":lambda: bespoke_anthro(nom_de_bom),
    "Random Anthro":lambda:random_anthro(nom_de_bom),
    """


    workflow_function_map = {
        "Fresh Anthro (new player)":fresh_anthro,
        "Bespoke Anthro":bespoke_anthro,
        "Random Anthro":random_anthro,
        "Maintain Existing Record":please.record_maintenance,
        "Input Paper Record":input_paper_record
    }
    please.clear_console()
    choice_comment = "Choose ANTHRO workflow? "
    choices= list(workflow_function_map.keys())
    anthro_record_type = please.choose_this(choices, choice_comment)

    if anthro_record_type in workflow_function_map:
        workflow_function_map[anthro_record_type]()

    else:
        input("not ready for this")

####################################
# FRESH ANTHRO FUNCTIONS
####################################

def adjust_mstr_by_int(minding:AnthroRecord) -> AnthroRecord:
    """
    alters MSTR based on persona's INT
    """
    adjusted_MSTR = minding.MSTR + exp_tables.mstr_adjusted_by_int[minding.INT]
    minding.MSTR = adjusted_MSTR if adjusted_MSTR > 0 else 1 
    return minding # altered by side effect

def anthro_type_by_attribute(making_anthro_list: AnthroRecord) -> list:
    """
    returns a list of eligible anthro types based on attributes
    """
    anthro_type_choices = []

    for anthro_type in exp_tables.anthro_type_attribute_requirements:
        anthro_type_flag = True

        for attribute_name in exp_tables.anthro_type_attribute_requirements[anthro_type]:
            persona_attribute_value = getattr(making_anthro_list, attribute_name)
            required_attribute_value = exp_tables.anthro_type_attribute_requirements[
                anthro_type
            ][attribute_name]
            if persona_attribute_value < required_attribute_value:
                anthro_type_flag = False
        if anthro_type_flag:
            anthro_type_choices.append(anthro_type)

    return anthro_type_choices

def anthro_type_choose(choosey: AnthroRecord) -> AnthroRecord:
    """
    pick from the eligible anthro types aka GENUS
    """
    if choosey.Fallthrough or choosey.Bespoke:
        choices = please.list_table_choices(exp_tables.anthro_types_list)
    else:
        choices = anthro_type_by_attribute(choosey)

    choosey.FAMILY_TYPE = please.choose_this(choices, "choose an ANTHRO GENUS.", choosey)

    return choosey # altered by side effect

# todo there is some sloppy stuff here 
def anthro_sub_choose(subway: AnthroRecord) -> AnthroRecord:
    """
    select the sub_type aka SPECIES for the anthro type aka GENUS
    """
    choices = choices = exp_tables.anthro_sub_types[subway.FAMILY_TYPE]

    if subway.Fallthrough:
        subway.FAMILY_SUB = please.choose_this(choices,"choose ANTHRO SPECIES.", subway)
        return subway # modified by side effect

    if please.say_yes_to(f"do you want to create your own ANTHRO SPECIES for the genus {subway.FAMILY_TYPE.lower()} "):
        sub_type = please.input_this(f"carefully input an ANTHRO SPECIES for the genus {subway.FAMILY_TYPE.lower()} ")
    else:
        sub_type = please.choose_this(choices,"choose ANTHRO SPECIES ", subway)

    subway.FAMILY_SUB = sub_type

    return subway # altered by side effect

def adjust_attributes_by_anthro_type(anthro_adjusting: AnthroRecord) -> AnthroRecord:
    """
    each ANTHRO GENUS has attribute adjustments for "reasons"
    adjust the persona's attributes according to the persona type aka GENUS
    """
    anthro_type = anthro_adjusting.FAMILY_TYPE
    anthro_line = exp_tables.attribute_adjustment_by_anthro_type[anthro_type]
    attributes_to_change = {attribute : change for attribute, change in anthro_line.items() if change != 0}

    for attribute,change in attributes_to_change.items():

        # CON special case, adjusts the HPM
        if attribute == "CON":
            anthro_line["HPM"] = please.roll_this(f'1d8+{change}')

        # INT special case, may adjust the MSTR
        elif attribute == "INT":
            old_change = exp_tables.mstr_adjusted_by_int[anthro_adjusting.INT]
            new_change = exp_tables.mstr_adjusted_by_int[anthro_adjusting.INT + change]
            new_MSTR = anthro_adjusting.MSTR + (new_change - old_change)
            change_MSTR = (new_change - old_change) if (new_MSTR) > 0 else 0
            anthro_line["MSTR"] = change_MSTR

    for attribute,change in anthro_line.items():
        old_attribute = getattr(anthro_adjusting, attribute)
        change = 0 if change < 0 and not anthro_adjusting.RP and attribute != "CHA"else change # protects players from -ve adjustments
        new_attribute = (old_attribute + change)
        new_attribute = 1 if new_attribute < 1 and attribute != "CHA" else new_attribute
        setattr(anthro_adjusting, attribute, new_attribute)

    return anthro_adjusting # adjusted by side effect

def anthro_hite_wate_calc(size_this:AnthroRecord, sizer: str) -> AnthroRecord:
    '''calculates hite and wate for persona based on smaller or larger '''
    anthro_type = size_this.FAMILY_TYPE

    size_table_chosen = exp_tables.small_anthro_sizes if sizer == "Smaller" else exp_tables.large_anthro_sizes
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
    '''
    add the anthro age and age_cat to the persona record
    '''
    
    anthro_type = years_old.FAMILY_TYPE
    age_categories = [val for val  in exp_tables.anthro_random_age_category.values() if val != "1d100"]
    die_roll = exp_tables.anthro_ages_by_category_and_type[anthro_type][age_categories.index(ager)]
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
    mentchance = exp_tables.anthro_type_mutation_chance[anthro_type]["mentchance"]
    physchance = exp_tables.anthro_type_mutation_chance[anthro_type]["physchance"]

    # create the mutations dict
    randomly_mutating.Mutations = {}

    ##### Mental Mutation chance, number and generation
    # percent chance mentchance
    if please.do_1d100_check(mentchance):
        mutation_number = please.roll_this(
            exp_tables.anthro_type_mutation_chance[anthro_type]["mentnumber"]
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
            exp_tables.anthro_type_mutation_chance[anthro_type]["physnumber"]
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
    option_list = ["Child", "Adolescent", "Adult", "Older", "Aged"]
    list_comment = "Choose a bespoke age range."
    age_cat = please.choose_this(option_list, list_comment, years_old)

    return age_cat

def anthro_nomenclature(avatar:AnthroRecord) -> AnthroRecord:
    '''name the  anthro persona'''
    please.clear_console()
    print(f'\n{avatar.Player_Name} you are NAMING a {please.get_kind_of(avatar)} {avatar.FAMILY.upper()} persona.')
    print(f'The persona looks like: {avatar.Quick_Description}')
    avatar.Persona_Name = please.input_this(f"please input the PERSONA NAME: ")
    return avatar # altered by side effects 


#####################################
# build a FRESH anthro persona
#####################################

def fresh_anthro() -> None:
    """
    builds the anthro record for a fresh persona
    """
    fresh = AnthroRecord()
    fresh.Player_Name = core.acquire_player_name()
    please.setup_persona(fresh)

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

    if fresh.RP_Cues:
        core.build_RP_role_play(fresh) 

    fresh.Quick_Description = f'A {fresh.Age} {fresh.Age_Suffix.lower()} old {fresh.FAMILY_SUB.lower()} {fresh.FAMILY_TYPE.lower()} {fresh.Vocation.lower()}'
    please.wrap_up_persona(fresh)

#####################################
# build a BESPOKE anthro persona
#####################################

def bespoke_anthro() -> None:
    """
    building a bespoke anthro persona typically a referee persona
    """
    bespoke = AnthroRecord()
    bespoke.Bespoke = True
    bespoke.Player_Name = core.acquire_player_name()
    please.setup_persona(bespoke)

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

    # todo bespoke and random mutation
    core.mutations_bespoke(bespoke)

    if please.say_yes_to("Do you want attribute selected VOCATION"):
        bespoke.Vocation = please.choose_this(vocation.attribute_determined(bespoke), "Choose a VOCATION")
    else:
        bespoke.Vocation = please.choose_this(exp_tables.vocation_list, "Choose VOCATION type.",bespoke)
 
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
        bespoke.Age_Cat = please.get_table_result(exp_tables.anthro_random_age_category)
    else:
        bespoke.Age_Cat = anthro_return_age_cat(bespoke)

    anthro_age_calc(bespoke, bespoke.Age_Cat)

    if bespoke.RP_Cues:
        core.build_RP_role_play(bespoke) 
    
    bespoke.Quick_Description = f'A {bespoke.Age} {bespoke.Age_Suffix.lower()} old {bespoke.FAMILY_SUB.lower()} {bespoke.FAMILY_TYPE.lower()} {bespoke.Vocation.lower()}'
    # todo RP level impact  on: attributes mutations
    please.wrap_up_persona(bespoke)

#####################################
# build a RANDOM anthro persona
#####################################

def random_anthro() -> None:
    """
    building a RANDOM anthro persona, typically a referee persona
    """
    rando = AnthroRecord()
    rando.Fallthrough = True
    rando.Player_Name = core.acquire_player_name()
    please.setup_persona(rando)

    core.initial_attributes(rando)
    rando.HPM = core.hit_points_max(rando)
    adjust_mstr_by_int(rando)
    rando.FAMILY_TYPE = choice(exp_tables.anthro_types_list)
    rando.FAMILY_SUB = choice(exp_tables.anthro_sub_types[rando.FAMILY_TYPE])
    adjust_attributes_by_anthro_type(rando)
    anthro_size_chooser(rando)
    core.movement_rate(rando)
    core.base_armour_rating(rando)
    core.wate_allowance(rando)
    anthro_mutations_rando(rando)
    rando.Vocation = choice(exp_tables.vocation_list)
    vocation.set_up_first_time(rando)
    rando.Level = please.get_table_result(exp_tables.random_EXPS_levels_list)
    rando.EXPS = vocation.convert_levels_to_exps(rando)
    if rando.Level > 1:
        rando.Interests.extend(vocation.update_interests(rando, (rando.Level - 1)))
        rando.Skills.extend(vocation.update_skills(rando, (rando.Level - 1)))

    vocation.attributes_to_vocation(rando)
    rando.Age_Cat = please.get_table_result(exp_tables.anthro_random_age_category)    
    anthro_age_calc(rando, rando.Age_Cat)

    if rando.RP_Cues:
        core.build_RP_role_play(rando) 

    rando.Quick_Description = f'A {rando.Age} {rando.Age_Suffix.lower()} old {rando.FAMILY_SUB.lower()} {rando.FAMILY_TYPE.lower()} {rando.Vocation.lower()}'

    please.wrap_up_persona(rando)


#####################################
# INPUT an anthro persona
#####################################

def input_paper_record() -> None:
    """
    input a paper record by hand
    """


    # set up the persona record class
    paper = AnthroRecord()

    # get names
    paper.Player_Name = please.input_this(f"please input your MUNDANE TERRAN NAME ")
    paper.Persona_Name = please.input_this(f"please input the PERSONA NAME ")


    # input the attributes from top stripe

    for (attribute) in exp_tables.suggested_anthro_attributes:
        please.clear_console()
        cant_move_on = True
        
        while cant_move_on:
            please.clear_console()
            print(f'inputting {paper.Persona_Name}\'s {exp_tables.suggested_anthro_attributes[attribute]["long_name"]}')
            # input(f"{exp_tables.suggested_anthro_attributes[attribute]["long_name"]} is typically {exp_tables.suggested_anthro_attributes[attribute]["start_min"]} to {exp_tables.suggested_anthro_attributes[attribute]["start_max"]} [Return to continue] ")
            attribute_value = please.input_this(f"input {paper.Persona_Name.lower()}'s {attribute} (usu {exp_tables.suggested_anthro_attributes[attribute]["start_min"]}-{exp_tables.suggested_anthro_attributes[attribute]["start_max"]}) ")

            try: 
                int(attribute_value)
                attribute_value = int(attribute_value)
            except ValueError:
                please.show_error_message(f"attributes must be integers")
                continue

            if attribute_value < 1 and attribute != "CHA":
                please.show_error_message(f"not compatible with life")
                continue

            if attribute_value > exp_tables.suggested_anthro_attributes[attribute]["start_max"]:
                if please.say_yes_to(f"is a {attribute} of {attribute_value} for real? "):
                    cant_move_on = False
            else:
                cant_move_on = False

            setattr(paper,attribute, attribute_value)

    # choose the family
    family_choices = ["Anthro", "Alien","Robot", "AI"]
    comment = f"input {paper.Persona_Name.lower()}'s FAMILY "
    family_choice = please.choose_this(family_choices,comment,paper)
    paper.FAMILY = family_choice

    # choose the family_type

    if paper.FAMILY == "Anthro":
        comment = f"input {paper.Persona_Name.lower()}'s GENUS"
        genus_choice = please.choose_this(exp_tables.anthro_types_list,comment,paper)
        setattr(paper,"FAMILY_TYPE", genus_choice)

    else:
        print('not here yet')

 
    # choose the family sub type
    if paper.FAMILY == "Anthro":
        anthro_sub_choose(paper)
    else:
        print('not here yet')

    # age and suffix
    age_suffixes = ["years","seconds","minutes","hours", "weeks", "months"]
    comment = f"input {paper.Persona_Name.lower()}'s AGE SUFFIX"
    age_suffix = please.choose_this(age_suffixes, comment, paper)
    paper.Age_Suffix = age_suffix

    age = please.input_this(f"what is {paper.Persona_Name.lower()}'s AGE in {paper.Age_Suffix} ")
    paper.Age = int(age)

    # HITE and WATE
    paper.Size_Cat = "Medium"
    paper.Hite_Suffix = "cms"
    paper.Wate_Suffix = "kgs"   

    hite = please.input_this(f"what is {paper.Persona_Name.lower()}'s HITE in {paper.Hite_Suffix} ")
    paper.Hite = int(hite)

    wate = please.input_this(f"what is {paper.Persona_Name.lower()}'s WATE in {paper.Wate_Suffix} ")
    paper.Wate = int(wate)

    # mutations
    mutations.pick_bespoke_mutation(paper)

    # vocation
    paper.Vocation = please.choose_this(exp_tables.vocation_list, "choose VOCATION type.",paper)
    level = please.input_this(f"what is {paper.Persona_Name.lower()}'s EXPS LEVEL ")
    paper.Level = int(level)

    # special case of Nothing
    if paper.Vocation == "Nothing":
        choices = list(exp_tables.vocation_aspiration_exps.keys())
        comment = "a nothing needs a VOCATIONAL ASPIRATION. Please pick one. "
        vocation_desired = please.choose_this(choices, comment)
        paper.Vocay_Aspiration = vocation_desired
        paper.Vocay_Aspiration_EXPS = exp_tables.vocation_aspiration_exps[vocation_desired]

    # interests
    interest_table = exp_tables.vocations_interests_pivot[paper.Vocation]
    choices = please.list_table_choices(interest_table)

    interest_amount = please.input_this(f"how many INTERESTS does {paper.Persona_Name.lower()} have ")
    for index in range(int(interest_amount)):
        paper.Interests.append(please.choose_this(choices, f"choose {paper.Vocation} interest #{index + 1}/{interest_amount}"))

    # skills
    skill_amount = int(please.input_this(f"how many SKILLS does {paper.Persona_Name.lower()} have "))

    skills_table = []
    for skillist in exp_tables.vocation_skills_tables[paper.Vocation]:
        for key, value in skillist.items():
            if key != "die_roll" and key != "name":
                skills_table.append(value)

    for index in range(int(skill_amount)):
        paper.Skills.append(please.choose_this(skills_table, f"choose {paper.Vocation} skill #{index + 1}/{skill_amount}"))         

    # add the calculated stuff to the paper record
    core.movement_rate(paper)
    core.base_armour_rating(paper)
    core.wate_allowance(paper)    

    # create the quick description for the attributes stripe
    paper.Quick_Description = f'A {paper.Age} {paper.Age_Suffix.lower()} old {paper.FAMILY_SUB.lower()} {paper.FAMILY_TYPE.lower()} {paper.Vocation.lower()}'

    # wrap up the paper persona 
    please.clear_console()
    input(f'\n{paper.Player_Name} has created a {please.get_kind_of(paper)} {paper.FAMILY.upper()} persona.\nHit RETURN to review..')
    please.screen_this(paper)
    print(f'\nYou may need to SCROLL UP to fully review...')
    please.assign_file_name(paper)
    please.clear_console()
    please.screen_this(paper)
    print(f'\nYou may need to SCROLL UP to fully review...')
    please.record_storage(paper)

    return