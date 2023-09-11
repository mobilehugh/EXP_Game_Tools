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

# todo consider minimum HPM for robot 

# set up RobotRecord
@dataclass
class RobotRecord(table.Robotic):
    pass

def robot_workflow():
    """
    player robot versus RP robot vs maintenance
    """
    # clearance for Clarence
    please.clear_console()

    print('You are about to embark on a ROBOT Build')
    nom_de_bom = please.input_this("\nPlease input your MUNDANE TERRAN NAME: ")

    workflow_function_map = {
        "Fresh Robot (New Player)":lambda: fresh_robot(nom_de_bom),
        "Bespoke Robot":lambda: bespoke_robot(nom_de_bom),
        "Random Robot":lambda: rando_robot((nom_de_bom)),
        "Maintenance":please.do_referee_maintenance,
    }

    comment = "Choose a ROBOT workflow:"
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
        if kilo_conv in range(*hite_range): # the * unpacks the tuple
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
            toy_type = toy.toy_cat_type("any")
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
                offender.Attacks.append(f'{new_attack}: {toy.toy_cat_type(new_attack)}')

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

    if isinstance(number, int):
        pass
    else:
        input(f"ooops {defender.FAMILY_TYPE} {number = }")

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
            defence_list.append(f'Armoured: {please.get_table_result(table.armour_list)}')
        elif defense == "Camouflage":
            defence_list.append(f"Camouflage vs: {', '.join(defender.Sensors)} detection")
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

    if defence_list:
        defence_list.sort()
    return defence_list

def robotic_locomotion(move_it:RobotRecord) -> str:
    '''create a locomotion string'''

    # bespoke locomotion skips fallthrough as fresh  is also a fallthrough
    if move_it.Bespoke:
        locomo_tuples = please.list_table_choices(table.primary_robotic_locomotion)
        locomo_choices = [t[0] for t in locomo_tuples]
        chosen = please.choose_this(locomo_choices, "Choose LOCOMOTION type.", move_it)        
        for tuple in locomo_tuples:
            if chosen in tuple:
                chosen = tuple
                break

    else:
        chosen = please.get_table_result(table.primary_robotic_locomotion)


    primary, secondary = chosen[0], chosen[1]

    if move_it.FAMILY_TYPE == "Android":
        return f'{move_it.Base_Family} legs' 
    
    if move_it.FAMILY_TYPE == "Social":
        return f'{move_it.Base_Family} like legs'
    
    if 'd' in secondary:
        return f'{please.roll_this(secondary)} {primary}'

    if secondary == "BackUp":
       return f'{primary} {choice(["moving", "pushing","propelling"])} {please.get_table_result(table.secondary_robotic_locomotion).lower()}' 

    return primary # [anti-grav, magnetic, chem slide, slog bag] 


def robot_description(looks_like: RobotRecord) -> str:
    """
    creates a wholly random robot description and colour
    """

    ### do none of this if android or social
    if looks_like.FAMILY_TYPE == "Android":
        return f'Looks like any other {looks_like.Base_Family.lower()}.'
    
    elif looks_like.FAMILY_TYPE == "Social":
        return f'Looks like a mechanical {looks_like.Base_Family.lower()}.'

    ### SIZE descriptor
    sized = looks_like.Size_Cat if looks_like.Size_Cat not in ["Medium", "Nano", "Giga"] else f"{looks_like.Size_Cat} sized"
    
    ### COLOUR descriptor
    colour = please.get_table_result(table.colour_bomb) if please.do_1d100_check(50) else f'{please.get_table_result(table.colour_bomb)} and {please.get_table_result(table.colour_bomb)}'

    ### SHAPE descriptor
    shaped = please.get_table_result(table.base_shape)
    shaped = shaped if shaped != "Descriptive" else please.get_table_result(table.descriptive_shapes)
    # mangle shape?
    shaped = shaped if please.do_1d100_check(40) else f'{please.get_table_result(table.shape_mangle)} {shaped}'
    # adorn shape?
    shaped = shaped if please.do_1d100_check(25) else f'{shaped} with {please.get_table_result(table.adornage)}'

    ###  LOCOMOTION descriptor
    floating = False

    if looks_like.Locomotion[0].isdigit():
        locomo = f', {choice(["atop", "sporting", "with", "moved by", "pushed by", "propelled by", "driven by"])} {looks_like.Locomotion}'

    elif looks_like.Locomotion in ['Chemical Slide', 'Slog Bag']:
        locomo = f' {choice(["atop a", "sitting on a", "moving on a"])} {looks_like.Locomotion}'

    elif looks_like.Locomotion in ["Anti-Grav", "Magnetic"]:
        floating = True

    elif looks_like.Locomotion == "Teleport":
        locomo = " with no obvious locomotion."

    else:
        locomo = f' and {looks_like.Locomotion}' 

    ### punk tuition 
    # to add . or , when connecting description and locomotion.
    if floating:
        descripto = f"A floating {sized.lower()} {colour} {shaped}."
    else:
        descripto = f"A {sized.lower()} {colour} {shaped}{locomo.lower()}."

    return descripto

