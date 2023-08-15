import math
from secrets import choice
from dataclasses import dataclass


import anthro
import outputs
import please
import table
import vocation
import core
import mutations
import toy


# set up RoboticRecord
@dataclass
class RobotRecord(table.Robotic):
    FAMILY: str = "Robot"

def robot_workflow():
    """
    player robot versus referee person vs persona maintenance
    """

    # clearance for Clarence
    please.clear_console()

    workflow_function_map = {
        "Fresh Robot (New Player)": fresh_robot,
        "Bespoke Robot": bespoke_robot,
        "Random Robot": rando_robot,
        "Maintenance":please.do_referee_maintenance,
    }

    comment = "Choose a robot workflow:"
    choices = list(workflow_function_map.keys())
    workflow_desired = please.choose_this(choices, comment)

    if workflow_desired in workflow_function_map:
        workflow_function_map[workflow_desired]()

def control_factor(controlling: RobotRecord) -> int:
    """
    returns a int value control factor
    """
    return  controlling.INT + (controlling.INT_Prime * controlling.Level)

def robotic_sensors(eye_eye:RobotRecord) -> list:
    ''' creates a list robot sensors'''
    sensor_list = []
    for _ in range(math.ceil(eye_eye.AWE / 4)):
        sensor_list.append(please.get_table_result(table.robotic_sensor_types))
    return sensor_list # changed by side effect

def robotic_locomotion(move_it:RobotRecord) -> str:
    '''create a locomotion string'''

    primary, secondary = please.get_table_result(table.primary_robotic_locomotion)


    if move_it.FAMILY_TYPE == "Android":
        return f'{move_it.Base_Family} legs' 
    
    if move_it.FAMILY_TYPE == "Social":
        return f'{move_it.Base_Family} like legs'
    
    if 'd' in secondary:
        return f'{please.roll_this(secondary)} {primary}'

    if secondary == "Secondary":
        primary = f'{primary} {choice(["moving", "pushing", "pulling"])} {please.get_table_result(table.secondary_robotic_locomotion).lower()}' 

    # if secondary = "None" falls to generic return 

    return primary

def list_eligible_robot_types(choosing: RobotRecord) -> list:
    """
    makes a 4 character string from primes to list of robots type options
    """
    auto_picker = (
        f"{choosing.CON_Prime}{choosing.DEX_Prime}{choosing.INT_Prime}{choosing.PSTR_Prime}"
    )

    return table.auto_prime_select_robot_type[auto_picker]

def robot_hite_wate_calc(sizer: RobotRecord) -> RobotRecord:
    """
    fills the robot's size, wate and hite attributes
    """

    if sizer.FAMILY_TYPE in ["Android", "Social",]: 
        return  sizer # if it's an android or social already calculated

    ### sizer.Size is determined by robot type

    ### get wate from size of robot
    sizer.Wate = please.roll_this(table.robot_size_to_wate[sizer.Size_Cat]["wate"])
    sizer.Wate_Suffix = table.robot_size_to_wate[sizer.Size_Cat]["suffix"]

    ### get hite from wate to hite table
    kilo_conv = 1 if sizer.Size_Cat == "NaNo" else sizer.Wate

    for hite_range, roll in table.robot_wate_to_hite.items():
        if kilo_conv in hite_range:
            sizer.Hite = please.roll_this(roll)
            break
    sizer.Hite_Suffix = "cms" if sizer.Wate < 10_000 else "meters"

    return sizer # modified by side effect


def robotic_peripherals(perry: RobotRecord, number: int) -> list:
    '''generates a list of robotic peripherals'''
    
    peripheral_list = []
    secondary_number = 0

    ### add the primary, less fancy, peripherals
    while len(peripheral_list) < number:
        peripheral = please.get_table_result(table.primary_robotic_peripheral)
        peripheral_list.append(peripheral)

        if peripheral == "Extra Roll":
            number += 1
            peripheral_list.pop()

        elif peripheral == "Choose":
            peripheral_list.pop()
            choices = please.list_table_choices(table.primary_robotic_peripheral)
            chosen = please.choose_this(choices, "Choose a primary peripheral")
            peripheral_list.append(chosen)

        elif peripheral == "Secondary":
            peripheral_list.pop()
            secondary_number += 1

    if secondary_number == 0:  # all done here
        return peripheral_list

    ### add the secondary, fancy, peripherals
    while secondary_number != 0:
        peripheral = please.get_table_result(table.secondary_robotic_peripheral)
        peripheral_list.append(peripheral)
        secondary_number -= 1

        if peripheral == "Extra Roll":
            secondary_number += 2  # always unsure about +1 or +2
            peripheral_list.pop()

        elif peripheral == "Choose":
            peripheral_list.pop()
            choices = please.list_table_choices(table.secondary_robotic_peripheral)
            chosen = please.choose_this(choices, "Choose a secondary peripheral")
            peripheral_list.append(choice)

    for position, peripheral in enumerate(peripheral_list):

        if peripheral == "Vocation Computer":
            all_vocations = [key for key in table.attributes_improve_by_vocation.keys()]
            new_peripheral = f"{choice(all_vocations)} vocation computer"
            peripheral_list[position] = new_peripheral

        elif peripheral == "Cybernetic Part":
            toy_type = toy.gimme_one("Any")
            new_peripheral = f"A hard wired toy - {toy_type}"
            peripheral_list[position] = new_peripheral

        elif peripheral == "Vocation":
            all_vocations = [
                key
                for key in table.attributes_improve_by_vocation.keys()
                if key != "Knite"
            ]
            perry.Vocation = choice(all_vocations)
            peripheral_list[position] = f"Robot has the vocation {perry.Vocation}"

        elif peripheral.split(" ")[0] == "Detect":
            peripheral_list[position] = f"{peripheral} {perry.AWE} km range"

        elif peripheral.split(" ")[0] == "Identify":
            peripheral_list[
                position
            ] = f"{peripheral} {2*perry.INT * perry.INT_Prime}%"

        elif peripheral == "Heightened CF":
            perry.CF = perry.CF * 2

        elif peripheral == "Increase Speed":
            perry.Move = perry.Move * please.roll_this("1d4+1")

        elif peripheral == "Increase WA":
            perry.WA = perry.WA * please.roll_this("1d6+1")

        elif peripheral == "Mental Mutation":
            mutations.single_random_mutation(perry, ['mental', 'no-defect'])

        elif peripheral == "Physical Mutation":
            mutations.single_random_mutation(perry, ['physical', 'no-defect'])


    return peripheral_list # also side effects on perry


