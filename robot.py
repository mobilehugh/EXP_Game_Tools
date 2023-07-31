import math
import secrets

import anthro
import outputs
import please
import table
import vocation
import core
import mutations


def robot_workflow():
    """
    player robot versus referee person vs persona maintenance
    """

    # clearance for Clarence
    please.clear_console()

    workflow_function_map = {
        "Fresh Robot (New Player)":fresh_robot,
        "Bespoke Robot":bespoke_robot,
        "Random Robot":rando_robot,
        "Maintenance":please.do_referee_maintenance,
    }

    list_comment = "Choose a robot workflow:"
    option_list = list(workflow_function_map.keys()) # fix does not guarantee [0] default
    workflow_desired = please.choose_this(option_list, list_comment)

    if workflow_desired in workflow_function_map:
        workflow_function_map[workflow_desired]()




def robot_fabricator_family(object: dict) -> None:
    """
    generates the family type that fabricated the robot
    """
    object.Base_Family = please.get_table_result(table.robot_fabricator_list)
    return


def control_factor(object: dict) -> None:
    """
    generates the control factor for the robot
    updates the CF for an existing robot
    """
    expected_CF = object.INT + (object.INT_Prime * object.Level)
    if "CF" not in object.__dict__:  # make a fresh CF
        object.CF = expected_CF

    else:  # update the CF normally, or just by increasing be base (usually bumped up)
        object.CF = (
            expected_CF
            if expected_CF > object.CF
            else (object.CF + object.Level * object.INT_Prime)
        )

    return




def robotic_power_source(object):
    object.Power_Plant = please.get_table_result(table.robotic_power_plant)
    object.Power_Reserve = object.CON
    return


def robotic_sensors(object):
    sensor_list = []
    rolls = math.ceil(object.AWE / 4)

    for i in range(rolls):
        sensor_list.append(please.get_table_result(table.robotic_sensor_types))

    object.Sensors = sensor_list

    return


def robotic_locomotion(object):
    primary, secondary = please.get_table_result(table.primary_robotic_locomotion)
    amount = ""

    if secondary == "Secondary":
        secondary = " moving " + please.get_table_result(
            table.secondary_robotic_locomotion
        )
    elif secondary == "None":
        secondary = ""
    else:
        amount = str(please.roll_this(secondary)) + " "
        secondary = ""

    object.Locomotion = amount + primary + secondary

    if object.Bot_Type == "Android" or object.Bot_Type == "Social":
        object.Locomotion = "Limbs are per " + object.Base_Family

    return


def list_eligible_robot_types(object: dict) -> list:
    """
    makes a 4 character string from primes to list of robots type options
    """
    auto_picker = (
        f"{object.CON_Prime}{object.DEX_Prime}{object.INT_Prime}{object.PSTR_Prime}"
    )

    return table.auto_prime_select_robot_type[auto_picker]


def fresh_robot_type(object):
    """
    Choose robot type from list of eligible robot types
    """
    choices = list_eligible_robot_types(object)
    comment = "Please choose a robot type:"
    chosen = please.choose_this(choices, comment)
    object.Bot_Type = choice
    robot_type_function_pivot[object.Bot_Type](object)
    return  # return for robot typing


def robot_size_wate_hite(object: dict) -> None:
    """
    fills the object's size, wate and hite attributes
    """

    if object.Bot_Type in [
        "Android",
        "Social",
    ]:  # if it's an android or social already calculated
        return

    ### object.Size is determined by robot type

    ### get wate from size of robot
    object.Wate = please.roll_this(table.robot_size_to_wate[object.Size])
    object.Wate_Suffix = "kgs"

    ### get hite from wate to hite table
    for hite_range, roll in table.robot_wate_to_hite.items():
        if object.Wate in hite_range:
            object.Hite = please.roll_this(roll)
            break
    object.Hite_Suffix = "cms"

    return