def change_to_leet(s: str) -> str:
    ''' turns a string into l33tsp34k'''
    leet_dict = {
        'A': '4',
        'E': '3',
        'G': '9',
        'I': '1',
        'O': '0',
        'S': '5',
        'T': '7'
    }
    return ''.join(leet_dict.get(c.upper(), c) for c in s)

def robot_nomenclature(name_it: RobotRecord) -> RobotRecord:
    ''' sort out MODEL, Company and persona names'''

    print("\n\n============================\nTime to give names to the robot above")
    print(f'This robot is a {name_it.FAMILY_SUB} {name_it.FAMILY_TYPE}.')
    print(f'{name_it.Quick_Description}')

    if please.say_no_to(f"Your robot model is {name_it.Model}. Is this okay?"):
        name_it.Model = please.input_this("What your robot's MODEL name? ")
           
    if please.say_no_to(f"Your robot fabricator is {name_it.Fabricator}. Is this okay?"):
        name_it.Fabricator = please.input_this("What your robot's FABRICATOR name? ")

    name_it.Persona_Name = please.input_this("What is your robot's PERSONA name? ")

    return name_it # modified by side effects

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

    ### temp set FAMILY_TYPE for anthro hite wate calc
    andy.FAMILY_TYPE = andy.Base_Family
    anthro.anthro_hite_wate_calc(andy, "Larger")
    andy.Wate = round(andy.Wate * 1.3)
    andy.FAMILY_TYPE = "Android"
    andy.FAMILY_SUB = andy.Base_Family

    ### core values
    andy.Adapt = 1
    andy.Value = 100000000
    HPM_roll = str(math.ceil(andy.CON / 2)) + "d8+" + str(andy.CON)
    andy.HPM = please.roll_this(HPM_roll)

    ### vocation EXCEPTION for android

    comment = "Choose your vocation."
    andy.Vocation  = please.choose_this([vocation for vocation in table.vocation_list if vocation != "Knite"], comment, andy)
  
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

    comboy.FAMILY_TYPE =  "Combot"

    ### determine SUB_TYPE
    choices = ["Expendable"]
    if comboy.CON >= 20:
        choices.append("Defensive")
    if comboy.CON >= 19 and comboy.DEX >= 15:
        choices.append("Offensive-Light")
    if comboy.CON >= 23 and comboy.PSTR >= 27:
        choices.append("Offensive-Heavy")

    if comboy.Bespoke or comboy.Fallthrough:
        choices = ["Expendable", "Defensive", "Offensive-Light", "Offensive-Heavy" ]

    comboy.FAMILY_SUB = please.choose_this(choices, "Please choose COMBOT sub-type.", comboy)

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
        comboy.Defences.extend(robot_defensive_systems(comboy, 1))
        comboy.Peripherals.extend(robotic_peripherals(comboy, 1))

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
        comboy.Defences.extend(robot_defensive_systems(comboy,  math.ceil(comboy.CON / 4)))
        comboy.Peripherals.extend(robotic_peripherals(comboy, 1))

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
        comboy.Defences.extend(robot_defensive_systems(comboy, 2))
        comboy.Peripherals.extend(robotic_peripherals(comboy, 1))

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
        comboy.Defences.extend(robot_defensive_systems(comboy, 3))
        comboy.Peripherals.extend(robotic_peripherals(comboy, 1))

        ### armour rating EXCEPTION  for Offensive-Heavy combot
        comboy.AR = 775 if comboy.AR < 775 else comboy.AR

        ### integrated heavy weapon EXCEPTION  for Offensive-Heavy combot
        roll = please.roll_this("1d100") + comboy.PSTR
        for spread, weapon in table.combot_heavy_weapons.items():
            if roll in range(*spread):
                break
        
        bombay = artay = ""
        if "Pop" in weapon:
            comboy.Peripherals.append("Integrated Popcorn Maker")

        if "Bomb" in weapon:
            bombay = f'Integrated bomb: {toy.toy_cat_type("Bomb")}'

        if "Missile" in weapon:
            bombay = f'Integrated Missile: delivers {toy.toy_cat_type("Bomb")} bomb.'
       
        if "Art" in weapon:
            artay = f'Integrated artillery: {toy.toy_cat_type("Artillery")}'

        if "Naval" in weapon:
            artay = f'Integrated naval artillery: base {toy.toy_cat_type("Artillery")}'

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

    ### datalyzer info
    nerdy.FAMILY_TYPE =  "Datalyzer"
    nerdy.FAMILY_SUB = ""

    ### core values
    nerdy.Adapt = 15
    nerdy.Value = 10000 * nerdy.INT
    nerdy.Size_Cat =  "Small"
    nerdy.HPM = please.roll_this("1d2+2") * nerdy.CON

    if please.do_1d100_check(5):
        offending_list = robot_offensive_rolls([(attack_one_rolls, 1)])
        nerdy.Attacks.append(robot_offensive_systems(nerdy,offending_list))


    nerdy.Defences.extend(robot_defensive_systems(nerdy, 1))
    if please.do_1d100_check(24): #24% chance second defence
        nerdy.Defences.extend(robot_defensive_systems(nerdy, 1))

    nerdy.Peripherals.extend(robotic_peripherals(nerdy, 2))

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

    ### explorations info
    expoh.FAMILY_TYPE = "Explorations"
    specs = ["Designed to explore, learn and report."]

    # build subtype choices
    choices = ["Planetary"]
    if expoh.INT >= 24:
        choices.append("Extra-Planetary")

    if expoh.Bespoke or expoh.Fallthrough:
        choices= ["Planetary", "Extra-Planetary" ]

    comment = "Please choose your Explorations bot type."
    chosen = please.choose_this(choices, comment, expoh)

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

        expoh.Peripherals.extend(robotic_peripherals(expoh, 1))

    elif chosen == "Extra-Planetary":
        expoh.FAMILY_SUB = "Extra-Planetary"
        expoh.Adapt = 0
        expoh.AR = 800
        expoh.Value = 1900000
        expoh.HPM = please.roll_this("1d6+10") * expoh.CON
        expoh.Size_Cat =  "Large"

        offending_list = robot_offensive_rolls([(attack_two_rolls,1)])
        robot_offensive_systems(expoh, offending_list)

        expoh.Peripherals.extend(robotic_peripherals(expoh, 1))

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
    hobby.FAMILY_SUB = ""
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
    hobby.Peripherals.extend(robotic_peripherals(hobby, number))
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
    specs = ["Capacitors of industry."]

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
            indy.Defences.extend(robot_defensive_systems(indy, 1))

        indy.Peripherals.extend(robotic_peripherals(indy, 2))

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
            indy.Defences.extend(robot_defensive_systems(indy, 1))

        indy.Peripherals.extend(robotic_peripherals(indy, 1))

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

        indy.Peripherals.extend(robotic_peripherals(indy, 1))


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