### robot offensive systems

# todo should these 4 functions be inside of robot_offensive_rolls?
def attack_one_rolls(rolls_list:list) -> list:
    '''adjusts attack_rolls_list (# of rolls) via recursion'''
    
    if please.do_1d100_check(25):
        rolls_list = attack_two_rolls(rolls_list)
    else:
        rolls_list[1] += 1
 
    return rolls_list

def attack_two_rolls(rolls_list:list) -> list:
    '''adjusts attack_rolls_list (# of rolls) via recursion'''

    die_roll = please.roll_this("1d100")

    if die_roll in range(1,11):
        for _ in range(2):
            rolls_list = attack_one_rolls(rolls_list)

    elif die_roll in range(90,101):
        rolls_list = attack_three_rolls(rolls_list)

    else:
        rolls_list[2] += 1

    return rolls_list

def attack_three_rolls(rolls_list: list) -> list:
    '''adjusts attack_rolls_list (# of rolls) via recursion'''

    die_roll = please.roll_this("1d100")

    if die_roll in range(1,16):
        for _ in range(3):
            rolls_list = attack_one_rolls(rolls_list)

    elif die_roll in range(16,31):
        for _ in range(2):
            rolls_list = attack_two_rolls(rolls_list)

    elif die_roll in range(95,101):
        rolls_list = attack_four_rolls(rolls_list)

    else:
        rolls_list[3] += 1

    return rolls_list

def attack_four_rolls(rolls_list: list) -> list:
    '''adjusts attack_rolls_list (# of rolls) via recursion'''
    die_roll = please.roll_this("1d100")

    if die_roll in range(1,11):
        for _ in range(4):
            rolls_list = attack_two_rolls(rolls_list)

    elif die_roll in range(11, 21):
        for _ in range(3):
            rolls_list = attack_three_rolls(rolls_list)
    
    else:
        rolls_list[4] += 1

    return rolls_list

def robot_offensive_rolls(offenses: list) -> list:
    """
    takes a list of tuples (attack_table,attack#) and returns list[]
    """
    attack_rolls_list = [0,0,0,0,0]  # list of the robot attacks

    for table,rolls in offenses:
        for _ in range(rolls):
            attack_rolls_list = table(attack_rolls_list)

    return attack_rolls_list

def robot_offensive_systems(offender: RobotRecord, rolls_list: list) -> RobotRecord:
    '''takes list of rolls for attack tables and adds to robot persona Attacks'''

    attack_tables_pivot = [table.robot_ram_dam, table.attack_table_one, table.attack_table_two, table.attack_table_three, table.attack_table_four]
    fancy_attacks = {"Electro":"+2d8 DMG, +100 attack vs robots","Inertia":"*3 DMG +10","Stun":"DMG = Intensity","Vibro":"+20 DMG, +100 attack"}

    offender.Attacks.append(f'Ram: {please.get_table_result(attack_tables_pivot[0])}') # every robot can ram

    for index, attack_table in enumerate(attack_tables_pivot):
        for _ in range(rolls_list[index]):
            new_attack = please.get_table_result(attack_table)

            if new_attack == "Ram":
                offender.Ramming += 1
                offender.Attacks.append(f'Ram: {please.get_table_result(attack_tables_pivot[0])}')

            elif "Strike" in new_attack:
                strike_break = new_attack.split(" ")
                if len(strike_break) == 1:
                    offender.Attacks.append(f'Strike: {please.get_table_result(table.strike_attacks)}')
                else:
                    fancy_strike = strike_break[1]
                    offender.Attacks.append(f'{new_attack}: {please.get_table_result(table.strike_attacks)}, {fancy_attacks[fancy_strike]}')
                    
            elif "Fling" in new_attack:
                strike_break = new_attack.split(" ")
                if len(strike_break) == 1:
                    offender.Attacks.append(f'Fling: {please.get_table_result(table.fling_attacks)}')
                else:
                    fancy_strike = strike_break[1]
                    offender.Attacks.append(f'{new_attack}: {please.get_table_result(table.fling_attacks)}, {fancy_attacks[fancy_strike]}')
          
            elif "Defensive" in new_attack:
                offender.Defences.append(please.get_table_result(table.robotic_defences))

            elif new_attack in ["Gun", "Aerosol", "Bomb", "Grenade"]:
                offender.Attacks.append(f'{new_attack}: {toy.gimme_one(new_attack)}')

            elif "Mutation" in new_attack:
                mutations.single_random_mutation(offender, ['any', 'combat'])
            else:
                offender.Attacks.append(new_attack)

    offender.Attacks.sort()
    return offender # is altered by side effect


def robot_defensive_systems(defender: RobotRecord, number: int) -> list:
    """
    returns a list of defenses for the robot
    """
    defence_list = []

    ### defensive systems does not have extra roll or choose.
    for _ in range(number):
        defense = please.get_table_result(table.robotic_defences)

        if defense == "Aunty Missile":
            defence_list.append(f"Aunty Missile: AR +{please.roll_this('1d6')*50} vs missiles")
        elif defense == "Aunty Personnel":
            defence_list.append(f"Aunty Personnel: Lethal 3d6 HPS, Non-Lethal 4d6 intensity")
        elif defense == "Increase AR":
            defender.AR += please.roll_this("1d6*50")
            defence_list.append(f"Hardened AR: new AR is {defender.AR}")
        elif defense == "Artifact Armour":
            defence_list = f'Armoured: {please.get_table_result(table.armour_list)}'
        elif defense == "Camouflage":
            defence_list.append(f"Camouflage against {defender.Sensors} sensors")
        elif defense == "Detect Ambush":
            defence_list.append(f"Detect Ambush: AWE is {defender.AWE * 4} vs ambush")
        elif defense == "Diffuse Explosives":
            defence_list.append(f"Diffuse Explosives: {defender.INT*2} and level {defender.Level+5} vs explosives.")
        elif defense == "Evasive Action":
            defence_list.append(f"Evasive Action: no move penalties when running away.")
        elif defense == "Force Field":
            defence_list.append(f"Force Field: {please.roll_this('1d4*25')} HPS  (cumulative)")
        elif defense == "Increase HPM":
            bump = 1 + (please.roll_this("1d6") / 10)
            defender.HPM = math.ceil(defender.HPM * bump)
            defence_list.append(f"Increase HPM to {defender.HPM} HPS (added)")
        elif defense == "Mental Mutation":
            mutations.single_random_mutation(defender, ['mental', 'combat'])

        defence_list.sort()
    return defence_list