def robotic_peripherals(object: dict, number: int) -> list:
    peripheral_list = []
    secondary_number = 0

    ### add the primary, less fancy, peripherals
    while len(peripheral_list) < number:
        peripheral = please.get_table_result(table.primary_robotic_peripheral)
        peripheral_list.append(peripheral)

        if peripheral == "Extra Roll":
            number += 1
            peripheral_list.pop()

        if peripheral == "Choose":
            peripheral_list.pop()
            choices = please.list_table_choices(table.primary_robotic_peripheral)
            chosen = please.choose_this(choices, "Choose a primary peripheral")
            peripheral_list.append(chosen)

        if peripheral == "Secondary":
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

        if peripheral == "Choose":
            peripheral_list.pop()
            choices = please.list_table_choices(table.secondary_robotic_peripheral)
            chosen = please.choose_this(choices, "Choose a secondary peripheral")
            peripheral_list.append(choice)

    ### fix peripheral list for secondary effects
    for position, peripheral in enumerate(peripheral_list):

        if peripheral == "Vocation Computer":
            all_vocations = [key for key in table.attributes_improve_by_vocation.keys()]
            new_peripheral = f"{secrets.choice(all_vocations)} vocation computer"
            peripheral_list[position] = new_peripheral

        elif peripheral == "Cybernetic Part":
            toy_type = please.get_table_result(table.toy_categories)
            new_peripheral = f"A hard wired toy - {toy_type}"
            peripheral_list[position] = new_peripheral

        elif peripheral == "Vocation":
            all_vocations = [
                key
                for key in table.attributes_improve_by_vocation.keys()
                if key != "Knite"
            ]
            object.Vocation = secrets.choice(all_vocations)
            peripheral_list[position] = f"Robot has the vocation {object.Vocation}"

        elif peripheral.split(" ")[0] == "Detect":
            peripheral_list[position] = f"{peripheral} {object.AWE} km range"

        elif peripheral.split(" ")[0] == "Identify":
            peripheral_list[
                position
            ] = f"{peripheral} {2*object.INT * object.INT_Prime}%"

        elif peripheral == "Heightened CF":
            object.CF = object.CF * 2

        elif peripheral == "Increase Speed":
            object.Move = object.Move * please.roll_this("1d4+1")

        elif peripheral == "Increase WA":
            object.WA = object.WA * please.roll_this("1d6+1")

        elif peripheral == "Mental Mutation":
            add_mutation = True
            while add_mutation:
                working_mutation = please.get_table_result(
                    mutations.mental_mutation_random
                )[1](object)
                if working_mutation.kind != "defect":
                    peripheral_list[
                        position
                    ] = f"Mutation effect {working_mutation.name}"
                    add_mutation = False

                else:
                    object.Mutations.pop(working_mutation.name)

        elif peripheral == "Physical Mutation":
            add_mutation = True
            while add_mutation:
                working_mutation = please.get_table_result(
                    mutations.physical_mutation_random
                )[1](object)
                if working_mutation.kind != "defect":
                    peripheral_list[
                        position
                    ] = f"Mutation effect {working_mutation.name}"
                    add_mutation = False

                else:
                    object.Mutations.pop(working_mutation.name)

    return peripheral_list


