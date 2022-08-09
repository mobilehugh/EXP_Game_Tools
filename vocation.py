import math
import please
import table
import secrets


""" 
huge code clean up here. replace gifts, interests and skills with update_gifts, update_interests and update_skills
"""


def biologist(object: dict) -> None:
    """
    Set up the biologist vocation.
    """
    # collect data
    intel = object.INT
    awe = object.AWE
    interest_rolls = math.ceil(awe / 4)
    skill_rolls = math.ceil(intel / 4)

    # assign GIFTS
    # done in real time

    # assign  INTERESTS
    object.Interests = fresh_interests(object, interest_rolls)

    # assign  SKILLS
    object.Skills = fresh_skills(object, skill_rolls)

    return


def knite(object: dict) -> None:
    """
    Set up the knite vocation.
    """
    # collect data
    intel = object.INT
    mstr = object.MSTR
    interest_rolls = math.ceil(mstr / 4)
    skill_rolls = math.ceil(intel / 3)

    # assign GIFTS
    # done in real time

    # assign  INTERESTS
    object.Interests = fresh_interests(object, interest_rolls)

    # assign  SKILLS
    object.Skills = fresh_skills(object, skill_rolls)

    return


def mechanic(object: dict) -> None:
    """
    Set up the mechanic vocation.
    """
    # collect Data
    intel = object.INT
    interest_rolls = math.ceil(intel / 4)
    skill_rolls = math.ceil(intel / 3)

    # assign GIFTS
    # done in real time

    # assign  INTERESTS
    object.Interests = fresh_interests(object, interest_rolls)

    # assign  SKILLS
    object.Skills = fresh_skills(object, skill_rolls)

    return


def mercenary(object: dict) -> None:
    """
    Set up the mercenary vocation.
    """
    
    # collect Data
    intel = object.INT
    dex = object.DEX
    interest_rolls = math.ceil(intel / 4)
    skill_rolls = math.ceil(dex / 3)

    # assign GIFTS
    # done in real time

    # assign  INTERESTS
    object.Interests = fresh_interests(object, interest_rolls)

    # assign  SKILLS
    object.Skills = fresh_skills(object, skill_rolls)

    return


def nomad(object: dict) -> None:
    """ 
    set up the nomad vocation.
    """
    # collect Data
    awe = object.AWE
    intel = object.INT
    interest_rolls = math.ceil(intel / 4)
    skill_rolls = math.ceil(awe / 3)

    # assign GIFTS
    # done in real time

    # assign  INTERESTS
    object.Interests = fresh_interests(object, interest_rolls)

    # assign  SKILLS
    object.Skills = fresh_skills(object, skill_rolls)

    return


def nothing(object: dict) -> None:
    """
    set up the nothing vocation.
    """
    # collect Data
    soc = object.SOC
    intel = object.INT
    interest_rolls = math.ceil(soc / 200)
    skill_rolls = math.ceil(intel / 3)

    # assign GIFTS
    # done in real time

    # assign  INTERESTS
    object.Interests = fresh_interests(object, interest_rolls)

    # assign  SKILLS
    object.Skills = fresh_skills(object, skill_rolls)

    ### Vocation aspiration is specific to the nothing vocation
    choices = list(table.vocation_aspiration_exps.keys())
    comment = "Please choose a vocation aspiration."

    if object.Otto:
        vocation_desired = secrets.choice(choices)

    else:
        vocation_desired = please.choose_this(choices, comment)

    ### initiate the nothing aspiration goal. managed in outputs.py
    object.Vocay_Aspiration = vocation_desired
    object.Vocay_Aspiration_EXPS = table.vocation_aspiration_exps[vocation_desired]

    return


def spie(object):
    # collect data
    intel = object.INT
    dex = object.DEX

    interest_rolls = math.ceil(intel / 4)
    skill_rolls = math.ceil(dex / 3)

    # assign GIFTS
    # done in real time

    # assign  INTERESTS
    object.Interests = fresh_interests(object, interest_rolls)

    # assign  SKILLS
    object.Skills = fresh_skills(object, skill_rolls)

    # assign MARTIAL ARTS
    object.Spie_Fu = spie_martial_arts(object)


    return


