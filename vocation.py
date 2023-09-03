import math
import secrets
import please
import table

#########################################################
#                                                       
#        vocation functions                             
#                                                       
#########################################################

'''
the vocation functions are for start up for assignments at first level
the persona record is adjusted by side effect 

"Biologist": biologist,
"Knite": knite,
"Mechanic": mechanic,
"Mercenary": mercenary,
"Nomad": nomad,
"Nothing": nothing,
"Spie": spie,
"Veterinarian": veterinarian,

GIFTS are level dependent and calculation on the fly when output is needed
INTERESTS are added to the Interests [] as strings
SKILLS are added to the Skills [] as strings

'''

def biologist(get_a_job: table.PersonaRecord) -> table.PersonaRecord:
    """
    Set up the biologist vocation.
    """
    interest_rolls = math.ceil(get_a_job.AWE / 4)
    skill_rolls = math.ceil(get_a_job.INT / 4)
    get_a_job.Interests = fresh_interests(get_a_job, interest_rolls)
    get_a_job.Skills = fresh_skills(get_a_job, skill_rolls)

    return get_a_job # modified by side effects


def knite(get_a_job: table.PersonaRecord) -> table.PersonaRecord:
    """
    Set up the knite vocation.
    """
    interest_rolls = math.ceil(get_a_job.MSTR / 4)
    skill_rolls = math.ceil(get_a_job.INT / 3)
    get_a_job.Interests = fresh_interests(get_a_job, interest_rolls)
    get_a_job.Skills = fresh_skills(get_a_job, skill_rolls)

    return get_a_job # modified by side effects


def mechanic(get_a_job: table.PersonaRecord) -> table.PersonaRecord:
    """
    Set up the mechanic vocation.
    """
    interest_rolls = math.ceil(get_a_job.INT / 4)
    skill_rolls = math.ceil(get_a_job.INT / 3)
    get_a_job.Interests = fresh_interests(get_a_job, interest_rolls)
    get_a_job.Skills = fresh_skills(get_a_job, skill_rolls)

    return get_a_job # modified by side effects


def mercenary(get_a_job: table.PersonaRecord) -> table.PersonaRecord:
    """
    Set up the mercenary vocation.
    """
    interest_rolls = math.ceil(get_a_job.INT / 4)
    skill_rolls = math.ceil(get_a_job.DEX / 3)
    get_a_job.Interests = fresh_interests(get_a_job, interest_rolls)
    get_a_job.Skills = fresh_skills(get_a_job, skill_rolls)

    return get_a_job # modified by side effects


def nomad(get_a_job: table.PersonaRecord) -> table.PersonaRecord:
    """ 
    set up the nomad vocation.
    """
    interest_rolls = math.ceil(get_a_job.INT / 4)
    skill_rolls = math.ceil(get_a_job.AWE / 3)
    get_a_job.Interests = fresh_interests(get_a_job, interest_rolls)
    get_a_job.Skills = fresh_skills(get_a_job, skill_rolls)

    return get_a_job # modified by side effects


def nothing(nothing_happening: table.PersonaRecord) -> table.PersonaRecord:
    """
    set up the nothing vocation.
    """
    interest_rolls = math.ceil(nothing_happening.SOC / 200)
    skill_rolls = math.ceil(nothing_happening.INT / 3)
    nothing_happening.Interests = fresh_interests(nothing_happening, interest_rolls)
    nothing_happening.Skills = fresh_skills(nothing_happening, skill_rolls)

    ### Vocation aspiration is specific to the nothing vocation
    if nothing_happening.Fallthrough:
        vocation_desired = secrets.choice(list(table.vocation_aspiration_exps.keys()))

    else:
        choices = list(table.vocation_aspiration_exps.keys())
        comment = "A nomad needs a VOCATIONAL ASPIRATION. Please pick one. "
        vocation_desired = please.choose_this(choices, comment)

    nothing_happening.Vocay_Aspiration = vocation_desired
    nothing_happening.Vocay_Aspiration_EXPS = table.vocation_aspiration_exps[vocation_desired]

    return nothing_happening # modified by side effects


def spie(get_a_job: table.PersonaRecord) -> table.PersonaRecord:
    """
    set up the Spie vocation
    """
    interest_rolls = math.ceil(get_a_job.INT / 4)
    skill_rolls = math.ceil(get_a_job.DEX / 3)
    get_a_job.Interests = fresh_interests(get_a_job, interest_rolls)
    get_a_job.Skills = fresh_skills(get_a_job, skill_rolls)

    return get_a_job # modified by side effects