def janitorial(maid: RobotRecord) -> RobotRecord:
    ''' insert janitorial elements into record'''

    maid.FAMILY_TYPE = "Janitorial"
    specs = ["Cleaning mopping and moping."]

    # build subtype choices
    choices = ["Industrial"]

    if maid.INT >= 12:
        choices.append("Domestic")

    if maid.Bespoke or maid.Fallthrough:
        choices = ["Industrial", "Domestic"]

    comment = "Please choose your type of Janitorial bot."
    chosen = please.choose_this(choices, comment, maid)

    if chosen == "Industrial":

        # Industrial particulars
        maid.FAMILY_SUB = "Industrial"
        maid.Adapt = 30
        maid.Value = 20000
        maid.HPM = please.roll_this("1d6") * maid.CON
        maid.Size_Cat =  "Medium"

        # robot_offensive_systems check
        if please.do_1d100_check(25):
            offenses = robot_offensive_rolls([(attack_one_rolls, 1)])
            robot_offensive_systems(maid, offenses)

        # robot_defensive_systems check
        if please.do_1d100_check(45):
            maid.Defences.extend(robot_defensive_systems(maid, 2))

        maid.Peripherals.extend(robotic_peripherals(maid, 1))

        specs.append("Combating entropy in the workplace.")
        maid.Spec_Sheet = specs

    elif chosen == "Domestic":

        # Domestic Janitorial 
        maid.FAMILY_SUB = "Domestic"
        maid.Adapt = 10
        maid.Value = 35000
        maid.HPM = please.roll_this("1d6") * maid.CON
        maid.Size_Cat =  "Small"

        # robot_offensive_systems check
        if please.do_1d100_check(10):
            offenses = robot_offensive_rolls([(attack_one_rolls, 1)])
            robot_offensive_systems(maid, offenses)

        # robot_defensive_systems check
        if please.do_1d100_check(15):
            maid.Defences.extend(robot_defensive_systems(maid, 2))

        maid.Peripherals.extend(robotic_peripherals(maid, 1))

        specs.append("Combating entropy in the home.")
        maid.Spec_Sheet = specs

    return maid # altered by side effect