def robot_description(looks_like: RobotRecord) -> RobotRecord:
    """
    creates a wholly random robot description and colour
    """

    ### do none of this if android or social
    if looks_like.FAMILY_TYPE == "Android":
        looks_like.Description = "Looks like any other " + looks_like.Base_Family.lower()
        return looks_like
    
    elif looks_like.FAMILY_TYPE == "Social":
        looks_like.Description = "Looks like a mechanical " + looks_like.Base_Family.lower()
        return looks_like

    ### SIZE descriptor
    sized = looks_like.Size_Cat if looks_like.Size_Cat not in ["Medium", "Nano", "Giga"] else f"{looks_like.Size_Cat} sized"
    
    ### SHAPE descriptor
    shaped = please.get_table_result(table.base_shape)
    shaped = shaped if shaped != "Descriptive" else please.get_table_result(table.descriptive_shapes)
    # mangle shape?
    shaped = shaped if please.do_1d100_check(40) else f'{please.get_table_result(table.shape_mangle)} {shaped}'
    # adorn shape
    shaped = shaped if please.do_1d100_check(25) else f'{shaped} and {please.get_table_result(table.adornage)}'

    ### COLOUR descriptor
    colour = please.get_table_result(table.colour_bomb) if please.do_1d100_check(50) else f'{please.get_table_result(table.colour_bomb)} with {please.get_table_result(table.colour_bomb)} accents'

    ###  LOCOMOTION descriptor
    floating = True  if looks_like.Locomotion in ["Anti-Grav", "Magnetic"] else False

    if looks_like.Locomotion[0].isdigit():
        locomo = f'{choice["with", "sporting", "with", "moved by", "pushed by", "propelled by", "driven by"]} {looks_like.Locomotion}'

    elif looks_like.Locomotion in ['Chemical Slide', 'Slog Bag']:
        locomo = f'{choice["a top", "sitting on a", "moved by"]} {looks_like.Locomotion}'

    return f"A {'floating ' if floating else ''}{sized.lower()} {colour} {shaped}{'.' if floating else locomo.lower()}{'' if floating else '.'}"

def robot_persona_name(object):

    print("\nWhen you are creating a robot persona you are also creating a MODEL.")
    print(
        "Your robot type is "
        + object.FAMILY_TYPE.upper()
        + ". You look like:"
        + object.Description
    )
    print(
        "Please consider your robot's MODEL name.\nWhich is different from you PERSONA name.\n"
    )

    object.Robot_Model = input("What is robot MODEL name? ")
    object.Persona_Name = input("What is your robot PERSONA name? ")

    return

####################################################
#
# List of ROBOT type functions
#
####################################################

def android(andy: RobotRecord) -> RobotRecord:
    """
    inject the android attributes into the andy
    """

    ### androids are odd in that they skip most of the robot attributes

    ### set family type to use ANTHRO calcs
    andy.FAMILY = "Anthro"
    andy.FAMILY_TYPE = andy.Base_Family

    anthro.anthro_hite_wate_calc(andy, "Larger")
    andy.Wate = round(andy.Wate * 1.3)
    core.hit_points_max(andy)

    ### reset to robot 
    andy.FAMILY = "Robot"
    andy.FAMILY_TYPE = "Android"
    andy.FAMILY_SUB = andy.Base_Family

    andy.FAMILY_TYPE = "Android"

    ### core values
    andy.Adapt = 1
    andy.Value = 100000000

    ### vocation EXCEPTION for android
    type_options = vocation.attribute_determined(andy)
    comment = "Choose your vocation."
    type_choice = please.choose_this(type_options, comment)
    andy.Vocation = type_choice
    vocation.set_up_first_time(andy)

    ### building the spec sheet
    specs = [f"Built in the image of their maker ({andy.FAMILY_SUB})."]
    specs.append(f"Has no biologic life force.")
    specs.append(f"Works as a {andy.Vocation}.")
    andy.Spec_Sheet = specs

    return andy # modified by side effect


