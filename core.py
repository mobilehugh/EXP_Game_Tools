import math
from dataclasses import asdict

import table
import please
import alien
import mutations


def initial_attributes(attributes_creating:table.PersonaRecord) -> table.PersonaRecord:
    """
    generates initial attributes for anthro, alien and robot personae 
    """
    # ANTHRO core attributes DIE ROLLS dictionary comprehension
    attribute_die_rolls = {
        key: value["dice"]
        for (key, value) in table.suggested_anthro_attributes.items()
        if key != "HPM"
    }
    
    for attribute in attribute_die_rolls:
        setattr(attributes_creating, attribute, please.roll_this(attribute_die_rolls[attribute]))

    # ALIEN REASSIGNMENTS of CON, DEX, INT, MSTR, PSTR
    if attributes_creating.FAMILY == "Alien":
        # alien core attributes DIE ROLLS dictionary comprehension
        attribute_die_rolls = {
            key: value["dice"]
            for (key, value) in table.alien_suggested_attributes.items()
            if key != "HPM"
        }   
        for attribute in attribute_die_rolls:
            setattr(attributes_creating, attribute, please.roll_this(attribute_die_rolls[attribute]))

    # ROBOT ADJUSTMENTS to CON, DEX, INT, MSTR, PSTR
    if attributes_creating.FAMILY == "Robot":
        # must assign robot primes
        attributes_creating.CON_Prime = please.roll_this("1d4")
        attributes_creating.DEX_Prime = please.roll_this("1d4")
        attributes_creating.INT_Prime = please.roll_this("1d4")
        attributes_creating.PSTR_Prime = please.roll_this("1d4")

        # reassign die rolls based on primes
        attributes_creating.CON = please.roll_this(table.robot_attributes[attributes_creating.CON_Prime]["CON"])
        attributes_creating.DEX = please.roll_this(table.robot_attributes[attributes_creating.DEX_Prime]["DEX"])
        attributes_creating.INT = please.roll_this(table.robot_attributes[attributes_creating.INT_Prime]["INT"]) 
        attributes_creating.PSTR = please.roll_this(table.robot_attributes[attributes_creating.PSTR_Prime]["PSTR"])
        attributes_creating.MSTR = 0

    return attributes_creating # modified by side effects

def hit_points_max(hit_points_creating:table.PersonaRecord) -> table.PersonaRecord:
    """
    generates initial hit points max for aliens, anthros and robots BY side effects
    """
    # anthro HPM based on CON only

    if hit_points_creating.FAMILY == "Anthro":
        con = hit_points_creating.CON
        dice = math.ceil(con / 2)
        die_roll = str(dice) + "d8+" + str(con)
        hpm = please.roll_this(die_roll)

    # alien HPM based on CON an SIZE
    elif hit_points_creating.FAMILY == "Alien":
        size = hit_points_creating.Size_Cat
        con = str(hit_points_creating.CON)
        hpm = please.roll_this(con + table.alien_HPM_size_and_dice[size])

        if hit_points_creating.Size_Cat == "Minute":
            hpm = math.ceil(hit_points_creating.HPM * ((hit_points_creating.Wate / 1000)))
            
   
        elif hit_points_creating.FAMILY == "Robot":
        # if hit_points_creating.FAMILY == "Robot":
        # string value per robot multiplied by CON
        # present structure of robots as functions does not allow for values just yet
        # the HPM is calculated and assigned by the function 
            pass
        
    # apply the appropriate HPM
    hit_points_creating.HPM = hpm

    return table.PersonaRecord # altered by side effect


def wate_allowance(wate_allowance:table.PersonaRecord) -> table.PersonaRecord:
    ''' determine wate allowance for alien, anthro and robot'''

    # anthro wate allowance is straight from table
    wate_allowed = table.wate_allowance_and_PSTR[wate_allowance.PSTR]
    
    # alien modifies wate allowance by alien size
    if wate_allowance.FAMILY == "Alien":
        size_mod = table.alien_size_and_WA[wate_allowance.Size_Cat]
        wate_allowed = round(float(wate_allowed * size_mod),1)
    
    # robot modifies wate allowance by PSTR prime
    elif wate_allowance.FAMILY == "Robot": 
        wate_allowed = wate_allowed * wate_allowance.PSTR_Prime

    wate_allowance.WA = wate_allowed

    return wate_allowance # is modified by side effect

def movement_rate(moving_time: table.PersonaRecord) -> table.PersonaRecord:
    """
    dexterity determines movement rate for anthro, alien, robot
    """

    # anthro movement is determined by DEX
    moving_rate = table.anthro_movement_rate_and_DEX[moving_time.DEX]

    # robot movement is double anthro
    if moving_time.FAMILY == "Robot":
        moving_rate = moving_rate * 2

    elif moving_time.FAMILY == "Alien":
        moving_rate = moving_time.DEX
        alien.assign_terrain_movements(moving_time)

    setattr(moving_time, "Move", moving_rate)

    return moving_time # is modified by side effect