def maintenance(wrench:RobotRecord) -> RobotRecord:
    '''insert maintenance bot stuff'''

    wrench.FAMILY_TYPE = "Maintenance"
    wrench.FAMILY_SUB = ""
    specs = ["Mechanic in a drum."]

    wrench.Adapt = 37
    wrench.Value = 1050000
    wrench.HPM = please.roll_this("1d4") * wrench.CON
    wrench.Size_Cat =  "Medium"

    # robot_offensive_systems check
    if please.do_1d100_check(40):
        offenses = robot_offensive_rolls([(attack_one_rolls, 1)])
        robot_offensive_systems(wrench, offenses)

    # robot_defensive_systems check
    if please.do_1d100_check(40):
        wrench.Defences.extend(robot_defensive_systems(wrench, 2))

    wrench.Peripherals.extend(robotic_peripherals(wrench, 1))

    # set up mechanic
    intel = wrench.INT
    wrench.INT = intel * 3  # temporary INT rise for skill calc
    wrench.Vocation = "Mechanic"
    # vocation.intake(wrench)
    wrench.INT = intel  # return to previous INT


    specs.append("Not a janitorial bot.")
    specs.append("Has Mechanic specs for repairs.")
    specs.append(f"Add {intel} (INT) to PT rolls.")
    wrench.Spec_Sheet = specs

    return wrench # altered by side effect


def Policing(copper: RobotRecord) -> RobotRecord:
    '''insert policing robot data into record'''

    copper.FAMILY_TYPE = "Policing"
    specs = [f"To serve and protect {copper.Base_Family}s."]

    # build subtype choices
    choices = ["Civil"]

    if copper.CON >= 15:
        choices.append("Riot")
    if copper.INT >= 15:
        choices.append("Detective")

    if copper.Bespoke or copper.Fallthrough:
        choices = ["Civil", "Riot", "Detective"]

    comment = "Please choose your policing bot type."
    chosen = please.choose_this(choices, comment, copper)

    if chosen == "Civil":

        # civilian policing
        copper.FAMILY_SUB = "Civil"
        specs.append("Mechanical street cop.")
        copper.Adapt = 10
        copper.Value = 600000
        copper.HPM = please.roll_this("3d4") * copper.CON
        copper.Size_Cat =  "Medium"

        # civil_offensive_systems
        copper.Attacks.append("Stun 4d4 intensity for 1d4 units.")
        offenses = robot_offensive_rolls([(attack_one_rolls, 1)])
        robot_offensive_systems(copper, offenses)
        copper.Defences.extend(robot_defensive_systems(copper, 1))
        copper.Peripherals.extend(robotic_peripherals(copper, 1))
        specs.append(f"Make loud commands at double CHA ({copper.CHA * 2}.")
        specs.append("Grapple and disarm with a successful to hit roll.")
        copper.Spec_Sheet = specs

    elif chosen == "Riot":

        # riot policing
        copper.FAMILY_SUB = "Riot"
        specs.append("Less lethal mob control. AKA riobot.")
        copper.Adapt = 10
        copper.Value = 300000
        copper.HPM = please.roll_this("1d4+9") * copper.CON
        copper.Size_Cat =  "Gigantic"

        # no offensive systems
        copper.Defences.extend(robot_defensive_systems(copper, 1))
        copper.Peripherals.extend(robotic_peripherals(copper, 1))

        specs.append(f"Grapple, disarm and detain up to {copper.PSTR} unruly targets.")
        specs.append(f"Crowd control devices:")

        # generate crowd control tools

        riot_policing_items = {
            (1, 20): f"Water Cannon. {copper.PSTR} targets. Hit = knocked down.",
            (21, 40): f"Tear Gas. {copper.CON} hex radius. {copper.CON} intensity. Blind for 1d8 units.",
            (41, 50): f"Stun Ray. {copper.PSTR} targets. {copper.CON} intensity. Stunned for 1d8 units.",
            (51, 60): f"Grav Disruptor.  {math.ceil(copper.CON / 2)} hex radius. {copper.CON} intensity or knocked down.",
            (61, 70): f"Force Beam {copper.PSTR} targets. {copper.PSTR} intensity. Tossed 1d4 hexes.",
            (71, 80): f"Weapon Malfunction. {math.ceil(copper.CHA / 2)} hex radius. 25 times increase powered weapons fail.",
            (81, 90): f"Battery Drain. {math.ceil(copper.INT / 2)} hex radius. Batteries drop to zero. No save.",
            (91, 101): f"Sleep Beam. {copper.CHA} targets. {copper.INT} intensity. Go to sleep.",
            "name": "Riot Policing",
            "number": "5.4",
            "die_roll": "1d100",
        }

        # add special riot stuff
        for _ in range(math.ceil(copper.INT / 3) + 1):
            specs.append(please.get_table_result(riot_policing_items))

        copper.Spec_Sheet = specs

    elif chosen == "Detective":

        copper.FAMILY_SUB = "Detective"
        specs.append("Detective, sleuth, criminologist.")
        copper.Adapt = 10
        copper.Value = 900000
        copper.HPM = please.roll_this("1d3+1") * copper.CON
        copper.Size_Cat =  "Small"

        offenses = robot_offensive_rolls([(attack_one_rolls, 1)])
        robot_offensive_systems(copper, offenses)
        copper.Defences.extend(robot_defensive_systems(copper, 1))
        copper.Peripherals.extend(robotic_peripherals(copper, 1))

        specs.append("Can order riot and civil bots around.")

        copper.Spec_Sheet = specs

        # detective can swap highest attribute into INT
        # finds the highest attribute from below
        intel = copper.INT

        dirty_list = []
        dirty_list.append(("AWE", copper.AWE))
        dirty_list.append(("CHA", copper.CHA))
        dirty_list.append(("CON", copper.CON))
        dirty_list.append(("DEX", copper.DEX))
        dirty_list.append(("PSTR", copper.PSTR))
        dirty_list = sorted(dirty_list, key=lambda tup: tup[1])
        attribute, highest = dirty_list[-1]

        if highest <= intel:
            return copper # is modified by side effect

        print("Detective may swap highest attribute to INT. Without penalty or benefit.")
        comment = f'Would you like to swap your {attribute} of {highest} to your INT of {intel}?'
        if please.say_yes_to(comment):
            setattr(copper, attribute, intel)
            setattr(copper, "INT", highest)
            copper.CF = control_factor(copper)


    return copper # is adjusted by side effects