def combot(comboy: RobotRecord) -> RobotRecord:
    """
    determine combot sub type and adjust persona record
    """
    ### robot nomenclature
    comboy.FAMILY_TYPE =  "Combot"

    ### determine SUB_TYPE
    # build the attribute determined list
    sub_type_choices = ["Expendable"]
    if comboy.CON >= 20:
        sub_type_choices.append("Defensive")
    if comboy.CON >= 19 and comboy.DEX >= 15:
        sub_type_choices.append("Offensive-Light")
    if comboy.CON >= 23 and comboy.PSTR >= 27:
        sub_type_choices.append("Offensive-Heavy")

    if comboy.Bespoke or comboy.Fallthrough:
        sub_type_choices = ["Expendable", "Defensive", "Offensive-Light", "Offensive-Heavy" ]

    if comboy.Fallthrough:
        comboy.FAMILY_SUB = choice(sub_type_choices)
    else:
        comboy.FAMILY_SUB = please.choose_this(sub_type_choices, "Please choose COMBOT sub-type.")

    ### generic spec sheet
    specs = [f"Unconcerned about base family ({comboy.Base_Family})."]

    if comboy.FAMILY_SUB == "Expendable":
        ### expendable core values
        comboy.Adapt = 0
        comboy.Value = 500000
        comboy.Size_Cat =  "Small"
        comboy.HPM = comboy.CON * 5

        offending_list = robot_offensive_rolls([(attack_one_rolls,1)])
        robot_offensive_systems(comboy,offending_list)
        comboy.Defences.append(robot_defensive_systems(comboy, 1))
        comboy.Peripherals.append(robotic_peripherals(comboy, 1))

        ### expendable spec sheet
        specs.append("Robotic general infantry.")
        specs.append("Somewhat nihilistic outlook.")
        specs.append("Can drive military vehicles.")
        comboy.Spec_Sheet = specs

        return comboy # modified by side effects

    elif comboy.FAMILY_SUB == "Defensive":

        ### defensive core values
        comboy.Adapt = 1
        comboy.Value = 10000000
        comboy.Size_Cat =  "Large"
        comboy.HPM = comboy.CON * please.roll_this("1d10+20")

        offending_list = robot_offensive_rolls([(attack_one_rolls,1)])
        robot_offensive_systems(comboy,offending_list)
        comboy.Defences.append(robot_defensive_systems(comboy,  math.ceil(comboy.CON / 4)))
        comboy.Peripherals.append(robotic_peripherals(comboy, 1))

        ### defensive spec sheet
        specs.pop() # removes disregard for base_family
        specs.append("Demoralize with pithy comments.")
        specs.append(f"Fortify against an attack {comboy.INT * 4}%.")
        specs.append(f"Intruder detection {comboy.AWE * 10} hex radius.")
        specs.append(f"Anti-detection detection {comboy.AWE + comboy.INT}%")
        specs.append(f"Identify weapon that inflicts damage {comboy.INT * 2}%")
        comboy.Spec_Sheet = specs

        return comboy # modified by side effects

    elif comboy.FAMILY_SUB == "Offensive-Light":

        ### Offensive-Light core values
        comboy.Adapt = -50
        comboy.Value = 100000000
        comboy.Size_Cat =  "Medium"
        comboy.HPM = comboy.CON * please.roll_this("1d10+15")

        offending_list = robot_offensive_rolls([(attack_two_rolls,2),(attack_three_rolls,1)])
        robot_offensive_systems(comboy,offending_list)
        comboy.Defences.append(robot_defensive_systems(comboy, 2))
        comboy.Peripherals.append(robotic_peripherals(comboy, 1))

        ### Offensive-Light spec sheet
        specs.append("Violent solutions are preferable.")
        lesser_bots = please.roll_this("1d4-1")
        commanding = "Command: Nil" if lesser_bots == 0 else f"Command: {lesser_bots} expendable combot(s)"
        specs.append(commanding)

        comboy.Spec_Sheet = specs

        return comboy # modified by side effects

    elif comboy.FAMILY_SUB == "Offensive-Heavy":

        ### Offensive-Heavy core values
        comboy.Adapt = -100
        comboy.Value = 1000000042
        comboy.Size_Cat =  "Gigantic"
        comboy.HPM = comboy.CON * please.roll_this("1d10+15")

        offending_list = robot_offensive_rolls([(attack_two_rolls,1),(attack_three_rolls,1),(attack_four_rolls,1)])
        robot_offensive_systems(comboy,offending_list)
        comboy.Defences.append(robot_defensive_systems(comboy, 3))
        comboy.Peripherals.append(robotic_peripherals(comboy, 1))

        ### armour rating EXCEPTION  for Offensive-Heavy combot
        comboy.AR = 775 if comboy.AR < 775 else comboy.AR

        ### integrated heavy weapon EXCEPTION  for Offensive-Heavy combot
        roll = please.roll_this("1d100") + comboy.PSTR
        for spread, weapon in table.combot_heavy_weapons.items():
            if roll in spread:
                break
        
        bombay = artay = ""
        if "Pop" in weapon:
            comboy.Peripherals.append("Integrated Popcorn Maker")

        if "Bomb" in weapon:
            bombay = f'Integrated bomb: {toy.gimme_one("Bomb")}'

        if "Missile" in weapon:
            bombay = f'Integrated Missile: delivers {toy.gimme_one("Bomb")} bomb.'
       
        if "Art" in weapon:
            artay = f'Integrated artillery: {toy.gimme_one("Artillery")}'

        if "Naval" in weapon:
            artay = f'Integrated naval artillery: base {toy.gimme_one("Artillery")}'

        if bombay:
            comboy.Attacks.append(bombay)
        if artay:
            comboy.Attacks.append(artay)
        
        comboy.Attacks.sort()
        ### Offensive-Heavy spec sheet
        specs.append("Mass destruction is preferred solution")
        comboy.Spec_Sheet = specs

        return comboy # modified by side effects

    return


def datalyzer(nerdy: RobotRecord) -> RobotRecord:
    """
    inject the datalyzer attributes into the nerdy
    """

    ### datalyzer nomenclature
    nerdy.FAMILY_TYPE =  "Datalyzer"
    nerdy.FAMILY_SUB = "Data Nerd"

    ### core values
    nerdy.Adapt = 15
    nerdy.Value = 10000 * nerdy.INT
    nerdy.Size_Cat =  "Small"
    nerdy.HPM = please.roll_this("1d2+2") * nerdy.CON

    if please.do_1d100_check(5):
        offending_list = robot_offensive_rolls([(attack_one_rolls, 1)])
        nerdy.Attacks.append(robot_offensive_systems(nerdy,offending_list))


    nerdy.Defences.append(robot_defensive_systems(nerdy, 1))
    if please.do_1d100_check(24): #24% chance second defence
        nerdy.Defences.append(robot_defensive_systems(nerdy, 1))

    nerdy.Peripherals.append(robotic_peripherals(nerdy, 2))

    ### mental mutation EXCEPTION for datalyzer
    if please.do_1d100_check(
        table.datalyzer_mental_chance[nerdy.Base_Family] + nerdy.INT
    ):
        mutations.single_random_mutation(nerdy, ['mental', 'no-defect'])

    ### datalyzer spec sheet
    specs = ["Tin can thinkers."]
    nerdy.Spec_Sheet = specs

    return nerdy # is modified by side effect