def spie_martial_arts(spie_fu_record: table.PersonaRecord) -> str:
    """
    return the spie fu string based on level 
    """

    # collect data from martial arts table
    spied_fu = table.spie_martial_arts[
        spie_fu_record.Level if spie_fu_record.Level < 10 else 10
    ]

    # martial armour rating
    martial_ar = spie_fu_record.AR + spied_fu["AR"]

    return  f'AR: {martial_ar} DMG: {spied_fu["Damage"]} Attacks: {spied_fu["freq"]} Order: {spied_fu["order"]}.'

def veterinarian(get_a_job: table.PersonaRecord) -> table.PersonaRecord:
    """
    set up the Veterinarian vocation
    """
    interest_rolls = math.ceil(get_a_job.INT / 4)
    skill_rolls = math.ceil(get_a_job.INT / 3)
    get_a_job.Interests = fresh_interests(get_a_job, interest_rolls)
    get_a_job.Skills = fresh_skills(get_a_job, skill_rolls)

    return get_a_job # modified by side effects


def attribute_determined(get_a_job: table.PersonaRecord) -> list:
    """
    returns a list of eligible vocations determined by attribute
    """

    # find eligible vocations for any attribute set

    vocation_list = []

    if (get_a_job.AWE + get_a_job.INT) >= 18:
        vocation_list.append("Biologist")

    if (get_a_job.DEX >= 15) and (get_a_job.MSTR >= 18) and (get_a_job.HPM >= 25):
        if please.say_yes_to("Is KNITE referee approved?"):
            vocation_list.append("Knite")

    if get_a_job.INT >= 13:
        vocation_list.append("Mechanic")

    if ((get_a_job.CON + get_a_job.DEX + get_a_job.PSTR) >= 22) and (get_a_job.HPM >= 40):
        vocation_list.append("Mercenary")

    if (get_a_job.AWE >= 10) and (get_a_job.CON >= 6) and (get_a_job.INT >= 5) and (get_a_job.HPM >= 20):
        vocation_list.append("Nomad")

    #  any persona can pursue Nothing vocation
    vocation_list.append("Nothing")

    if ((get_a_job.AWE + get_a_job.CHA + get_a_job.CON + get_a_job.DEX + get_a_job.INT + get_a_job.MSTR + get_a_job.PSTR) >= 92) and (get_a_job.HPM >= 30):
        if please.say_yes_to("Is SPIE referee approved?"):
            vocation_list.append("Spie")

    if (get_a_job.CHA >= 12) and ((get_a_job.DEX + get_a_job.INT) >= 16):
        vocation_list.append("Veterinarian")

    return vocation_list


def attributes_to_vocation(get_a_job: table.PersonaRecord) -> table.PersonaRecord:
    """
    bestow improved attributes by vocation type
    """
    vocation = get_a_job.Vocation

    for attribute, die_roll in table.attributes_improve_by_vocation[vocation].items():

        if die_roll == "mercshift":
            old_attribute = getattr(get_a_job, attribute)
            die_roll = str(get_a_job.Level) + "d6"
            new_attribute = 40 + please.roll_this(die_roll)
            new_attribute = old_attribute if new_attribute < old_attribute else new_attribute
            

        elif die_roll == "nothingshift":
            old_attribute = getattr(get_a_job, attribute)
            die_roll = str(get_a_job.Level) + "d50"
            new_attribute = 700 + please.roll_this(die_roll)
            new_attribute = old_attribute if new_attribute < old_attribute else new_attribute

        else:
            old_attribute = getattr(get_a_job, attribute)
            new_attribute = please.roll_this(die_roll)
            new_attribute = old_attribute if new_attribute < old_attribute else new_attribute

        setattr(get_a_job, attribute, new_attribute)

    return get_a_job # is adjusted by side effect


def set_up_first_time(get_a_job: table.PersonaRecord) -> table.PersonaRecord:
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

    vocations_function_pivot[get_a_job.Vocation](get_a_job)

    return get_a_job # is adjusted by side effect

#########################################################
#                                                       #
#        Level/EXPS Management                          #
#                                                       #
#########################################################

def exps_level_picker(level_persona: table.PersonaRecord) -> table.PersonaRecord:
    """
    only assigns a Level to the get_a_job.
    level adjustments elsewhere
    """
    if level_persona.Fallthrough or level_persona.Bespoke:
        level_choices = [lvl for lvl in range(1,16)]

    list_comment = "Choose an EXPS LEVEL?"
    level_persona.Level = please.choose_this(level_choices, list_comment, level_persona)

    return level_persona # is adjusted by side effect


def convert_levels_to_exps(get_a_job: table.PersonaRecord, new_level:int = 0) -> int:
    """
    Returns an EXPS total based on the experience Level of the get_a_job
    does not alter get_a_job.
    """

    vocation = get_a_job.Vocation
    exps_table = table.vocation_exps_levels[vocation]

    exp_ranger = {l:x for x, l in exps_table.items() if isinstance(x, tuple)}
    level = new_level if new_level > get_a_job.Level else get_a_job.Level
    top_level = exps_table["top_level"]

    if level > top_level:
        exps_bottom = exps_table["top_amount"]
        full_levels = level - (exps_table["top_level"] + 1)
        exps_amount = int(
            exps_bottom
            + (full_levels * exps_table["rate"])
            + exps_table["rate"] / 2
        )

    else:
        bottom, top = exp_ranger[level]
        exps_amount = round(bottom + (top-bottom)/2)

    return exps_amount