def spie_martial_arts(object: dict) -> str:
    """
    Update the object's martial arts data.
    """

    # collect data from martial arts table
    martial_arts_data = table.spie_martial_arts[
        object.Level if object.Level < 10 else 10
    ]

    # martial armour rating
    martial_ar = object.AR + martial_arts_data["AR"]

    freq = martial_arts_data["freq"]
    damage = martial_arts_data["Damage"]
    sequence = martial_arts_data["order"]
    martial_desc = f"AR: {martial_ar} DMG: {damage} Attacks: {int(freq)} Order: {sequence}"

    ### removes old Spie Fu from interests. Only works on one element
    for x, interest in enumerate(object.Interests):
        if "Spie Fu" in interest:
            object.Interests.pop(x)

    return martial_desc


def veterinarian(object):
    # collect data
    intel = object.INT
    interest_rolls = math.ceil(intel / 4)
    skill_rolls = math.ceil(intel / 3)

    # assign GIFTS
    # done in real time

    # assign  INTERESTS
    object.Interests = fresh_interests(object, interest_rolls)

    # assign  SKILLS
    object.Skills = fresh_skills(object, skill_rolls)

    # # assign veterinarian interests
    # interest_list = []

    # while len(interest_list) < interest_rolls:
    #     interest = please.get_table_result(table.veterinarian_interests)
    #     interest_list.append(interest)
    #     if interest == "Extra Roll":
    #         interest_rolls += 1
    #         interest_list.pop()

    #     if interest == "Choose":
    #         interest_list.pop()
    #         choices = please.list_table_choices(table.veterinarian_interests)
    #         choice_comment = "Choose a veterinarian interest."
    #         choice = please.choose_this(choices, choice_comment)
    #         interest_list.append(choice)

    # interest_list.sort()
    # object.Interests = interest_list

    # # assign spie skills
    # skill_list = []

    # while len(skill_list) < skill_rolls:
    #     # select a random interest table
    #     interest_type_list = interest_list[secrets.randbelow(len(interest_list))]
    #     skill = please.get_table_result(
    #         table.vet_interest_skill_pivot[interest_type_list]
    #     )
    #     skill_list.append(skill)

    #     if skill == "Extra Roll":
    #         skill_rolls += 1
    #         skill_list.pop()

    #     if skill == "Choose":
    #         skill_list.pop()
    #         choices = please.list_table_choices(
    #             table.vet_interest_skill_pivot[interest_type_list]
    #         )
    #         choice_comment = "Choose a veterinarian skill."
    #         choice = please.choose_this(choices, choice_comment)
    #         skill_list.append(choice)

    # skill_list.sort()
    # object.Skills = skill_list

    return


# data for classes revomved from here


def list_eligible_vocations(object: dict) -> list:
    """
    returns a list of eligibile vocations to choose one
    """

    # find eligible vocations for any attribute set
    awe = object.AWE
    cha = object.CHA
    con = object.CON
    dex = object.DEX
    intel = object.INT
    mstr = object.MSTR
    pstr = object.PSTR
    hpm = object.HPM

    vocation_list = []

    if (awe + intel) >= 18:
        vocation_list.append("Biologist")

    if (dex >= 15) and (mstr >= 18) and (hpm >= 25):
        if please.say_yes_to("Is KNITE referee approved?"):
            vocation_list.append("Knite")

    if intel >= 13:
        vocation_list.append("Mechanic")

    if ((con + dex + pstr) >= 22) and (hpm >= 40):
        vocation_list.append("Mercenary")

    if (awe >= 10) and (con >= 6) and (intel >= 5) and (hpm >= 20):
        vocation_list.append("Nomad")

    #  any persona can pursue Nothing vocation
    vocation_list.append("Nothing")

    if ((awe + cha + con + dex + intel + mstr + pstr) >= 92) and (hpm >= 30):
        if please.say_yes_to("Is SPIE referee approved?"):
            vocation_list.append("Spie")

    if (cha >= 12) and ((dex + intel) >= 16):
        vocation_list.append("Veterinarian")

    return vocation_list