def rescue(saviour: RobotRecord) -> RobotRecord:
    ''' insert rescue data into record'''

    saviour.FAMILY_TYPE = "Rescue"
    specs = ["Rescuing entities and environments."]
    
    # build subtype choices
    choices = ["Containment"]
    if saviour.DEX >= 22:
        choices.append("Retrieval")

    if saviour.Bespoke or saviour.Fallthrough:
        choices = ["Containment", "Retrieval"]

    comment = "Please choose your type of rescue bot. "
    chosen = please.choose_this(choices, comment, saviour)

    if chosen == "Retrieval":

        # retrieval info
        saviour.FAMILY_SUB = "Retrieval"
        specs.append("Built to retrieve entities and equipment from danger.")
        saviour.Adapt = 10
        saviour.Value = 950000
        saviour.HPM = please.roll_this("2d10+5") * saviour.CON
        saviour.Size_Cat =  "Large"

        # systems 
        fences = robot_offensive_rolls([(attack_one_rolls, 1)])
        robot_defensive_systems(saviour, fences)

        saviour.Defences.extend(robot_defensive_systems(saviour, 3))
        saviour.Peripherals.extend(robotic_peripherals(saviour, 1))

        specs.append("Exatmo hardened and environment agnostic.")
        specs.append(f"{math.ceil(saviour.PSTR / 2)} stasis chambers for holding medium sized entities.")
        specs.append("150 hexes of retractable glowing safety fencing.")

        saviour.Spec_Sheet = specs

        if not saviour.Fallthrough:
            chosen = please.choose_this(
                ["Hell yeah!", "Um, no."], "Was your retrieval bot programmed by the JIBC? "
            )
            if chosen == "Hell yeah!":
                saviour.AWE = 3
                saviour.CHA = 1
                saviour.CON = 3
                saviour.DEX = 9
                saviour.INT = 4
                saviour.PSTR = 12
                saviour.HPM = 4
                saviour.SOC = 42
                saviour.Attacks = ["Sarcasm, but only towards the vulnerable."]
                saviour.Defences = ["Use rules and protocols to avoid work."]
                saviour.Peripherals = ["A bowl to collect the tears of children."]
                saviour.FAMILY_SUB = "JIBC"
                saviour.Spec_Sheet = ["Pretends to be a veterinarian, but has no specs.","Zero resiliency."]
                saviour.Size_Cat = "Tiny"

    elif chosen == "Containment":
        saviour.FAMILY_SUB = "Containment"
        specs.append("Built to contain spillage of toxins, including fire.")
        saviour.Adapt = 10
        saviour.Value = 750000
        saviour.HPM = please.roll_this("2d10+5") * saviour.CON
        saviour.Size_Cat =  "Gigantic"

        # robot_offensive_systems chance
        if please.do_1d100_check(25):
            fences = robot_offensive_rolls([(attack_one_rolls, 1)])
            robot_defensive_systems(saviour, fences)
        saviour.Defences.extend(robot_defensive_systems(saviour, 3))
        saviour.Peripherals.extend(robotic_peripherals(saviour, 1))

        saviour.AR = 875

        specs.append("Exatmo hardened and environment agnostic.")
        specs.append(f"Detect toxins. {saviour.AWE * 10} hex range.")
        specs.append(f"Can store up to {20 * saviour.WA} kgs of toxins.")
        specs.append(f"Extinguish {5 * saviour.CON} hexes of fire.")
        specs.append("Immune to fire, but not fire weapons")
        specs.append("250 hexes of retractable glowing safety fencing.")
        specs.append("100 hexes (area) of ejectable 'safety plastic.'")
        specs.append("Plastic spray can act like a Web Gun (chap 46).")

        saviour.Spec_Sheet = specs

        return saviour # modified by side effects