# todo double check that exps in is related to get_a_job.EXPS
def convert_exps_to_levels(get_a_job: table.PersonaRecord, new_exps = 0) -> int:
    """
    Generates an experience Level based on the EXPS of the get_a_job
    Does not alter get_a_job.
    """
    exps_table = table.vocation_exps_levels[get_a_job.Vocation]
    exps_amount = new_exps if new_exps > get_a_job.Level else get_a_job.Level
    top = exps_table["top_amount"]
    top_level = exps_table["top_level"]
    rate = exps_table["rate"]

    level_ranger = {x:l for x, l in exps_table.items() if isinstance(x, tuple)} # reverses from level -> EXPS

    if exps_amount > top:
        new_level = top_level + math.ceil((exps_amount - top) / rate)
    else:
        for extuple, level in level_ranger.items():
            if exps_amount >= extuple[0] and exps_amount <= extuple[1]:
                new_level = level
                break

    return new_level

#########################################################
#                                                       
#        gifts, interests, skills management                
#                                                       
#########################################################


def update_gifts(returning_gifts: table.PersonaRecord) -> list:
    """
    returns a list of gifts based on the persona level
    """
    gift_list = []
    gift_table = list(table.vocations_gifts_pivot[returning_gifts.Vocation].values())
    
    gift_list.append(gift_table[0])
    if returning_gifts.Level > 3:
        gift_list.append(gift_table[1])
    if returning_gifts.Level > 6:
        gift_list.append(gift_table[2])

    return gift_list


def fresh_interests(get_a_job: table.PersonaRecord, interest_rolls: int) -> list:
    """
    generates a fresh list of interests on first level
    """

    interest_table = table.vocations_interests_pivot[get_a_job.Vocation]
    interest_list = []
    while len(interest_list) < interest_rolls:
        interest = please.get_table_result(interest_table)
        interest_list.append(interest)

        if interest == "Extra Roll":
            interest_rolls += 1
            interest_list.pop()

        if interest == "Choose" and not get_a_job.Fallthrough:
            interest_list.pop()
            choices = please.list_table_choices(interest_table)
            choice_comment = f"Choose a {get_a_job.Vocation.upper()} INTEREST."
            chosen = please.choose_this(choices, choice_comment)
            interest_list.append(chosen)

        elif interest == "Choose" and get_a_job.Fallthrough:
            interest_list.pop()

    return interest_list


def fresh_skills(get_a_job: table.PersonaRecord, skill_rolls: int) -> list:
    """
    generates a fresh list of skills on first level
    """
    
    ### vocation skills can be combined from multiple tables
    skills_table = []
    for skillist in table.vocation_skills_tables[get_a_job.Vocation]:
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

        if skill == "Choose" and not get_a_job.Fallthrough:
            skill_list.pop()
            choices = please.list_table_choices(skills_table)
            choice_comment = f"Choose a {get_a_job.Vocation} skill."
            chosen = please.choose_this(choices, choice_comment)
            skill_list.append(chosen)

        elif skill == "Choose" and get_a_job.Fallthrough:
            skill_list.pop()

    return skill_list


def update_interests(get_a_job: table.PersonaRecord, interest_rolls: int) -> list:
    """
    returns a list to EXTEND get_a_job.Interests using get_a_job.Vocation and increase in level
    """
    if get_a_job.Vocation in ["Alien", "Robot"]:
        # no work for you here aliens and robots
        return []


    ### create a list of all interests
    do_not_include = ["Choose", "name", "die_roll"]

    all_interests = [
            val
            for lose, val in table.vocations_interests_pivot[get_a_job.Vocation].items()
            if lose not in do_not_include and  val not in do_not_include
        ]
    
    ### check to see if any extra rolls
    initial_number_of_rolls = interest_rolls
    for _ in range(initial_number_of_rolls):
        if (
            please.get_table_result(table.vocations_interests_pivot[get_a_job.Vocation])
            == "Extra Roll"
        ):
            interest_rolls += 1

        ### strip Extra Roll from all_skills
    all_interests = [x for x in all_interests if x != "Extra Roll"]

    ### create interest list to return
    interest_list = []

    if get_a_job.Fallthrough:
        for _ in range(interest_rolls):
            interest_list.append(secrets.choice(all_interests))
        return interest_list

    if please.say_yes_to(f"Would you like to pick the ({interest_rolls}) INTEREST(s)? "):
        for _ in range(interest_rolls):
            interest = please.choose_this(
                sorted(all_interests), "Choose an INTEREST to add. "
            )
            interest_list.append(interest)

    else:
        for _ in range(interest_rolls):
            interest_list.append(secrets.choice(all_interests))

    return interest_list