def robot_offensive_systems(object: dict, attack_table: int, rolls: int) -> list:
    """
    returns a list of offensive systems based on table level and number of rolls
    """

    attack_list = []  # list of the robot attacks
    attack_table_counter = [0, 0, 0, 0]  # empty list counter for attack tables
    attack_table_counter[
        attack_table - 1
    ] += rolls  # set initial list counter for attack tables

    number_to_table_pivot = {
        0: table.attack_table_one,
        1: table.attack_table_two,
        2: table.attack_table_three,
        3: table.attack_table_four,
    }

    ### all robots can ram
    attack_list.append("Ram with " + please.get_table_result(table.robot_ram_dam))

    while sum(attack_table_counter) > 0:  # keep adding attacks until no rolls are left

        for table_number, roll_number in enumerate(
            attack_table_counter
        ):  # loop through each attack table counter

            if roll_number == 0:  # jump this table if zero rolls
                continue

            for v in range(roll_number):
                attack_thing = please.get_table_result(
                    number_to_table_pivot[table_number]
                )

                if "Table" in attack_thing:
                    __, add_table_number, add_roll_number = attack_thing.split(" ")
                    add_roll_number = int(add_roll_number)
                    add_table_number = int(add_table_number) - 1
                    attack_table_counter[add_table_number] += add_roll_number
                    attack_table_counter[table_number] -= 1

                else:
                    attack_list.append(attack_thing)
                    attack_table_counter[table_number] -= 1

    ### Modify attack_list based on the rolls
    for attack in attack_list:
        attack_location = attack_list.index(
            attack
        )  # find the location of the attack in the list

        if "Type A" in attack or "Type B" in attack:

            weapon_desc = "Type A" if "Type A" in attack else "Type B"
            weapon_type = (
                please.get_table_result(table.attack_type_A)
                if "Type A" in attack
                else please.get_table_result(table.attack_type_B)
            )
            weapon_name, weapon_damage = weapon_type.split(" ")

            if "Striking" in attack:
                attack_list[
                    attack_location
                ] = f"{weapon_name} standard {weapon_desc} attack ({weapon_damage})"
            elif "Electro" in attack:
                attack_list[
                    attack_location
                ] = f"{weapon_name} electrified {weapon_desc} attack ({weapon_damage}+2d8)"
            elif "Vibro" in attack:
                attack_list[
                    attack_location
                ] = f"{weapon_name} vibrating {weapon_desc} attack ({weapon_damage}+20)"
            elif "Stun" in attack:
                attack_list[
                    attack_location
                ] = f"{weapon_name} stunning {weapon_desc} attack ({weapon_damage} + stun)"
            elif "Inertia" in attack:
                attack_list[
                    attack_location
                ] = f"{weapon_name} inertial {weapon_desc} attack ({weapon_damage}*3+10)"

        elif attack == "Defensive System":
            pass  # we will add a defence once that system is created

    return attack_list


def robot_defensive_systems(object: dict, number: int) -> list:
    """
    returns a list of defenses for the robot
    """
    defence_list = []

    ### defensive systems does not have extra roll or choose.
    for __ in range(number):
        defence_list.append(please.get_table_result(table.robotic_defenses))

    ### make defensive system calculations

    for defense in defence_list:
        defence_location = defence_list.index(
            defense
        )  # find location of defense in defence list
        if defense == "Aunty Missile":
            defence_list[
                defence_location
            ] = f"Aunty Missile: AR +{please.roll_this('1d6')*50} vs missiles"
        elif defense == "Aunty Personnel":
            defence_list[
                defence_location
            ] = f"Aunty Personnel: Lethal 3d6 HPS, Non-Lethal 4d6 intensity"
        elif defense == "Increase AR":
            bump = please.roll_this("1d6") * 50
            object.AR += bump
            defence_list[
                defence_location
            ] = f"Armour rating +{bump} now {object.AR} (added)"
        elif defense == "Artifact Armour":
            pass  # eventually insert some armour here
        elif defense == "Camouflage":
            defence_list[
                defence_location
            ] = f"Camouflage against {object.Sensors} sensors"
        elif defense == "Detect Ambush":
            defence_list[
                defence_location
            ] = f"Detect Ambush: AWE is {object.AWE * 4} vs ambush"
        elif defense == "Diffuse Explosives":
            defence_list[
                defence_location
            ] = f"Diffuse Explosives: {object.INT*2} and level {object.Level+5} vs explosives."
        elif defense == "Evasive Action":
            defence_list[
                defence_location
            ] = f"Evasive Action: no move penalties when running away."
        elif defense == "Force Field":
            defence_list[
                defence_location
            ] = f"Force Field: {please.roll_this('1d4')*25} HPS  (cumulative)"
        elif defense == "Increase HPM":
            bump = 1 + (please.roll_this("1d6") / 10)
            object.HPM = math.ceil(object.HPM * bump)
            defence_list[defence_location] = f"Increase HPM to {object.HPM} HPS (added)"
        elif defense == "Mental Mutation":
            fresh_amount = True

            while fresh_amount:
                fresh_amount = False
                working_mutation = please.get_table_result(
                    mutations.mental_mutation_random
                )[1](object)
                if (
                    working_mutation.kind == "Defect"
                    or working_mutation.kind == "non-combat"
                ):
                    fresh_amount = True
                    object.Mutations.pop(working_mutation.name)

            defence_list[
                defence_location
            ] = f"Mental Mutation: {working_mutation.name} (added)"

    return defence_list