def social(friend: RobotRecord) -> RobotRecord:
    '''insert social bot into record'''

    friend.FAMILY_TYPE = "Social"
    friend.FAMILY_SUB = friend.Base_Family
    specs = [f"Built to serve the {friend.Base_Family}."]
    friend.Adapt = 50
    friend.Value = 100000
    friend.HPM = please.roll_this("1d3+1") * friend.CON

    ### set family type to use ANTHRO calcs
    friend.FAMILY = "Anthro"
    friend.FAMILY_TYPE = friend.Base_Family

    anthro.anthro_hite_wate_calc(friend, "Larger")
    friend.Wate = round(friend.Wate * 1.5)
    core.hit_points_max(friend)

    ### reset to robot 
    friend.FAMILY = "Robot"
    friend.FAMILY_TYPE = "Social"
    friend.FAMILY_SUB = friend.Base_Family

    # RobotAttacks check
    if please.do_1d100_check(10):
        fences = robot_offensive_rolls([(attack_one_rolls, 1)])
        robot_offensive_systems(friend, fences)

    # RobotDefences check
    if please.do_1d100_check(85):
        friend.Defences.extend(robot_defensive_systems(friend, 1))

    friend.Peripherals.extend(robotic_peripherals(friend, 1))

    specs.append("Previously called a relations bot, or robotler.")
    specs.append(f"Mechanized, inorganic version of {friend.Base_Family}.")
    specs.append(f"Can speak up to {friend.INT * 10} languages.")
    specs.append("Can learn any intelligent language in 1d4 days.")
    specs.append(f"Can offer etiquette and customs advice on up to {friend.INT} cultures.")
    specs.append(f"Can look after up to {friend.INT * 2} organic clients.")
    specs.append("Social bots do not look after other robots.")

    friend.Spec_Sheet = specs

    return friend # adjusted by side effect


def transport(taxi: RobotRecord) -> RobotRecord:
    '''insert transport options into record'''

    taxi.FAMILY_TYPE = "Transport"
    specs = ["Getting things from one place to another."]

    # build subtype choices
    choices = ["Planetary"]

    if taxi.DEX >= 22 and taxi.INT >= 22:
        choices.append("Extra-Planetary")

    if taxi.Bespoke or taxi.Fallthrough:
        choices = ["Planetary", "Extra-Planetary"]

    comment = "Please choose your type of Transport bot. "
    chosen = please.choose_this(choices, comment, taxi)

    if chosen == "Planetary":

        # planetary transport bot
        taxi.FAMILY_SUB = "Planetary"
        specs.append("Planet side chauffer.")
        taxi.Adapt = 22
        taxi.Value = 450000
        taxi.HPM = please.roll_this("1d4+8") * taxi.CON
        taxi.Size_Cat =  "Small"

        # RobotAttacks check
        if please.do_1d100_check(50):
            fences = robot_offensive_rolls([(attack_one_rolls, 1)])
            robot_offensive_systems(taxi, fences)

        # RobotDefences check
        if please.do_1d100_check(40):
            taxi.Defences.extend(robot_defensive_systems(taxi, 1))

        taxi.Peripherals.extend(robotic_peripherals(taxi, 1))

        specs.append(
            f"Expert driver can divide {taxi.INT + 5} between vehicles."
        )
        specs.append(f"Driving an unknown vehicle {taxi.INT * 4}%")
        specs.append("Any inatmo vehicle. No exatmo vehicles.")
        specs.append("Not skilled in vehicle combat.")
        specs.append("Can act as a steward on exatmo vehicles.")

        taxi.Spec_Sheet = specs

    elif chosen == "Extra-Planetary":

        # extra planetary transport bot
        taxi.FAMILY_SUB = "Extra-Planetary"
        specs.append("Space vehicle pilot.")
        taxi.Adapt = 22
        taxi.Value = 450000
        taxi.HPM = please.roll_this("1d4+8") * taxi.CON
        taxi.Size_Cat =  "Small"

        # RobotAttacks check
        if please.do_1d100_check(50):
            fences = robot_offensive_rolls([(attack_one_rolls, 1)])
            robot_offensive_systems(taxi, fences)

        # RobotDefences check
        if please.do_1d100_check(40):
            taxi.Defences.extend(robot_defensive_systems(taxi, 1))

        taxi.Peripherals.extend(robotic_peripherals(taxi, 1))

        specs.append(f"Expert pilot can divide up {taxi.INT + 5} between vehicles.")
        specs.append(
            f"Can only pilot exatmo vehicles. {taxi.INT * 4}% chance to drive vehicles within space ship."
        )
        specs.append(f"Driving an unknown vessel {taxi.INT * 4}%")
        specs.append("Not skilled in space vehicle combat.")
        specs.append("Has a steward skill for ships with organics.")

        taxi.Spec_Sheet = specs

    return