def explorations(expoh:RobotRecord) -> RobotRecord:
    '''inject explorations bot '''

    ### explorations nomenclature
    expoh.FAMILY_TYPE = "Explorations"
    specs = ["Designed to explore, learn and report."]

    # build subtype choices
    choices = ["Planetary"]
    if expoh.INT >= 24:
        choices.append("Extra-planetary")
    if expoh.Bespoke or expoh.Fallthrough:
        choices= ["Planetary", "Extra-Planetary" ]
    if expoh.Fallthrough:
        chosen = choice(choices)
    else:
        comment = "Please choose your Explorations bot type."
        chosen = please.choose_this(choices, comment)

    if chosen == "Planetary":
        expoh.FAMILY_SUB = "Planetary"
        specs.append("Created to explore their own planet.")
        expoh.Adapt = 0
        expoh.Value = 250000
        expoh.HPM = please.roll_this("1d6+10") * expoh.CON
        expoh.Size_Cat =  "Medium"

        if please.do_1d100_check(25):
            offending_list = robot_offensive_rolls([(attack_one_rolls,1)])
            robot_offensive_systems(expoh, offending_list)

        robot_defensive_systems(expoh, 1)
        robotic_peripherals(expoh, 1)

    elif chosen == "Extra-Planetary":
        expoh.FAMILY_SUB = "Extra-Planetary"
        expoh.Adapt = 0
        expoh.AR = 800
        expoh.Value = 1900000
        expoh.HPM = please.roll_this("1d6+10") * expoh.CON
        expoh.Size_Cat =  "Large"

        offending_list = robot_offensive_rolls([(attack_two_rolls,1)])
        robot_offensive_systems(expoh, offending_list)
        robotic_peripherals(expoh, 1)

        specs.append("Created to explore unknown planets.")
        specs.append("Comprehend languages and alien intelligence.")
        specs.append("Exatmo hardened.")
        expoh.Spec_Sheet = specs

    specs.append("Atmospheric analysis.")
    specs.append("Communications.")
    specs.append("Mineral identification.")
    specs.append("Detect Toxins. Rads, poison etc.")
    specs.append("Terrain mapping.")
    specs.append("Obsessed with collecting samples.")

    expoh.Spec_Sheet = specs
    return

def hobbot(hobby:RobotRecord) -> RobotRecord:
    '''insert hobbot data into persona record'''

    ### hobbot data
    hobby.FAMILY_TYPE = "Hobbot"
    hobby.FAMILY_SUB = "Hacker Snowflake"
    hobby.Adapt = 84
    hobby.HPM = please.roll_this("2d4") * hobby.CON
    hobby.Size_Cat =  "Tiny"

    if please.do_1d100_check(10):
        offending_list = robot_offensive_rolls([(attack_one_rolls, 1)])
        robot_offensive_systems(hobby, offending_list)

    if please.do_1d100_check(50):
        robot_defensive_systems(hobby, 1)

    # robotic_peripherals are random
    number = please.roll_this("2d4")
    robotic_peripherals(hobby, number)
    hobby.Value = 10000 + 20000 * number

    specs = ["Highly modified hobbyist machines."]
    specs.append("+25 bonus for mechanics.")
    specs.append("No two are the same.")
    hobby.Spec_Sheet = specs

    return hobby # adjusted by side effect


def industrial(indy: RobotRecord) -> RobotRecord:
    '''insert industrial robot into persona record'''

    indy.FAMILY_TYPE = "Industrial"
    indy.Adapt = 5
    indy.HPM = please.roll_this("1d4+8") * indy.CON
    indy.Size_Cat =  "Medium"
    specs = ["Capacitor of industry."]

    # build subtype choices
    choices = []
    if indy.INT >= indy.DEX and indy.INT >= indy.PSTR:
        choices.append("Construction")
    if indy.PSTR >= indy.DEX and indy.PSTR >= indy.INT:
        choices.append("Lifting")
    if indy.DEX >= indy.PSTR and indy.DEX >= indy.INT:
        choices.append("Moving")

    if indy.Bespoke or indy.Fallthrough:
        choices = ["Construction", "Lifting", "Moving"]

    comment = "Please choose your Industrial bot type."
    chosen = please.choose_this(choices, comment, indy)

    if chosen == "Construction":
        indy.FAMILY_SUB = "Construction"
        indy.Value = 50000

        offenses = robot_offensive_rolls([(attack_two_rolls, 2)])
        robot_offensive_systems(indy, offenses)

        if please.do_1d100_check(15):
            indy.Defences.append(robot_defensive_systems(indy, 1))

        indy.Peripherals.append(robotic_peripherals(indy, 2))

        specs.append("Likes to build things.")
        if indy.INT >= 22: specs.append("Can design simple things.")
        specs.append("Cannot fabricate complex TOYS.")
        specs.append("Programmable by a mechanic.")
        specs.append(f"Raw materials for {indy.CON} months.")
        indy.Spec_Sheet = specs

    elif chosen == "Lifting":
        indy.FAMILY_SUB = "Lifting"
        indy.Value = 30000
        indy.Size_Cat =  "Large"

        if please.do_1d100_check(35):
            offenses = robot_offensive_rolls([(attack_one_rolls, 1)])
            robot_offensive_systems(indy, offenses)

        # robot_defensive_systems check
        if please.do_1d100_check(16):
            indy.Defences.append(robot_defensive_systems(indy, 1))

        indy.Peripherals.append(robotic_peripherals(indy, 1))

        specs.append("Likes to lift and organize.")
        specs.append(f"Has {math.ceil(indy.DEX / 3)} lifting articulations.")
        specs.append(f"Can lift {indy.WA * 3} kgs up to {indy.PSTR_Prime + indy.DEX_Prime} hexes.")
        specs.append(f"Must roll vs CF ({indy.CF}) to drop things.")
        indy.Spec_Sheet = specs

    elif chosen == "Moving":
        indy.FAMILY_SUB = "Moving"
        indy.Value = 20000
        indy.Size_Cat =  "Large"

        # robot_offensive_systems check
        if please.do_1d100_check(35):
            robot_offensive_systems(indy, 2)
        else:
            indy.Robot_Attacks = []
        # robot_defensive_systems check
        if please.do_1d100_check(15):
            robot_defensive_systems(indy, 1)
        else:
            indy.Defences = []
        robotic_peripherals(indy, 1)

        indy.Move = math.ceil(indy.Move * 1.5)
        specs.append(f"Increased move to {indy.Move} h/u.")
        specs.append(f"Can deliver {indy.WA * 3} kgs at {indy.Move} h/u.")
        specs.append(f"Deliver range is {indy.AWE * 100} kilometers.")
        specs.append("Can read maps.")
        loading = ((indy.INT + indy.DEX) * 3) >= please.roll_this("1d100")
        if loading:
            specs.append("This bot is self loading (not loathing).")
        indy.Spec_Sheet = specs

    return