def robot_description(object: dict) -> None:
    """
    creates a wholly random robot description and colour
    """

    ### do none of this if android or social
    if object.Bot_Type == "Android":
        object.Description = "Looks like any other " + object.Base_Family.lower()
        return
    elif object.Bot_Type == "Social":
        object.Description = "Looks like a mechanical " + object.Base_Family.lower()
        return

    ### correct for medium size
    sized = (
        object.Size if object.Size not in ["Medium", "Nano"] else f"{object.Size} sized"
    )

    ### generate the base shape
    base_shape = please.get_table_result(table.base_shape)
    if base_shape == "Descriptive":
        base_shape = please.get_table_result(table.descriptive_shapes)

    ### maybe mangle the base shape
    if please.do_1d100_check(60):
        base_shape_mangle = " " + please.get_table_result(table.shape_mangle)
    else:
        base_shape_mangle = ""

    ### are you adornable?
    if please.do_1d100_check(75):
        adornmentations = " with " + please.get_table_result(table.adornage)
    else:
        adornmentations = ""

    ### get the base colour
    base_colour = please.get_table_result(table.colour_bomb)

    ### maybe accent the colour
    if please.do_1d100_check(50):
        colour_accent = " and " + please.get_table_result(table.colour_bomb)
    else:
        colour_accent = ""

    ###############################
    ###  locomotion and appearance
    ###############################

    # loco = object.Locomotion
    base_loco = ""
    loco_split = object.Locomotion.split(" ")

    ### looking at no complementary locomotion type
    floating = False  # if false uses base_loco
    if loco_split[0] == "Anti-Grav" or loco_split[0] == "Magnetic":
        floating = True
        base_loco = ""

    ### grammar fixing 2 legs vs 1 leg
    elif loco_split[0].isdigit():
        one_leg = True if int(loco_split[0]) == 1 else False
        base_loco_ending = (
            " ".join(loco_split[1:]) if len(loco_split) > 2 else loco_split[1]
        )
        if one_leg:
            base_loco = f" on a {base_loco_ending[0:-1]}"
        else:
            base_loco = f" on {base_loco_ending}"

    ### grammar fixing something with something
    elif "moving" in loco_split:
        betweener = secrets.choice(
            ["moved by", "pushed by", "propelled by", "driven by"]
        )
        base_loco = f" and {loco_split[2]} {betweener} {loco_split[0]}"

    elif "Slog" in loco_split or "Chemical" in loco_split:
        betweener = secrets.choice(
            ["sitting on a", "mounted on a", "on top of a" "carried by a", "atop a"]
        )
        base_loco = f" {betweener} {loco_split[0]} {loco_split[1]}"

    elif "Teleport" in loco_split:
        base_loco = " no visible means of locomotion"

    else:
        base_loco = f" on {loco_split[0]}"

    ### apply the final attribute to object
    object.Description = f"A {'floating ' if floating else ''}{sized.lower()} {base_colour}{colour_accent}{base_shape_mangle} {base_shape}{adornmentations}{'.' if floating else base_loco.lower()}{'' if floating else '.'}"

    return