def bespoke_anthro_attributes_by_vocation(object: dict) -> None:
    """
    bestow improved attributes based on vocation type
    """
    vocation = object.Vocation
    adjustments = table.attributes_improve_by_vocation[vocation]

    ### create Level if not already there
    hack = 42 if hasattr(object, "Level") else exps_level_picker(object)

    for attribute, die_roll in adjustments.items():

        if die_roll == "mercshift":
            old_attribute = getattr(object, attribute)
            die_roll = str(object.Level) + "d6"
            new_attribute = 40 + please.roll_this(die_roll)
            new_attribute = (
                old_attribute if new_attribute < old_attribute else new_attribute
            )

        elif die_roll == "nothingshift":
            old_attribute = getattr(object, attribute)
            die_roll = str(object.Level) + "d50"
            new_attribute = 700 + please.roll_this(die_roll)
            new_attribute = (
                old_attribute if new_attribute < old_attribute else new_attribute
            )

        else:
            old_attribute = getattr(object, attribute)
            new_attribute = please.roll_this(die_roll)
            new_attribute = (
                old_attribute if new_attribute < old_attribute else new_attribute
            )

        print(f"{vocation} alters {attribute}: {old_attribute} -> {new_attribute}")
        setattr(object, attribute, new_attribute)
    return


def set_up_first_time(object):
    """
    activates the vocation function to update vocation record
    """
    vocations_function_pivot = {
        "Biologist": biologist,
        "Knite": knite,
        "Mechanic": mechanic,
        "Mercenary": mercenary,
        "Nomad": nomad,
        "Nothing": nothing,
        "Spie": spie,
        "Veterinarian": veterinarian,
    }

    vocations_function_pivot[object.Vocation](object)

    return


#########################################################
#                                                       #
#        Level/EXPS Management                          #
#                                                       #
#########################################################


def exps_level_bespoke(object: dict) -> None:
    """
    User assigns an EXPS level from 1 to 15
    """
    chosen_EXPS_level = int(input("What is the Bespoke Level? (1 to 15) "))
    chosen_EXPS_level = (
        1 if chosen_EXPS_level < 2 else chosen_EXPS_level
    )  # minimum of 1
    chosen_EXPS_level = (
        15 if chosen_EXPS_level > 15 else chosen_EXPS_level
    )  # maximum of 15
    object.Level = chosen_EXPS_level
    return


def random_exps_level(object: dict) -> None:
    """
    computer assigns a random weighted EXPS level from 1 to 10 and rarely 13
    """

    level = please.get_table_result(table.random_EXPS_levels_list)
    object.Level = level
    return


def exps_level_picker(object: dict) -> None:
    """
    only assigns a Level to the object.
    level adjustments elsewhere
    """

    option_list = ["Random", "Bespoke"]
    list_comment = "Choose a method for EXPS LEVEL?"
    Bespoke_Level = please.choose_this(option_list, list_comment)

    if Bespoke_Level == "Bespoke":
        exps_level_bespoke(object)
    elif Bespoke_Level == "Random":
        random_exps_level(object)
    else:
        print("Error: exps_level_picker")

    return


def convert_levels_to_exps(object: dict) -> int:
    """
    Returns an EXPS total based on the experience Level of the object
    does not alter object.
    """

    vocation = object.Vocation
    level = object.Level
    top_level = table.vocation_exps_levels[vocation]["top_level"]

    if level > top_level:
        exps_bottom = table.vocation_exps_levels[vocation]["top_amount"]
        full_levels = level - (table.vocation_exps_levels[vocation]["top_level"] + 1)
        exps_amount = int(
            exps_bottom
            + (full_levels * table.vocation_exps_levels[vocation]["rate"])
            + table.vocation_exps_levels[vocation]["rate"] / 2
        )

    else:

        for exps_range, level_number in table.vocation_exps_levels[vocation].items():
            if level == level_number:
                exps_amount = int(
                    (exps_range.stop - exps_range.start) / 2 + exps_range.start
                )
                break

    return exps_amount