def base_armour_rating(armourize: table.PersonaRecord) -> table.PersonaRecord:
    """
    determine armour rating of anthro, alien and robots
    """
    if armourize.FAMILY == "Anthro":
        rating = 500 + (6 * armourize.DEX)

    elif armourize.FAMILY == "Alien":
        rating = 500 + please.roll_this("3d100")

    elif armourize.FAMILY == "Robot":
        rating = 700

    armourize.AR = rating

    return armourize # is altered by side effects


def assign_persona_name(avatar_name: table.PersonaRecord) -> table.PersonaRecord:
    """
    I know it is only only one line, but I want to make build_show work
    """
    input(f'you are at assign_persona_name')
    ### get mundane terran name of the player
    avatar_name.Persona_Name = please.input_this(f'\nPlease input your PERSONA NAME: ')

    return avatar_name # is modified by side effect


def descriptive_attributes(descriptive: table.PersonaRecord) -> table.PersonaRecord:
    """
    persona attribute shifts based on descriptive words
    """
    # todo descriptive attributes need a logic check 
    # todo descriptive attributes missing size, age, AR, 
    # todo descriptive knock on effects of PSTR -> WA, DEX -> Move, CON -> HPS
    # builds a combined table 
    if descriptive.FAMILY == "Alien":
        upwards_table = {**table.descriptive_attributes_higher, **table.alien_descriptive_attributes}

    elif descriptive.FAMILY == "Robot":
        upwards_table = {**table.descriptive_attributes_higher, **table.alien_descriptive_attributes}
        
    else:
        upwards_table = table.descriptive_attributes_higher

    upwards_list = list(upwards_table.keys())
    downwards_list = list(table.descriptive_attributes_lower.keys())
    choices = sorted(upwards_list + downwards_list)
    choices.insert(0,"EXIT")

    altering_descriptor = "Start"
    while altering_descriptor != "EXIT":
        choice_comment = "Choose an  attribute descriptor? "
        altering_descriptor = please.choose_this(choices, choice_comment)
        if altering_descriptor in upwards_list:
            alter_attribute = upwards_table[altering_descriptor][0]
            alter_amount = upwards_table[altering_descriptor][1]

            if altering_descriptor in ["Fast", "Resilient", "Independent", "Efficient", "Adaptable"]:
                before = getattr(descriptive, alter_attribute)
                setattr(descriptive, alter_attribute, before*int(alter_amount))
                if altering_descriptor == "Resilient":
                    descriptive.HPM = descriptive.HPM if descriptive.HPM > 70 else 70
                   
            else:
                old_attribute = getattr(descriptive, alter_attribute)
                new_attribute = please.roll_this(alter_amount)
                new_attribute = new_attribute if new_attribute > old_attribute else old_attribute + please.roll_this("1d3")
                setattr(descriptive, alter_attribute, new_attribute)

        if altering_descriptor in downwards_list:
            alter_attribute = table.descriptive_attributes_lower[altering_descriptor][0]
            alter_amount = table.descriptive_attributes_lower[altering_descriptor][1]
            if altering_descriptor == "Slow":
                descriptive.Move = math.floor(descriptive.Move/2)
            else:
                new_attribute = please.roll_this(alter_amount)
                setattr(descriptive, alter_attribute, new_attribute)
               
        if altering_descriptor == "Exit":
            exit

    return descriptive # is altered by side effect


def manual_persona_update(updating: table.PersonaRecord) -> table.PersonaRecord:
    ''' painfully update every element in persona record'''
    FORBIDDEN = ["Player_Name", "FAMILY", "FAMILY_TYPE", "Fallthrough", "RP", "Show", "Bin", "Date_Created", "Date_Updated", "ID", "File_Name"]

    print(f"Manually adjusting {len(asdict(updating).keys())} items in {updating.Persona_Name}")
    for attr, value in asdict(updating).items():

        if attr not in FORBIDDEN:
            print()
            if please.say_no_to(f'Do you want to change {attr} from {value}? '):
                continue
            else:
                change = please.input_this(f'Change {attr} from {value} to what? ')
                setattr(updating, attr, change)

    print()

    for attr, value in asdict(updating).items():
        if attr not in FORBIDDEN:
            print(f'{attr} = {value}')

    return updating # altered by side effects in this function


def mutations_bespoke(mutate_RP: table.PersonaRecord) -> table.PersonaRecord:

    ### determine RP anthro mutations
    choices = ["Family Determined", "Bespoke", "Random"]
    choice_comment = "What selection method do you want for MUTATIONS?"
    method_type_selection = please.choose_this(choices, choice_comment)

    if method_type_selection == "Family Type Determined":
        mental_amount, physical_amount = mutations.biologic_mutations_number(mutate_RP)
        mutations.mutation_assignment(mutate_RP,mental_amount, physical_amount,"any")

    elif method_type_selection == "Bespoke":
        mutations.pick_bespoke_mutation(mutate_RP)

    # todo exit get's sorted because choose this sorts it
    elif method_type_selection == "Random":
        more_random = True

        while more_random:
            mutations.single_random_mutation(mutate_RP, ['any'])
            if not please.say_yes_to("Give me another mutation! "):
                break

    return mutate_RP # altered by side effect at functions outside this function