def robot_persona_name(object):

    print("\nWhen you are creating a robot persona you are also creating a MODEL.")
    print(
        "Your robot type is "
        + object.Bot_Type.upper()
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


def android(object: dict) -> None:
    """
    inject the android attributes into the object
    """

    ### androids are odd in that they skip most of the robot attributes

    ### robot nomenclature
    object.FAMILY = "Robot"
    object.FAMILY_TYPE =  "Android"
    object.FAMILY_SUB = object.Base_Family

    ### core values
    object.Adapt = 1
    object.Value = 100000000
    object.Size = "Medium"
    anthro.anthro_hit_points_fresh(object)

    object.Attacks = []
    object.Defences = []
    object.Peripherals = []

    ### hite and wate EXCEPTION for android
    #object.Anthro_Type = object.Base_Family
    # this is wrong Anthro_Type is now FAMILY_TYPE == Android
    # must now get wate with Base_Family
    # points out error of using objects and side effects 

    anthro.anthro_size_fresh(object)
    object.Wate = round(object.Wate * 1.3)

    ### vocation EXCEPTION for android
    type_options = vocation.attribute_determined(object)
    comment = "Choose your vocation."
    type_choice = please.choose_this(type_options, comment)
    object.Vocation = type_choice
    vocation.set_up_first_time(object)

    ### building the spec sheet
    specs = [f"Built in the image of their maker ({object.FAMILY_SUB})."]
    specs.append(f"Has no biologic life force.")
    specs.append(f"Works as a {object.Vocation}.")
    object.Spec_Sheet = specs
    return


def combot(object: dict) -> None:
    """
    inject the combot attributes into the object
    """
    ### robot nomenclature
    object.FAMILY = "Robot"
    object.FAMILY_TYPE =  "Combot"

    ### subtype determination
    sub_types = ["Expendable"]
    if object.CON >= 20:
        sub_types.append("Defensive")
    if object.CON >= 19 and object.DEX >= 15:
        sub_types.append("Light Offensive")
    if object.CON >= 23 and object.PSTR >= 27:
        sub_types.append("Heavy Offensive")
    comment = "Please choose combot sub-type,"
    object.FAMILY_SUB = please.choose_this(sub_types, comment)

    ### core values may be overridden
    object.Adapt = 0
    object.Value = 500000
    object.Size = "Medium"
    object.HPM = object.CON * 5

    object.Attacks = []
    object.Defences = []
    object.Peripherals = []

    ### generic spec sheet
    specs = [f"Not too concerned about base family ({object.Base_Family})."]

    if object.FAMILY_SUB == "Expendable":

        ### expendable nomenclature
        object.FAMILY_SUB = "Expendable"

        ### expendable core values
        object.Attacks = robot_offensive_systems(object, 1, 1)
        object.Defences = robot_defensive_systems(object, 1)
        object.Peripherals = robotic_peripherals(object, 1)

        ### expendable spec sheet
        specs.append("Robotic general infantry.")
        specs.append("Somewhat nihilistic outlook.")
        specs.append("Can drive military vehicles.")
        object.Spec_Sheet = specs
        return

    elif object.FAMILY_SUB == "Defensive":

        ### defensive nomenclature
        object.FAMILY_SUB = "Defensive"

        ### defensive core values
        object.Adapt = 1
        object.Value = 10000000
        object.Size = "Large"
        object.HPM = object.CON * please.roll_this("1d10+20")

        object.Attacks = robot_offensive_systems(object, 1, 1)
        object.Defences = robot_defensive_systems(object, math.ceil(object.CON / 4))
        object.Peripherals = robotic_peripherals(object, 1)

        ### defensive spec sheet
        specs.pop()
        specs.append("Prefers a non-violent path")
        specs.append("Demoralize with pithy comments.")
        specs.append(f"Fortify against an attack {object.INT * 4}%.")
        specs.append(f"Intruder detection {object.AWE * 10} hex radius.")
        specs.append(f"Anti-detection detection {object.AWE + object.INT}%")
        specs.append(f"Identify weapon that inflicts damage {object.INT * 2}%")
        object.Spec_Sheet = specs

        return

    elif object.FAMILY_SUB == "Light Offensive":

        ### light offensive nomenclature
        object.FAMILY_SUB = "Light Offensive"

        ### light offensive core values
        object.Adapt = -50
        object.Value = 100000000
        object.Size = "Large"
        object.HPM = object.CON * please.roll_this("1d10+15")

        object.Attacks = robot_offensive_systems(object, 2, 2)
        more_attacks = robot_offensive_systems(object, 3, 1)
        object.Attacks = object.Attacks + more_attacks
        object.Defences = robot_defensive_systems(object, 2)
        object.Peripherals = []

        ### light offensive spec sheet
        specs.append("Violent solutions are preferable.")
        lesser_bots = please.roll_this("1d4-1")
        if lesser_bots > 0:
            specs.append(f"Commands {lesser_bots} expendable combot(s).")

        object.Spec_Sheet = specs
        return

    elif object.FAMILY_SUB == "Heavy Offensive":

        ### heavy offensive nomenclature
        object.FAMILY_SUB = "Heavy Offensive"

        ### heavy offensive core values
        object.Adapt = -100
        object.Value = 1000000042
        object.Size = "Gigantic"
        object.HPM = object.CON * please.roll_this("1d10+15")

        level_two_attacks = robot_offensive_systems(object, 2, 1)
        level_three_attacks = robot_offensive_systems(object, 3, 1)
        level_four_attacks = robot_offensive_systems(object, 4, 1)

        object.Attacks = level_two_attacks + level_three_attacks + level_four_attacks
        object.Defences = robot_defensive_systems(object, 3)
        object.Peripherals = []

        ### armour rating EXCEPTION  for heavy offensive combot
        object.AR = 775 if object.AR < 775 else object.AR

        ### integrated heavy weapon EXCEPTION  for heavy offensive combot
        roll = please.roll_this("1d100") + object.PSTR
        for range, weapon in table.combot_heavy_weapons.items():
            if roll in range:
                object.Attacks.append(weapon)
                break

        ### heavy offensive spec sheet
        specs.append("Mass destruction is preferred solution")
        object.Spec_Sheet = specs
        return

    return


def datalyzer(object: dict) -> None:
    """
    inject the datalyzer attributes into the object
    """

    ### datalyzer nomenclature
    object.FAMILY = "Robot"
    object.FAMILY_TYPE =  "Datalyzer"
    object.FAMILY_SUB = "Data Nerd"

    ### core values
    object.Adapt = 15
    object.Value = 10000 * object.INT
    object.Size = "Small"
    object.HPM = please.roll_this("1d2+2") * object.CON

    object.Attacks = (
        [] if not please.do_1d100_check(5) else robot_offensive_systems(object, 1, 1)
    )
    object.Defences = robot_defensive_systems(object, 1)
    if please.do_1d100_check(24):
        object.Defences.append(robot_defensive_systems(object, 1))
    object.Peripherals = robotic_peripherals(object, 2)

    ### mental mutation EXCEPTION for datalyzer
    if please.do_1d100_check(
        table.datalyzer_mental_chance[object.Base_Family] + object.INT
    ):
        no_mutation_yet = True
        while no_mutation_yet:
            working_mutation = please.get_table_result(mutations.mental_mutation_random)[1](
                object
            )
            if working_mutation.kind != "defect":
                no_mutation_yet = False

    ### datalyzer spec sheet
    specs = ["Tin can thinkers."]
    object.Spec_Sheet = specs

    return


def explorations(object):
    specs = ["Designed to explore, learn and report."]
    intel = object.INT
    con = object.CON

    # build subtype choices
    choices = ["Planetary"]
    if intel >= 24:
        choices.append("Extra-planetary")
    comment = "Please choose your Explorations bot type."
    chosen = please.choose_this(choices, comment)

    if chosen == "Planetary":
        object.FAMILY_SUB = "Planetary"
        specs.append("Created to explore their own planet.")
        object.Adapt = 0
        object.Value = 250000
        object.HPM = please.roll_this("1d6+10") * con
        object.Size = "Outdoor"
        robot_size_wate_hite(object)
        # RoboticAttack check
        if please.do_1d100_check(25):
            robot_offensive_systems(object, 1)
        else:
            object.Robot_Attacks = []
        robot_defensive_systems(object, 1)
        robotic_peripherals(object, 1)

        specs.append("Atmospheric analysis.")
        specs.append("Communications.")
        specs.append("Mineral identification.")
        specs.append("Detect Toxins. Rads, poison etc.")
        specs.append("Obsessed with collecting samples.")

        object.Spec_Sheet = specs

    elif chosen == "Extra-planetary":
        object.FAMILY_SUB = "Extra-planetary"
        specs.append("Created to explore unknown planets.")
        object.Adapt = 0
        object.AR = 800
        object.Value = 1900000
        object.HPM = please.roll_this("1d6+10") * con
        object.Size = "Outdoor"
        robot_size_wate_hite(object)
        robot_offensive_systems(object, 1)
        robot_defensive_systems(object, 3)
        robotic_peripherals(object, 1)

        specs.append("Atmospheric analysis.")
        specs.append("Mineral identification.")
        specs.append("Detect Toxins. Rads, poison etc.")
        specs.append("Obsessed with collecting samples.")
        specs.append("Comprehend languages and alien intelligence.")
        specs.append("Terrain mapping.")
        specs.append("Exatmo hardened.")
        object.Spec_Sheet = specs

    return


def hobbot(object):
    object.FAMILY_SUB = ";ldsafkjdsf"
    specs = ["Highly modified hobbyist machines."]
    con = object.CON
    object.Adapt = 84
    # value moved due to calculations
    object.HPM = please.roll_this("2d4") * con
    object.Size = "Indoor"
    robot_size_wate_hite(object)
    # robot_offensive_systems chance
    if please.do_1d100_check(10):
        robot_offensive_systems(object, 1)
    else:
        object.Robot_Attacks = []
    # RobotDefences chance
    if please.do_1d100_check(50):
        robot_defensive_systems(object, 1)
    else:
        object.Defences = []
    # robotic_peripherals are random
    number = please.roll_this("2d4")
    robotic_peripherals(object, number)
    object.Value = 10000 + 20000 * number

    specs.append("Have lots of peripherals.")
    specs.append("+2DD bonus for mechanics.")
    specs.append("No two are the same.")
    object.Spec_Sheet = specs

    return


def industrial(object):
    specs = ["Building, lifting, moving."]
    intel = object.INT
    dex = object.DEX
    pstr = object.PSTR
    con = object.CON
    awe = object.AWE
    wa = object.WA
    cf = object.CF
    move = object.MoveRate

    # build subtype choices
    # fix this system for intel pstr and max
    choices = []
    if intel >= dex and intel >= pstr:
        choices.append("Construction")
    if pstr >= dex and pstr >= intel:
        choices.append("Lifting")
    if dex >= pstr and dex >= intel:
        choices.append("Moving")
    comment = "Please choose your Indutrial bot type."
    chosen = please.choose_this(choices, comment)

    if chosen == "Construction":
        object.FAMILY_SUB = "Construction"
        specs.append("Fabricator Mechanichus.")
        object.Adapt = 5
        object.Value = 50000
        object.HPM = please.roll_this("1d4+8") * con
        object.Size = "Indoor"
        robot_size_wate_hite(object)
        robot_offensive_systems(object, 2)
        # robot_defensive_systems check
        if please.do_1d100_check(15):
            robot_defensive_systems(object, 1)
        else:
            object.Defences = []
        robotic_peripherals(object, 2)

        specs.append("Can fabricate simple things.")
        specs.append("Cannot fabricate complex TOYS.")
        if intel >= 22:
            specs.append("Can design simple things.")
        specs.append("Programmable by a mechanic.")
        specs.append("DD of programming increases with value.")
        specs.append(f"Raw materials for {con} months.")
        object.Spec_Sheet = specs

    elif chosen == "Lifting":
        object.FAMILY_SUB = "Lifting"
        specs.append("Putting everything in it's place.")
        object.Adapt = 5
        object.Value = 30000
        object.HPM = please.roll_this("1d4+8") * con
        object.Size = "Outdoor"
        robot_size_wate_hite(object)
        # robot_offensive_systems check
        if please.do_1d100_check(35):
            robot_offensive_systems(object, 2)
        else:
            object.Robot_Attacks = []
        # robot_defensive_systems check
        if please.do_1d100_check(16):
            robot_defensive_systems(object, 1)
        else:
            object.Defences = []
        robotic_peripherals(object, 1)

        specs.append("Disemployed cargo hoists.")
        arms = math.ceil(dex / 3)
        specs.append(f"Has {arms} lifting articulations.")
        lift = wa * 3
        rise = object.PSTR_Prime + object.DEX_Prime
        specs.append(f"Can lift {lift} kgs up to {rise} hexes.")
        specs.append(f"Must roll vs CF ({cf}%) to drop things.")
        object.Spec_Sheet = specs

    elif chosen == "Moving":
        object.FAMILY_SUB = "Moving"
        specs.append("Sentient delivery bots.")
        object.Adapt = 5
        object.Value = 20000
        object.HPM = please.roll_this("1d4+8") * con
        object.Size = "Outdoor"
        robot_size_wate_hite(object)
        # robot_offensive_systems check
        if please.do_1d100_check(35):
            robot_offensive_systems(object, 2)
        else:
            object.Robot_Attacks = []
        # robot_defensive_systems check
        if please.do_1d100_check(15):
            robot_defensive_systems(object, 1)
        else:
            object.Defences = []
        robotic_peripherals(object, 1)

        object.Move = math.ceil(move * 1.5)
        specs.append(f"Increased move to {object.Move} h/u.")
        lift = wa * 3
        specs.append(f"Can deliver {lift} kgs at {object.Move} h/u.")
        specs.append(f"Deliver range is {awe * 100} kilometers.")
        specs.append("Can read maps.")
        loading = ((intel + dex) * 3) >= please.roll_this("1d100")
        if loading:
            specs.append("This bot is self loading (not loathing).")
        object.Spec_Sheet = specs

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
        object.Size = "Outdoor"
        robot_size_wate_hite(object)
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
        object.Size = "Outdoor"
        robot_size_wate_hite(object)
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
    object.Size = "Indoor"
    robot_size_wate_hite(object)
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
        object.Size = "Outdoor"
        robot_size_wate_hite(object)
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
        object.Size = "Outdoor"
        robot_size_wate_hite(object)
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
        object.Size = "Indoor"
        robot_size_wate_hite(object)
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
        object.Size = "Outdoor"
        robot_size_wate_hite(object)
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
        object.Size = "Outdoor"
        robot_size_wate_hite(object)
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
    # ob__ject.Anthro_Type = basefamily
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
        object.Size = "Indoor"
        robot_size_wate_hite(object)
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
        object.Size = "Indoor"
        robot_size_wate_hite(object)
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
        object.Size = "Indoor"
        robot_size_wate_hite(object)
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
        object.Size = "Outdoor"
        robot_size_wate_hite(object)
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

def fresh_robot():
    """
    builds A FRESH robot persona using EXP persona creation
    """
    # todo robot is a class or a function 

    # clearance for Clarence
    please.clear_console()
    print("\nYou are generating a fresh ROBOT PERSONA")

    fresh = table.PersonaRecord()
    fresh.FAMILY = "Robot"
    fresh.FAMILY_TYPE = "Unknown_Type"
    fresh.FAMILY_SUB = "Unknown_Sub"
    fresh.Vocation = "Robot"
    fresh.Robot_Model = "Robot"


    ### get mundane terran name of the player
    fresh.Player_Name = input("\nPlease input your MUNDANE TERRAN NAME: ")

    core.initial_attributes(fresh)
    robot_fabricator_family(fresh)
    control_factor(fresh)
    core.movement_rate(fresh)
    core.wate_allowance(fresh)
    robotic_power_source(fresh)
    robotic_sensors(fresh)
    core.base_armour_rating(fresh)

    # temporary until we have a proper robot persona
    fresh.Bot_Type = secrets.choice(["Android", "Combot", "Datalyzer"])
    robot_type_function_pivot[fresh.Bot_Type](fresh)
    # fresh_robot_type(fresh)


    # robot HPM based on CON and type
    # string value per robot multiplied by CON
    # present structure of robots as functions does not allow for values just yet
    # the HPM is calculated and assigned by the function 

    # offensive systems is called by robot type
    # defensive systems is called by robot type
    # peripherals is called by robot type

    ### require bot_type
    robotic_locomotion(fresh)
    robot_size_wate_hite(fresh)
    robot_description(fresh)

    if fresh.Vocation != "Robot":
        vocation.set_up_first_time(fresh)

    outputs.robot_review(fresh)
    robot_persona_name(fresh)
    outputs.robot_review(fresh)
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