def veterinarian(doc: RobotRecord) -> RobotRecord:
    '''insert veterinarian data into record'''

    doc.FAMILY_TYPE = "Veterinarian"
    specs = [
        "Veterinarian in a drum.",
        "Very high regard for organic life.",
    ]

    # build subtype choices
    choices = ["Diagnostic"]

    if doc.DEX >= 23 and doc.INT >= 21:
        choices.append("Interventional")

    if doc.Bespoke or doc.Fallthrough:
        choices =  ["Diagnostic", "Interventional"]

    comment = "Please choose your type of veterinarian bot. "
    chosen = please.choose_this(choices, comment, )

    if chosen == "Diagnostic":

        # diagnostic robot info
        doc.FAMILY_SUB = "Diagnostic"
        specs.append("Prefers to FIGURE than fix.")
        doc.Adapt = 10
        doc.Value = 2250000
        doc.HPM = 2 * doc.CON
        doc.Size_Cat =  "Small"

        # no attacks 
        # RobotDefences chance
        if please.do_1d100_check(10):
            doc.Defences.extend(robot_defensive_systems(doc, 1))

        doc.Peripherals.extend(robotic_peripherals(doc, 1))
        doc.Vocation = "Veterinarian"

        specs.extend([
            f"Vet thinking task rolls +{doc.INT * 2} bonus.",
            "Excellent at diagnosis and planning.",
            "Only simple interventions.",
            f"Identify medical equipment and pharma {doc.INT * 5}%.",
            "Has veterinarian vocation"
            ])

        doc.Spec_Sheet = specs

    elif chosen == "Interventional":

        # interventional specs
        doc.FAMILY_SUB = "Interventional"
        specs.append("Prefers to FIX  than figure.")
        doc.Adapt = 10
        doc.Value = 5000000
        doc.HPM = 2 * doc.CON
        doc.Size_Cat =  "Medium"

        # no attacks 
        # Defences check
        if please.do_1d100_check(10):
            doc.Defences.extend(robot_defensive_systems(doc, 1))
        # Peripherals check
        doc.Peripherals.extend(robotic_peripherals(doc, 1))

        specs.extend([
            "Often needs vet direction.",
            "Can perform all manner of interventions tasks.",
            f"Vet intervention task rolls +{doc.INT * 3} bonus.",
            f"Anaesthesia has a range of {math.ceil(doc.PSTR / 3)} hexes.",
            "Does NOT have a vocation" 
            ])

        doc.Spec_Sheet = specs

    return doc # is manipulated by side effect


#####################################
# build a FRESH robot persona
#####################################

### build a fresh robot persona
def fresh_robot(player_name:str) -> None:
    """
    builds A FRESH robot persona using EXP persona creation
    """
    fresh = RobotRecord()
    fresh.Player_Name = player_name
    please.setup_persona(fresh)

    fresh.Base_Family = please.get_table_result(table.robot_base_family) # must be first for Android
    core.initial_attributes(fresh)
    fresh.CF = control_factor(fresh)
    core.movement_rate(fresh)
    core.wate_allowance(fresh)
    fresh.Power_Plant = please.get_table_result(table.robotic_power_plant)
    fresh.Power_Reserve = fresh.CON
    fresh.Sensors = robotic_sensors(fresh)
    core.base_armour_rating(fresh)

    ### choose the FAMILY_TYPE
    fresh.FAMILY_TYPE = please.choose_this(list_eligible_robot_types(fresh), "Please choose a robot type.")
    robot_types_func_map[fresh.FAMILY_TYPE](fresh)

    if fresh.FAMILY_TYPE != "Android":
        fresh.Attacks.append(f'Ram: {please.get_table_result(table.robot_ram_dam)}') # every robot can ram, except Androids

    ### requires bot_type
    fresh.Locomotion = robotic_locomotion(fresh)
    robot_hite_wate_calc(fresh)
    fresh.Quick_Description = robot_description(fresh)

    if fresh.Vocation != "Robot":
        vocation.set_up_first_time(fresh)

    if fresh.RP_Cues:
        core.build_RP_role_play(fresh) 

    please.wrap_up_persona(fresh)



#####################################
# build a BESPOKE robot persona
#####################################