def convert_exps_to_levels(object: dict) -> int:
    """
    Generates an experience Level based on the EXPS of the object
    Does not alter object.
    """

    exps_table = table.vocation_exps_levels[object.Vocation]
    exps_amount = object.EXPS

    # print("\n\nyou get past assignment in levelizer")

    top = exps_table["top_amount"]
    top_level = exps_table["top_level"]
    rate = exps_table["rate"]
    if exps_amount > top:
        new_level = top_level + round((exps_amount - top) / rate)
    else:
        for key in exps_table:
            if exps_amount in key:
                new_level = exps_table[key]
                break

    return new_level


def update_persona_exps(object: dict) -> None:
    """
    increases EXPS or Level and adjust object accordingly
    """
    initial_exps = object.EXPS
    initial_level = object.Level

    comment_list = [
        "Increasing EXPS from a SESSION",
        "Increasing a LEVEL",
        "Setting a fresh EXPS Total",
    ]
    experience = please.choose_this(comment_list, "Please select upgrade method.")

    if experience == "Increasing EXPS from a SESSION":
        session_exps = int(
            input(f"Present EXPS is {initial_exps}. How much EXPS do you want to add? ")
        )
        session_exps = 42 if session_exps < 1 else session_exps
        object.EXPS = initial_exps + session_exps
        object.Level = convert_exps_to_levels(object)

    elif experience == "Increasing a LEVEL":
        new_level = int(
            input(
                f"Present Level is {object.Vocation} {initial_level}. What is the NEW LEVEL? "
            )
        )
        if new_level - initial_level > 1:
            if please.say_yes_to(
                f"Do you really want to jump from {initial_level} level to {new_level} level?"
            ):
                print(f"New level will be a {new_level} level {object.Vocation}")
            else:
                print("Ok, 'll keep it the same")
                new_level = initial_level

        new_level = 0 if new_level < 1 else new_level
        object.Level = new_level

        if please.say_yes_to("Do you want to update EXPS for the new level?"):
            object.EXPS = convert_levels_to_exps(object)

    elif experience == "Setting a fresh EXPS Total":
        new_exps = int(
            input(f"Present EXPS Total is {initial_exps}. What is the new EXPS Total? ")
        )
        new_exps = 42 if new_exps < 42 else new_exps

        if please.say_yes_to("Do you want to update the LEVEL for the new EXPS TOTAL?"):
            object.Level = convert_exps_to_levels(object)

    if not please.say_yes_to(
        f"{object.Persona_Name}:  Level: {initial_level} -> {object.Level} and EXPS Total: {initial_exps} -> {object.EXPS}"
    ):
        object.EXPS = initial_exps
        object.Level = initial_level
        update_persona_exps(object)

    level_increase = object.Level - initial_level

    if (
        object.Vocation in [key for key in table.attributes_improve_by_vocation.keys()]
        and level_increase > 0
    ):
        # gifts are updated on the fly as the results are fixed
        update_interests(object, level_increase)
        update_skills(object, level_increase)
        return

    return


def update_gifts(object: dict) -> str:
    """
    returns a list of gifts based on the persona level
    """
    gift_table = []
    raw_gift_table = [
        value for key, value in table.vocations_gifts_pivot[object.Vocation].items()
    ]

    gift_table.append(raw_gift_table[0])
    if object.Level > 3:
        gift_table.append(raw_gift_table[1])
    if object.Level > 6:
        gift_table.append(raw_gift_table[2])

    return gift_table