def janitorial(object):
    specs = ["Cleaning mopping and moping."]
    intel = object.INT
    con = object.CON

    # build subtype choices
    choices = ["Industrial"]

    if intel >= 12:
        choices.append("Domestic")
    comment = "Please choose your type of Janitorial bot."
    chosen = please.choose_this(choices, comment)

    if chosen == "Industrial":
        object.FAMILY_SUB = "Industrial"
        object.Adapt = 30
        object.Value = 20000
        object.HPM = please.roll_this("1d6") * con
        object.Size_Cat =  "Outdoor"
        robot_hite_wate_calc(object)
        # robot_offensive_systems check
        if please.do_1d100_check(25):
            robot_offensive_systems(object, 1)
        else:
            object.Robot_Attacks = []
        # robot_defensive_systems
        if please.do_1d100_check(45):
            robot_defensive_systems(object, 2)
        else:
            object.Defences = []
        robotic_peripherals(object, 1)

        specs.append("Combating entropy in the workplace.")
        object.Spec_Sheet = specs

    elif chosen == "Domestic":
        object.FAMILY_SUB = "Domestic"
        object.Adapt = 10
        object.Value = 35000
        object.HPM = please.roll_this("1d6") * con
        object.Size_Cat =  "Outdoor"
        robot_hite_wate_calc(object)
        # robot_offensive_systems
        if please.do_1d100_check(10):
            robot_offensive_systems(object, 1)
        else:
            object.Robot_Attacks = []
        # robot_defensive_systems
        if please.do_1d100_check(15):
            robot_defensive_systems(object, 2)
        else:
            object.Defences = []
        robotic_peripherals(object, 2)

        specs.append("Combating entropy in the home.")
        object.Spec_Sheet = specs

    return


def maintenance(object):
    object.FAMILY_SUB = "Mechanic"
    specs = ["Mechanic in a drum."]
    intel = object.INT
    con = object.CON
    # lvl = object.Level
    object.Adapt = 37
    object.Value = 1050000
    object.HPM = please.roll_this("1d4") * con
    object.Size_Cat =  "Indoor"
    robot_hite_wate_calc(object)
    # RoboticAttack check
    if please.do_1d100_check(40):
        robot_offensive_systems(object, 1)
    else:
        object.Robot_Attacks = []
    # RobotDefences chance
    if please.do_1d100_check(40):
        robot_defensive_systems(object, 1)
    else:
        object.Defences = []
    robotic_peripherals(object, 2)

    # set up mechanic
    object.INT = intel * 3  # temporary INT rise for skill calc
    object.Vocation = "Mechanic"
    # vocation.intake(object)
    object.INT = intel  # return to previous INT

    # endow mechanic specs and abilities
    vocation.DataGeneration(object)

    # revisit here to remove combat table for mechanic
    # beware of specs wipe out and cross over
    specs.append("Not a janitorial bot.")
    specs.append("Has Mechanic specs for repairs.")
    specs.append(f"Add {intel} (INT) to PT rolls.")
    object.Spec_Sheet = specs

    return


def police(object):
    specs = [f"To serve and protect {object.Base_Family}s."]
    awe = object.AWE
    cha = object.CHA
    con = object.CON
    dex = object.DEX
    intel = object.INT
    pstr = object.PSTR

    # build subtype choices
    choices = ["Civil"]

    if con >= 15:
        choices.append("Riot")
    if intel >= 15:
        choices.append("Special")

    comment = "Please choose your policing bot type. "
    chosen = please.choose_this(choices, comment)

    if chosen == "Civil":
        object.FAMILY_SUB = "Civil"
        specs.append("Mechanical street cop.")
        object.Adapt = 10
        object.Value = 600000
        object.HPM = please.roll_this("3d4") * con
        object.Size_Cat =  "Outdoor"
        robot_hite_wate_calc(object)
        robot_offensive_systems(object, 1)
        # special stun attack
        object.Robot_Attacks.append("Stun 4d4 intensity for 1d4 units.")
        robot_defensive_systems(object, 1)
        robotic_peripherals(object, 1)

        specs.append(f"Make loud commands at double CHA ({cha * 2}.")
        specs.append("Grapple and disarm with a successful to hit roll.")
        object.Spec_Sheet = specs

    elif chosen == "Riot":
        object.FAMILY_SUB = "Riot"
        specs.append("Less lethal mob control. AKA riobot.")
        object.Adapt = 10
        object.Value = 300000
        object.HPM = please.roll_this("1d4+9") * con
        object.Size_Cat =  "Outdoor"
        robot_hite_wate_calc(object)
        object.Robot_Attacks = []
        robot_defensive_systems(object, 1)
        robotic_peripherals(object, 1)

        specs.append(f"Grapple, disarm and detain up to {pstr} unruly targets.")
        specs.append(f"Crowd control devices:")

        # generate crowd control tools
        halfcon = math.ceil(con / 2)
        halfintel = math.ceil(intel / 2)
        halfcha = math.ceil(cha / 2)

        RiotPolicing = {
            range(1, 21): f"Water Cannon. {pstr} targets. Hit = knocked down.",
            range(
                21, 41
            ): f"Tear Gas. {con} hex radius. {con} intensity. Blind for 1d8 units.",
            range(
                41, 51
            ): f"Stun Ray. {pstr} targets. {con} intensity. Stunned for 1d8 units.",
            range(
                51, 61
            ): f"Grav Disruptor.  {halfcon} hex radius. {con} intensity or knocked down.",
            range(
                61, 71
            ): f"Force Beam {pstr} targets. {pstr} intensity. Tossed 1d4 hexes.",
            range(
                71, 81
            ): f"Weapon Malfunction. {halfcha} hex radius. 25 times increase powered weapons fail.",
            range(
                81, 91
            ): f"Battery Drain. {halfintel} hex radius. Batteries drop to zero. No save.",
            range(
                91, 101
            ): f"Sleep Beam. {cha} targets. {intel} intensity. Go to sleep.",
            "name": "Riot Policing",
            "number": "5.4",
            "die_roll": "1d100",
        }

        number = math.ceil(intel / 3)

        for __ in range(number + 1):
            specs.append(please.get_table_result(RiotPolicing))

        object.Spec_Sheet = specs

    elif chosen == "Special":
        object.FAMILY_SUB = "Special"
        specs.append("Detective, sleuth, criminologist.")
        object.Adapt = 10
        object.Value = 900000
        object.HPM = please.roll_this("1d3+1") * con
        object.Size_Cat =  "Indoor"
        robot_hite_wate_calc(object)
        robot_offensive_systems(object, 1)
        robot_defensive_systems(object, 1)
        robotic_peripherals(object, 1)

        specs.append("Can order riot and civil bots around.")

        object.Spec_Sheet = specs

        print("May swap highest attribute to INT.")
        print("Without penalty or benefit.")
        comment = "Would you like to swap your highest attribute? "
        chosen = please.choose_this(["Yes", "No"], comment)
        if chosen == "No":
            return
        elif chosen == "Yes":
            dirty_list = []
            dirty_list.append(("AWE", awe))
            dirty_list.append(("CHA", cha))
            dirty_list.append(("CON", con))
            dirty_list.append(("DEX", dex))
            dirty_list.append(("PSTR", pstr))
            dirty_list = sorted(dirty_list, key=lambda tup: tup[1])
            attribute, highest = dirty_list(-1)

            if highest > intel:
                object.INT = highest
                setattr(object, attribute, intel)
                control_factor(object)

    return