def bespoke_robot(player_name:str) -> None:
    """
    builds A BESPOKE robot persona using EXP persona creation
    """
    bespoke = RobotRecord()
    bespoke.Bespoke = True
    bespoke.Player_Name = player_name
    please.setup_persona(bespoke)

    base_family_choices = please.list_table_choices(table.robot_base_family)
    bespoke.Base_Family = please.choose_this(base_family_choices, "Choose a base family", bespoke)

    core.initial_attributes(bespoke) # cannot use descriptive attributes until later
    bespoke.CF = control_factor(bespoke)
    core.movement_rate(bespoke)
    core.wate_allowance(bespoke)
    bespoke.Power_Reserve = bespoke.CON
    
    if please.say_yes_to("Determine robot type by ATTRIBUTES? <- you don't choose."):
        bespoke.FAMILY_TYPE = please.choose_this(list_eligible_robot_types(bespoke), "Please choose a robot type.")
    else:
        family_type_choices = please.list_table_choices(table.single_roll_robot_type)
        bespoke.FAMILY_TYPE = please.choose_this(family_type_choices, "Choose robot type", bespoke)


    power_plant_choices = please.list_table_choices(table.robotic_power_plant)
    bespoke.Power_Plant = please.choose_this(power_plant_choices, "Choose a power plant", bespoke)

    sensor_choices = please.list_table_choices(table.robotic_sensor_types)
    sensor_amount = math.ceil(bespoke.AWE / 4)
    sensors = []

    if please.say_yes_to("Randomly determine SENSORS? "):
        bespoke.Sensors = robotic_sensors(bespoke)
    else:
        for _ in range(sensor_amount):
            sensors.append(please.choose_this(sensor_choices, "Choose a sensor."))
        bespoke.Sensors.extend(sensors)

    core.base_armour_rating(bespoke)

    robot_types_func_map[bespoke.FAMILY_TYPE](bespoke)

    if bespoke.FAMILY_TYPE != "Android":
        bespoke.Attacks.append(f'Ram: {please.get_table_result(table.robot_ram_dam)}') # every robot can ram, except Androids

    ### past this line requires bot_type

    bespoke.Locomotion = robotic_locomotion(bespoke)

    robot_hite_wate_calc(bespoke)
  
    if bespoke.Vocation != "Robot":
        vocation.set_up_first_time(bespoke)

    vocation.exps_level_picker(bespoke)

    if bespoke.Level > 1:
        print(f"You have {bespoke.Level - 1} additional INTEREST(s) and SKILL(s).")
        bespoke.Interests.extend(
            vocation.update_interests(bespoke, (bespoke.Level - 1))
        )
        bespoke.Skills.extend(vocation.update_skills(bespoke, (bespoke.Level - 1)))

    ### generate RP EXPS points
    bespoke.EXPS = 42 if bespoke.Level == 1 else vocation.convert_levels_to_exps(bespoke)

    if please.say_yes_to("Do you want any descriptive changes? "):
        core.descriptive_attributes(bespoke)

    if bespoke.RP_Cues:
        core.build_RP_role_play(bespoke) 

    bespoke.Quick_Description = robot_description(bespoke)

    please.wrap_up_persona(bespoke)


#####################################
# build a RANDO robot persona
#####################################

def rando_robot(player_name:str) -> None:
    """
    builds A RANDOM robot persona using EXP persona creation
    """
    rando = RobotRecord()
    rando.Fallthrough = True
    rando.Player_Name = player_name
    please.setup_persona(rando)

    base_family_choices = please.list_table_choices(table.robot_base_family)
    rando.Base_Family = please.choose_this(base_family_choices, "rando", rando)

    core.initial_attributes(rando)
    rando.CF = control_factor(rando)
    core.movement_rate(rando)
    core.wate_allowance(rando)
    rando.Power_Reserve = rando.CON
    
    power_plant_choices = please.list_table_choices(table.robotic_power_plant)
    rando.Power_Plant = please.choose_this(power_plant_choices, "rando", rando)
    rando.Sensors = robotic_sensors(rando)
    core.base_armour_rating(rando)
    rando.FAMILY_TYPE = choice(please.list_table_choices(table.single_roll_robot_type))
    robot_types_func_map[rando.FAMILY_TYPE](rando)

    if rando.FAMILY_TYPE != "Android":
        rando.Attacks.append(f'Ram: {please.get_table_result(table.robot_ram_dam)}') # every robot can ram, except Androids

    ### past this line requires bot_type

    rando.Locomotion = robotic_locomotion(rando)
    robot_hite_wate_calc(rando)
   
    if rando.Vocation != "Robot":
        vocation.set_up_first_time(rando)

    vocation.exps_level_picker(rando)

    if rando.Level > 1:
        rando.Interests.extend(vocation.update_interests(rando, (rando.Level - 1)))
        rando.Skills.extend(vocation.update_skills(rando, (rando.Level - 1)))

    rando.EXPS = 42 if rando.Level == 1 else vocation.convert_levels_to_exps(rando)

    if rando.RP_Cues:
        core.build_RP_role_play(rando) 

    rando.Quick_Description = robot_description(rando)

    please.wrap_up_persona(rando)

robot_types_func_map = {
    "Android": android,
    "Combot": combot,
    "Datalyzer": datalyzer,
    "Explorations": explorations,
    "Hobbot": hobbot,
    "Industrial": industrial,
    "Janitorial": janitorial,
    "Maintenance": maintenance,
    "Policing": Policing,
    "Rescue": rescue,
    "Social": social,
    "Transport": transport,
    "Veterinarian": veterinarian,
}