def update_skills(get_a_job: table.PersonaRecord, skill_rolls: int) -> list:
    """
    returns a list to EXTEND get_a_job.Skills using get_a_job.Vocation and get_a_job.Level
    """

    if get_a_job.Vocation in ["Alien", "Robot"]:
        # no skills for you here aliens and robots
        return []

    ### create a list of all skills (3 tables) without Choose
    all_skills = []
    for sub_list in table.vocation_skills_tables[get_a_job.Vocation]:
        for key, value in sub_list.items():
            if value != "1d100" and key != "Name" and value != "Choose":
                all_skills.append(value)

    ### check to see if any extra rolls, this is a hack for skills 2% chance of extra
    base_number = skill_rolls
    for _ in range(base_number):
        if secrets.choice(all_skills) == "Extra Roll":
            skill_rolls += 1

    ### strip Extra Roll from all_skills
    all_skills = [x for x in all_skills if x != "Extra Roll"]

    ### create skills_list to return
    skills_list = []

    if get_a_job.Vocation == "Spie":
        get_a_job.Spie_Fu = spie_martial_arts(get_a_job)

    if get_a_job.Fallthrough:
        for _ in range(skill_rolls):
            skills_list.append(secrets.choice(all_skills))
        return skills_list

    if please.say_yes_to(f"Would you like to pick each ({skill_rolls}) skill?"):
        for _ in range(skill_rolls):
            interest = please.choose_this(
                sorted(all_skills), "Choose an interest to add."
            )
            skills_list.append(interest)

    else:
        for _ in range(skill_rolls):
            skills_list.append(secrets.choice(all_skills))

    return skills_list


def update_persona_exps(record_to_update: table.PersonaRecord) -> table.PersonaRecord:
    """
    increases EXPS or Level and adjust record_to_update accordingly
    also updates interest and skills if appropriate
    """
    initial_exps = record_to_update.EXPS
    initial_level = record_to_update.Level
    vocation = record_to_update.Vocation

    comment_list = [
        "Change EXPS",
        "Change LEVEL",
        "Reset EXPS",
    ]
    experience = please.choose_this(comment_list, f"Presently {vocation} level {initial_level} with {initial_exps} EXPS.")

    if experience == "Change EXPS":
        session_exps = int(
            please.input_this(f"Present EXPS is {initial_exps}. How much EXPS do you want to add? ")
        )
        session_exps = 42 if initial_exps - session_exps < 42 else session_exps #protects from negative EXPS

        new_level = convert_exps_to_levels(record_to_update, session_exps)
        new_exps = initial_exps + session_exps

    elif experience == "Change LEVEL":
        new_level = int(
            please.input_this(
                f"Present Level is {vocation} level {initial_level}. What is the NEW LEVEL? "
            )
        )
        new_level = initial_level if new_level < 1 else new_level #protects from negative LVL
        new_exps = convert_levels_to_exps(record_to_update, new_level)

        # record_to_update.Level = new_level

    elif experience == "Reset EXPS":
        new_exps = int(
            please.input_this(f"Present EXPS Total is {initial_exps}. What is the new EXPS TOTAL? ")
        )
        new_exps = 42 if new_exps < 42 else new_exps # protects from negative EXPS
        new_level = convert_exps_to_levels(record_to_update)

        if not please.say_yes_to(f"{vocation} Level: {initial_level} -> {new_level} and EXPS: {initial_exps} -> {new_exps}"):
            update_persona_exps(record_to_update)




    ### approve or negate the changes. if negated return to update EXPS

    if  please.say_yes_to(
        f"{vocation} Level: {initial_level} -> {new_level} and EXPS: {initial_exps} -> {new_exps}"
    ):
        record_to_update.EXPS = new_exps
        record_to_update.Level = new_level
        please.store_this(record_to_update)
    else:
        update_persona_exps(record_to_update) # return to top

    ### check for adding abilities via vocation
    level_increase = record_to_update.Level - initial_level

    ### updates interests and skills if level increase and NOT alien or robot
    if (
        record_to_update.Vocation in [key for key in table.attributes_improve_by_vocation.keys()]
        and level_increase > 0
    ):
        # gifts are updated on the fly as the results are fixed
        new_interests = update_interests(record_to_update, level_increase)
        record_to_update.Interests.extend(new_interests)
        new_skills = update_skills(record_to_update, level_increase)
        record_to_update.Skills.extend(new_skills)
        please.store_this(record_to_update)

    return record_to_update # altered by side effect in this function and others