def rescue(object):
    specs = ["Rescuing entities and environments."]
    awe = object.AWE
    con = object.CON
    dex = object.DEX
    pstr = object.PSTR
    wa = object.WA

    # build subtype choices
    choices = ["Spillage"]

    if dex >= 22:
        choices.append("Retrieval")
    comment = "Please choose your type of rescue bot. "
    chosen = please.choose_this(choices, comment)

    if chosen == "Retrieval":
        object.FAMILY_SUB = "Retrieval"
        specs.append("Built to retrieve entities and equipment from danger.")
        object.Adapt = 10
        object.Value = 950000
        object.HPM = please.roll_this("2d10+5") * con
        object.Size_Cat =  "Outdoor"
        robot_hite_wate_calc(object)
        robot_offensive_systems(object, 1)
        robot_defensive_systems(object, 3)
        robotic_peripherals(object, 1)

        specs.append("Exatmo hardened and  environment agnostic.")
        chambers = math.ceil(pstr / 2)
        specs.append(f"{chambers} stasis chambers for holding anthro sized entities.")
        specs.append("150 hexes of retractable glowing safety fencing.")

        object.Spec_Sheet = specs

        chosen = please.choose_this(
            ["Hell yeah!", "Um, no."], "Was your retrieval bot made by the JIBC? "
        )
        if chosen == "Hell yeah!":
            object.AWE = 3
            object.CHA = 1
            object.CON = 3
            object.DEX = 9
            object.INT = 4
            object.PSTR = 12
            object.HPM = 4
            object.SOC = 42
            object.Robot_Attacks = ["Sarcasm, but only towards the vulnerable."]
            object.Defences = [
                "Can use rules and protocols to avoid work.",
                "Zero resiliency.",
            ]
            object.Peripherals = ["A bowl to collect the tears of children."]
            object.FAMILY_SUB = "JIBC"
            object.Spec_Sheet = ["Pretends to be a veterinarian, but has no specs."]

    elif chosen == "Spillage":
        object.FAMILY_SUB = "Spillage"
        specs.append("Built to contain spillage of toxins, including fire.")
        object.Adapt = 10
        object.Value = 750000
        object.HPM = please.roll_this("2d10+5") * con
        object.Size_Cat =  "Outdoor"
        robot_hite_wate_calc(object)
        # robot_offensive_systems chance
        if please.do_1d100_check(25):
            robot_offensive_systems(object, 1)
        else:
            object.Robot_Attacks = []
        robot_defensive_systems(object, 3)
        robotic_peripherals(object, 1)

        object.AR = 875

        specs.append("Exatmo hardened and are environment agnostic.")
        specs.append(f"Detect toxins. {awe * 10} hex range.")
        specs.append(f"Can store up to {20 * wa} kgs of toxins.")
        specs.append(f"Extinguish {5 * con} hexes of fire.")
        specs.append("Immune to fire, but not fire weapons")
        specs.append("250 hexes of retractable glowing safety fencing.")
        specs.append("100 hexes (area) of ejectable 'safety plastic.'")
        specs.append("Plastic spray can act like a Web Gun (chap 46).")

        object.Spec_Sheet = specs

        return


def social(object):
    object.FAMILY_SUB = basefamily = object.Base_Family
    specs = [f"Built to serve {basefamily}."]
    intel = object.INT
    con = object.CON
    object.Adapt = 50
    object.Value = 100000
    object.HPM = please.roll_this("1d3+1") * con
    # social wate and hite
    # object.Anthro_Type = basefamily
    # this is no longer correct FAMILY_TYPE == social now

    anthro.AnthroHiteWate(object)
    object.Wate = round(object.Wate * 1.5)
    # RobotAttacks chance
    if please.do_1d100_check(10):
        robot_offensive_systems(object, 1)
    else:
        object.Robot_Attacks = []
    # RobotDefences chance
    if please.do_1d100_check(85):
        robot_defensive_systems(object, 1)
    else:
        object.Defences = []
    robotic_peripherals(object, 1)

    specs.append("Previously called a relations bot, or robotler.")
    specs.append(f"Mechanicanized, inorganic version of {basefamily}.")
    specs.append(f"Can speak up to {intel * 10} languages.")
    specs.append("Can learn any intelligent language in 1d4 days.")
    specs.append(f"Can offer etiquette and customs advice on up to {intel} cultures.")
    specs.append(f"Can look after up to {intel * 2} organic clients.")
    specs.append("Social bots do not look after other robots.")

    object.Spec_Sheet = specs

    return