def fresh_interests(object: dict, interest_rolls: int) -> list:
    """
    generates a fresh list of interests on first level
    """

    interest_table = table.vocations_interests_pivot[object.Vocation]
    interest_list = []
    while len(interest_list) < interest_rolls:
        interest = please.get_table_result(interest_table)
        interest_list.append(interest)

        if interest == "Extra Roll":
            interest_rolls += 1
            interest_list.pop()

        if interest == "Choose" and not object.Otto:
            interest_list.pop()
            choices = please.list_table_choices(interest_table)
            choice_comment = f"Choose a {object.Vocation} interest."
            choice = please.choose_this(choices, choice_comment)
            interest_list.append(choice)
        elif interest == "Choose" and object.Otto:
            interest_list.pop()

    return interest_list


def fresh_skills(object: dict, skill_rolls: int) -> list:
    """
    generates a fresh list of skills on first level
    """

    skills_table = []

    for skillist in table.vocations_skills_mashup[object.Vocation]:
        for key, value in skillist.items():
            if key != "die_roll" and key != "name":
                skills_table.append(value)

    skill_list = []
    while len(skill_list) < skill_rolls:
        skill = secrets.choice(skills_table)
        skill_list.append(skill)

        if skill == "Extra Roll":
            skill_rolls += 1
            skill_list.pop()

        if skill == "Choose" and not object.Otto:
            skill_list.pop()
            choices = please.list_table_choices(skills_table)
            choice_comment = f"Choose a {object.Vocation} skill."
            choice = please.choose_this(choices, choice_comment)
            skill_list.append(choice)
        elif skill == "Choose" and object.Otto:
            skill_list.pop()

    return skill_list


def update_interests(object: dict, interest_rolls: int) -> list:
    """
    expand the interests of the persona by choice or random
    """

    ### create a list of all interests
    all_interests = [
        val
        for lose, val in table.vocations_interests_pivot[object.Vocation].items()
        if lose != "die_roll"
        and lose != "name"
        and val != "Extra Roll"
        and val != "Choose"
    ]

    ### check to see if any extra rolls
    initial_number_of_rolls = interest_rolls
    for __ in range(initial_number_of_rolls):
        if (
            please.get_table_result(table.vocations_interests_pivot[object.Vocation])
            == "Extra Roll"
        ):
            interest_rolls += 1

    ### create interest list to return
    interest_list = []

    if object.Otto:
        for __ in range(interest_rolls):
            interest_list.append(secrets.choice(all_interests))
        return interest_list

    if please.say_yes_to(f"Would you like to pick each ({interest_rolls}) interests?"):
        for __ in range(interest_rolls):
            interest = please.choose_this(
                sorted(all_interests), "Choose an interest to add."
            )
            interest_list.append(interest)

    else:
        for __ in range(interest_rolls):
            interest_list.append(secrets.choice(all_interests))

    return interest_list


def update_skills(object: dict, skill_rolls: int) -> list:
    """
    returns a list to EXTEND object.Skills using object.Vocation and object.Level
    """
    ### create a list of all skills (3 tables) without Choose
    all_skills = []
    for sub_list in table.vocations_skills_mashup[object.Vocation]:
        for key, value in sub_list.items():
            if value != "1d100" and key != "Name" and value != "Choose":
                all_skills.append(value)

    ### check to see if any extra rolls, this is a hack for skills 2% chance of extra
    base_number = skill_rolls
    for __ in range(base_number):
        if secrets.choice(all_skills) == "Extra Roll":
            skill_rolls += 1

    ### strip Extra Roll from all_skills
    all_skills = [x for x in all_skills if x != "Extra Roll"]

    ### create skills_list to return
    skills_list = []

    if object.Vocation == "Spie":
        object.Spie_Fu = spie_martial_arts(object)

    if object.Otto:
        for __ in range(skill_rolls):
            skills_list.append(secrets.choice(all_skills))
        return skills_list

    if please.say_yes_to(f"Would you like to pick each ({skill_rolls}) skill?"):
        for __ in range(skill_rolls):
            interest = please.choose_this(
                sorted(all_skills), "Choose an interest to add."
            )
            skills_list.append(interest)

    else:
        for __ in range(skill_rolls):
            skills_list.append(secrets.choice(all_skills))

    return skills_list