def transport(object):
    specs = ["Getting things from one place to another."]
    con = object.CON
    dex = object.DEX
    intel = object.INT

    # build subtype choices
    choices = ["Planetary"]

    if dex >= 22 and intel >= 22:
        choices.append("Extra-Planetary")
    comment = "Please choose your type of Transport bot. "
    chosen = please.choose_this(choices, comment)

    if chosen == "Planetary":
        object.FAMILY_SUB = "Planetary"
        specs.append("Planet side chauffer.")
        object.Adapt = 22
        object.Value = 450000
        object.HPM = please.roll_this("1d4+8") * con
        object.Size_Cat =  "Indoor"
        robot_hite_wate_calc(object)
        # RobotAttacks chance
        if please.do_1d100_check(50):
            robot_offensive_systems(object, 1)
        else:
            object.Robot_Attacks = []
        # RobotDefences chance
        if please.do_1d100_check(40):
            robot_defensive_systems(object, 1)
        else:
            object.Defences = []
        robotic_peripherals(object, 1)

        specs.append(
            f"Expert driver can divide {intel + 5} specs between any vehicles."
        )
        specs.append(f"Driving an unknown vehicle {intel * 4}%")
        specs.append("Any inatmo vehicle. No space vehicles.")
        specs.append("Not skilled in vehicle combat.")
        specs.append("Can act as a  steward skill for large vehicles.")

        object.Spec_Sheet = specs

    elif chosen == "Extra-Planetary":
        object.FAMILY_SUB = "Extra-Planetary"
        specs.append("Space vehicle pilot.")
        object.Adapt = 22
        object.Value = 450000
        object.HPM = please.roll_this("1d4+8") * con
        object.Size_Cat =  "Indoor"
        robot_hite_wate_calc(object)
        # RobotAttacks chance
        if please.do_1d100_check(50):
            robot_offensive_systems(object, 1)
        else:
            object.Robot_Attacks = []
        # RobotDefences chance
        if please.do_1d100_check(40):
            robot_defensive_systems(object, 1)
        else:
            object.Defences = []
        robotic_peripherals(object, 1)

        specs.append(f"Expert pilot can divide up {intel + 5} specs.")
        specs.append(
            "Can only pilot space vessels. May drive any vehicles on space vessel."
        )
        specs.append(f"Driving an unknown vessel {intel * 4}%")
        specs.append("Not skilled in vehicle combat.")
        specs.append("Has a steward skill for ships with organics.")

        object.Spec_Sheet = specs

    return


def veterinarian(object):
    specs = [
        "Veterinarian in a drum.",
        "Very high regard for preservation of organic life.",
    ]
    con = object.CON
    dex = object.DEX
    intel = object.INT
    intel_prime = object.INT_Prime
    pstr = object.PSTR

    # build subtype choices
    choices = ["Diagnostic"]

    if dex >= 23 and intel >= 21:
        choices.append("Interventional")
    comment = "Please choose your type of veterinarian bot. "
    chosen = please.choose_this(choices, comment)

    if chosen == "Diagnostic":
        object.FAMILY_SUB = "Diagnostic"
        specs.append("Prefers to figure out rather than fix.")
        object.Adapt = 10
        object.Value = 2250000
        object.HPM = 2 * con
        object.Size_Cat =  "Indoor"
        robot_hite_wate_calc(object)
        object.Robot_Attacks = []
        # RobotDefences chance
        if please.do_1d100_check(10):
            robot_defensive_systems(object, 1)
        else:
            object.Defences = []
        robotic_peripherals(object, 1)

        specs.append(
            f"On vet performance table {intel_prime} DD bonus and {intel * 2} PT roll bonus."
        )
        specs.append(
            "Good at diagnosis and minor specs. Cannot perform major interventions."
        )
        specs.append(f"Identify medical equipment and pharmaceuticals {intel * 5}%.")

        object.Spec_Sheet = specs

    elif chosen == "Interventional":
        object.FAMILY_SUB = "Interventional"
        specs.append("Prefers to fix rather than figure out.")
        object.Adapt = 10
        object.Value = 5000000
        object.HPM = 2 * con
        object.Size_Cat =  "Outdoor"
        robot_hite_wate_calc(object)
        object.Robot_Attacks = []
        # RobotDefences chance
        if please.do_1d100_check(10):
            robot_defensive_systems(object, 1)
        else:
            object.Defences = []
        robotic_peripherals(object, 1)

        specs.append("Needs direction from diagnostic bot or veterinarian.")
        specs.append(
            "Can perform all manner of interventions. Including surgery and anesthesia."
        )
        specs.append(f"On vet performance table may add INT to ({intel}) to PT roll.")
        distance = math.ceil(pstr / 2)
        specs.append(f"Anaesthesia has a range of {distance} hexes.")

        object.Spec_Sheet = specs

    # be sure to add veterinarian class for PT but not CT
    object.Vocation = "Veterinarian"

    # endow veterinarian specs and abilities
    vocation.DataGeneration(object)

    return


#####################################
# build a FRESH robot persona
#####################################

### build a fresh robot persona
def fresh_robot():
    """
    builds A FRESH robot persona using EXP persona creation
    """
    # todo robot is a class or a function 

    # clearance for Clarence
    please.clear_console()
    print("\nYou are generating a fresh ROBOT PERSONA")

    fresh = RobotRecord()

    fresh.Player_Name = please.input_this("\nPlease input your MUNDANE TERRAN NAME: ")
    core.initial_attributes(fresh)
    fresh.Base_Family = please.get_table_result(table.robot_fabricator_list)
    fresh.CF = control_factor(fresh)
    core.movement_rate(fresh)
    core.wate_allowance(fresh)
    fresh.Power_Plant = please.get_table_result(table.robotic_power_plant)
    fresh.Power_Reserve = fresh.CON
    fresh.Sensors = robotic_sensors(fresh)
    core.base_armour_rating(fresh)

    ### choose the FAMILY_TYPE
    bot_type = please.choose_this(list_eligible_robot_types(fresh), "Please choose a robot type.")
    fresh.FAMILY_TYPE = bot_type
    robot_type_function_pivot[bot_type](fresh)

    ### requires bot_type
    fresh.Locomotion = robotic_locomotion(fresh)
    robot_hite_wate_calc(fresh)
    fresh.Quick_Description = robot_description(fresh)

    if fresh.Vocation != "Robot":
        vocation.set_up_first_time(fresh)

    outputs.outputs_workflow(fresh, "screen")
    robot_persona_name(fresh)
    outputs.outputs_workflow(fresh, "screen")
    please.assign_id_and_file_name(fresh)
    please.record_storage(fresh)
    return


#####################################
# build a BESPOKE robot persona
#####################################

def bespoke_robot():
    pass


#####################################
# build a RANDO robot persona
#####################################

def rando_robot():
    pass

robot_type_function_pivot = {
    "Android": android,
    "Combot": combot,
    "Datalyzer": datalyzer,
    "Explorations": explorations,
    "Hobbot": hobbot,
    "Industrial": industrial,
    "Janitorial": janitorial,
    "Maintenance": maintenance,
    "Police": police,
    "Rescue": rescue,
    "Social": social,
    "Transport": transport,
    "Veterinarian": veterinarian,
}

