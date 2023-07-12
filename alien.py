import math
import re

import please
import table
import anthro
import vocation
import mutations
import outputs
import core

def alien_workflow() -> None:
    """
    player alien versus referee person vs persona maintenance
    """
    please.clear_console()
    option_function_map = {
        "Fresh Alien (New Player)":fresh_alien, 
        "Bespoke Alien":bespoke_alien, 
        "Random Alien":rando_alien, 
        "Maintenance":please.do_referee_maintenance
    }

    option_list = list(option_function_map.keys())
    list_comment = "Choose an alien workflow:"
    plan_desired = please.choose_this(option_list, list_comment)

    if plan_desired in option_function_map:
        option_function_map[plan_desired]()

####################################
# FRESH ALIEN FUNCTIONS
####################################

def alien_size_fresh(object):

    size, kgs_roll = please.get_table_result(table.alien_sizes)

    object.Size = size
    object.Wate = please.roll_this(kgs_roll)
    object.Wate_Suffix = "kgs"

    """  if size == "Tiny":
        object.Size = size
        object.Wate = please.roll_this("1d10")

    elif size == "Small":
        object.Size = size
        object.Wate = please.roll_this("1d50")

    elif size == "Medium":
        object.Size = size
        object.Wate = please.roll_this("1d50+50")

    elif size == "Large":
        object.Size = size
        object.Wate = please.roll_this("5d100+100")

    elif size == "Gigantic":
        object.Size = size
        object.Wate = please.roll_this("6d1000+600") """

    return

def alien_attacks_per_unit(object):

    attacks = please.get_table_result(table.attacks_per_unit)

    if attacks == 0:
        object.Attacks = 1
        object.Attack_Desc = "per 2 units"
    else:
        object.Attacks = attacks
        object.Attack_Desc = "per unit"

    return


def alien_damage_per_attack(object: dict) -> None:
    """
    damage per attack depends on Size and PSTR
    """

    pstr = object.PSTR
    size = object.Size

    for pstr_range in table.alien_attack_damage:
        if pstr in pstr_range:
            object.Damage = f"{table.alien_attack_damage[pstr_range][size]}"
            break

    return


def alien_attack_type_fresh(object):
    object.Attack_Type = please.get_table_result(table.alien_attack_type)


def alien_shape_fresh(object):

    four_quarter_parts = ["Head", "Body", "Arms", "Legs"]

    for key in four_quarter_parts:
        die_roll = please.roll_this("1d149-1")
        body_part = table.alien_quarter_shapes[die_roll]
        setattr(object, key, body_part)

    return


def adornalizer(part, adornment):
    """
    Returns a descriptive adornment sentence
    """
    if part == "Nil (s)":
        return " "

    # random descriptors
    sizes = ["small", "", "large", "", "tiny", ""]
    amounts = ["one", "one", "two", "many", "several", "many"]
    connectors = [
        "adorned with",
        "sporting",
        "adorned with",
        "connected to",
        "adorned with",
        "sporting",
    ]

    size = sizes[please.roll_this("1d6-1")]
    amount = amounts[please.roll_this("1d6-1")]
    connector = connectors[please.roll_this("1d6-1")]

    adorning = f" {connector} {amount} {size} {adornment}"

    if amount != "one":
        adorning = adorning + "s"

    if part == "Arms":
        adorning = f" with {size} {adornment}s"

    return adorning


def alien_adornments_fresh(object):
    quarter_part_pivot = {
        "Head": table.alien_head_adornments,
        "Body": table.alien_body_adornments,
        "Arms": table.alien_arm_adornments,
    }

    for part, adorn_table in quarter_part_pivot.items():
        if getattr(object, part) == "Nil (s)":
            adorntribute = f"{part}_Adorn"
            setattr(object, adorntribute, " ")
            continue

        if please.say_yes_to(
            f"Do you want to ADORN the alien's {part.upper()} ({getattr(object, part).split(' (')[0]})?"
        ):
            adornment = please.get_table_result(adorn_table)

            # if adornment is a Arms adornment then replace with arms adornment
            if adornment == "Arms Adornment":
                adornment = please.get_table_result(table.alien_arm_adornments)

            # if adornment is a head adornment then replace with head adornment
            if adornment == "Head Adornment":
                adornment = please.get_table_result(table.alien_head_adornments)

            adornment = adornalizer(part, adornment)
            adorntribute = f"{part}_Adorn"

            setattr(object, adorntribute, adornment)

        else:
            adorntribute = f"{part}_Adorn"
            setattr(object, adorntribute, " ")

        adornment = please.get_table_result(adorn_table)

    return


# todo move terrain movements to calculated in outputs, and not stored

def assign_terrain_movements(moving_time: table.PersonaRecord) -> table.PersonaRecord:
    '''assigns alien movements (head, body, arms, legs) -> land, air, water (l,a,w)'''

    four_quarter_parts = ["Head", "Body", "Arms", "Legs"]
    movements = []
    ### build a list of combined terrain types (l, a, w, s, s-w)
    for part in four_quarter_parts:
        body_part = getattr(moving_time, part)
        terrains = re.search('\((.*?)\)', body_part).group(1) # regex capture of string inside the brackets

        if "," in terrains:
            multiple_terrains = terrains.split(",")
            movements.extend(multiple_terrains)
        else:
            movements.append(terrains)

    moving_time.Move_Land = math.ceil(moving_time.DEX * (movements.count("l") / 4))
    moving_time.Move_Air = math.ceil(moving_time.DEX * (movements.count("a") / 4))
    moving_time.Move_Water = math.ceil(moving_time.DEX * (movements.count("w") / 4))

    return moving_time # is altered by side effect


def alien_quick_description_builder(object):
    head = object.Head
    body = object.Body
    head = head.split("(")[0].strip()
    body = body.split("(")[0].strip()

    sentences = {
        (True, False, False): "flies.",
        (False, True, False): "swims.",
        (False, False, True): "runs.",
        (True, True, False): "flies and swims.",
        (True, False, True): "flies and runs.",
        (False, True, True): "swims and runs.",
        (True, True, True): "flies, swims, and runs.",
        (False, False, False): "is sessile.",
    }

    description = "A "

    if object.Size == "Medium":
        description += "Medium sized "
    else:
        description += object.Size + " "

    if head == "Nil":
        description += "headless "
    else:
        description += head + " headed "

    if body == "Nil":
        description += "bodyless thing"
    else:
        description += body

    description += " that "

    mobility = []

    # check Air
    if object.Move_Air > 0:
        mobility.append(True)
    else:
        mobility.append(False)

    # check Water
    if object.Move_Water > 0:
        mobility.append(True)
    else:
        mobility.append(False)

    # check Land
    if object.Move_Land > 0:
        mobility.append(True)
    else:
        mobility.append(False)

    # print(mobility)
    combo = tuple(mobility)
    description += sentences[combo]

    setattr(object, "Quick_Description", description)

    return


def alien_natural_powers_fresh(object):
    mentchance = object.MSTR
    physchance = object.CON
    object.Mutations = {}

    ### build the number of mental powers
    mutation_number = 0
    while please.do_1d100_check(mentchance):
        mutation_number += 1

    fresh_amount = 0
    while fresh_amount < mutation_number and mutation_number > 0:
        working_mutation = please.get_table_result(mutations.mental_mutation_random)[1](
            object
        )
        print(working_mutation)
        fresh_amount += 1

        if working_mutation.kind == "defect":
            if please.say_yes_to("Does a DEFECT get an extra roll? "):
                fresh_amount -= 1

    ### build the number of physical powers
    mutation_number = 0
    while please.do_1d100_check(physchance):
        mutation_number += 1

    fresh_amount = 0
    # number of mutations is random based on anthro type
    while fresh_amount < mutation_number and mutation_number > 0:
        working_mutation = please.get_table_result(mutations.physical_mutation_random)[1](
            object
        )
        print(working_mutation)
        fresh_amount += 1

        if working_mutation.kind == "defect" and object.FAMILY_TYPE!= "Purestrain":
            if please.say_yes_to("Does a DEFECT get an extra roll? "):
                fresh_amount -= 1

    return


def alien_life_span_fresh(object):

    ### collect all the data
    span_data = please.get_table_result(table.alien_life_span_data)
    base = span_data["base"]
    die_roll = span_data["die_roll"]
    multi = span_data["multiplier"]
    years = "years"

    ### calculate total life span
    life_span = base + please.roll_this(die_roll) * multi
    setattr(object, "Life_Span", [0, life_span])

    ### calculate portion of life span in each stage
    child = life_span * (please.roll_this(table.alien_life_stages["Child"]) / 100)
    adol = life_span * (please.roll_this(table.alien_life_stages["Adolescent"]) / 100)
    adult = life_span * (please.roll_this(table.alien_life_stages["Adult"]) / 100)
    aged = life_span * (please.roll_this(table.alien_life_stages["Aged"]) / 100)

    ### if life span is short switch to months
    if life_span < 6:
        life_span = life_span * 12
        years = "months"

    ### build life cycle list
    life_cycle = []

    life_cycle.append(
        f"Life Span : 0 to {str(life_span)} {years}."
    )
    life_cycle.append(
        f"Child: 0 to {child:.2f}; Adol: {child:.2f} to {(child + adol):.2f}"
    )
    life_cycle.append(f"Adult: {(child + adol):.2f} to {(child + adol + adult):.2f}")
    life_cycle.append(
        f"Old: {(child + adol + adult):.2f} to {(life_span - aged):.2f}; Aged: {(life_span - aged):.2f} to {life_span}"
    )

    object.Life_Cycle = life_cycle

    ### data for future calc of alien age if needed
    object.Age_Adolescent = child + adol
    object.Alien_Age_Suffix = years

    return


def alien_age_fresh(object):
    ### assign proposed age to alien age
    base_age = object.Age_Adolescent
    start_range = please.roll_this("1d50") - 26  # -26 generates -25 to 24 modifier
    age = base_age * (1 + (start_range / 100))
    object.Age = round(age, 1)

    return


def alien_voice() -> str:
    """
    returns a random alien noise
    """
    sound_one = please.get_table_result(table.alien_sounds)
    sound_two = please.get_table_result(table.alien_sounds)
    while sound_one == sound_two:
        sound_two = please.get_table_result(table.alien_sounds)

    return f"{sound_one}s and {sound_two}s"


def alien_biology(object):

    alien_biology = []

    ### alien natural biome
    biome = please.get_table_result(table.biome_base_list)
    character = please.get_table_result(table.biome_sub_list)
    alien_biology.append(f"Biome: {character} {biome}.")

    ### alien energy source and procurement
    source = please.get_table_result(table.alien_biology_energy_source)
    procure = please.get_table_result(table.alien_biology_energy_procurement)
    alien_biology.append(f"Energy: {source} by {procure}.")

    ### alien reproduction
    repro = please.get_table_result(table.alien_biology_reproduction)
    alien_biology.append(f"Reproduction: {repro}.")

    ### alien domicile and aroma
    home = please.get_table_result(table.alien_biology_domicile)
    smell = please.get_table_result(table.alien_biology_aroma)
    alien_biology.append(f"Domicile: {home} Smell: {smell}.")

    ### alien grouping size
    grouping = please.get_table_result(table.alien_biology_group_size)
    alien_biology.append(f"Group Size: {grouping}.")

    ### alien sounds
    sounds = alien_voice()
    object.Sounds = sounds

    object.Biology = alien_biology

    return


def alien_society_fresh(object):
    awe = object.AWE
    cha = object.CHA
    dex = object.DEX
    intel = object.INT
    mstr = object.MSTR

    tool_score = 0
    language = culture = education = vocay = vocay_path = False
    religion = politics = philosophy = False

    alien_tool_score = ["None", "Simple", "Tech", "Computer", "Creator"]

    #########################################
    # set up boolean flags for each society
    # calculate tool score
    #########################################

    ### Language Check
    if please.do_1d100_check(intel * 3):
        language = True

    ### initial tool check
    if please.do_1d100_check(dex * 2):
        tool_score += 1

    ### Culture Check
    if language and please.do_1d100_check(cha * 3):  # check culture
        culture = True
        if please.do_1d100_check(intel * 2):  # check tool score if culture is true
            tool_score += 1

        ### religion check
        chance = 2 * intel - mstr
        chance = chance if chance > 0 else 0  # ternary vs -ve chance
        if please.do_1d100_check(chance):
            religion = True
    else:
        if please.do_1d100_check(intel * 2):  # check tool score if culture is false
            tool_score += 1

    ### Education Check
    if culture and please.do_1d100_check(awe * 3):  # check education
        education = True
        if please.do_1d100_check(intel * 2):  # check tool score if education is true
            tool_score += 1

        ### politics check
        if please.do_1d100_check(intel + cha):
            politics = True

    else:
        if please.do_1d100_check(intel * 2):  # check tool score if education is true
            tool_score += 1

    ### Vocation Check
    if education and please.do_1d100_check(awe + dex + intel):  # check vocation
        vocay = True
        if please.do_1d100_check(intel * 2):  # check tool score if vocation is true
            tool_score += 1

        # vocay_path check
        if please.do_1d100_check(intel + awe + dex):
            vocay_path = True

        # philosophy check
        if please.do_1d100_check(intel + awe):
            philosophy = True

    else:
        if please.do_1d100_check(intel * 2):  # check tool score if vocation is false
            tool_score += 1

    ######################################################
    # build alien society list
    ######################################################

    alien_society = []

    ### add in tool usage
    alien_society.append(
        f"Tool Usage: {alien_tool_score[tool_score]} ({tool_score}/4)."
    )

    ### add in language
    if language:
        alien_society.append(f"Species has a LANGUAGE made up of: {object.Sounds}.")
    else:
        alien_society.append("Species has NO language.")

        ### flora or fauna check
        if tool_score == 0 and not language:
            alien_society.append(f"Species is FLORA OR FAUNA.")

    ### add in culture
    if culture:
        if religion:
            religiousism = please.get_table_result(table.role_play_RP_religion)
            alien_society.append(f"Species has CULTURE and religion ({religiousism}).")
        else:
            alien_society.append(f"Species has CULTURE and no religion.")

    if education:
        if politics:
            politicism = please.get_table_result(table.role_play_RP_politics)
            alien_society.append(f"Species has EDUCATION and politics ({politicism}).")
        else:
            alien_society.append(f"Species has EDUCATION and no politics.")

    if vocay:
        if philosophy:
            philosophism = please.get_table_result(table.role_play_RP_philosophy)
            alien_society.append(
                f"Species has VOCATIONS and philosophy ({philosophism})."
            )
        else:
            alien_society.append(f"Species has VOCATIONS and no philosophy.")
        setattr(object, "Vocation", "Yes")
    else:
        setattr(object, "Vocation", "None")

    ### populate the object as needed.
    setattr(object, "Tool_Use", alien_tool_score[tool_score])
    setattr(object, "Tool_Score", tool_score)
    setattr(object, "Society", alien_society)

    return


def alien_vocation_check(object):
    tools = object.Tool_Use
    vocation = object.Vocation

    if vocation == "None":
        object.Vocation = "Alien"
        return

    if please.say_yes_to("Would your alien like to pursue a VOCATION?"):
        ### choose vocation type
        choices = vocation.list_eligible_vocations(object)
        choice_comment = "Which VOCATION do you want?"
        type_choice = please.choose_this(choices, choice_comment)
        object.Vocation = type_choice
        vocation.set_up_first_time(object)
    else:
        object.Vocation = "Alien"

    return


def alien_nomenclature(object):
    print(
        "\nPlease carefully consider a SPECIES NAME for your alien persona.\n"
        "This is NOT your alien persona name (which follows).\n"
    )

    alien_species = input("What is the name of your entire ALIEN SPECIES? ")
    if alien_species == "quit" or alien_species == "Quit":
        if please.say_yes_to("Do you want to QUIT the program"):
            print("\n*** program terminated")
            exit()
    object.FAMILY_TYPE = alien_species

    core.assign_persona_name

    return

####################################
# BESPOKE ALIEN FUNCTIONS
####################################

def alien_size_bespoke(object: dict) -> None:
    """
    generate alien size including minute and humongous
    """

    methods = ["Random", "Bespoke"]
    choice_comment = "Choose a method for alien SIZE?"
    choice = please.choose_this(methods, choice_comment)

    if choice == "Random":
        alien_size_fresh(object)

        if object.Size == "Tiny" and please.do_1d100_check(16):
            object.Size = "Minute"

        elif object.Size == "Gigantic" and please.do_1d100_check(16):
            object.Size = "Humongous"

    elif choice == "Bespoke":
        size_choices = [sizes for sizes in table.alien_size_and_WA.keys()]
        object.Size = please.choose_this(size_choices, "Choose a SIZE for your alien.")

    # assign wate based on size
    sizes_split = please.list_table_choices(table.alien_sizes)
    for size, kgs_roll in sizes_split:
        if size == object.Size:
            object.Wate = please.roll_this(kgs_roll)
            object.Wate_Suffix = "kgs"

    if object.Size == "Minute":
        object.Wate = please.roll_this("1d1000")
        object.Wate_Suffix = "gms"
        new_pstr = math.ceil(object.PSTR * (object.Wate / 1000))
        setattr(object, "PSTR", new_pstr)
        # Must fix the HPM later.

    if object.Size == "Humongous":
        object.Wate = please.roll_this("1d50") * 6
        object.Wate_Suffix = "Tonnes"

    return


def alien_attributes_bespoke(object: dict) -> None:
    """
    determine attributes
    """

    methods = ["Random", "Bespoke", "Descriptive"]
    choice_comment = "Choose a method for alien ATTRIBUTES?"
    choice = please.choose_this(methods, choice_comment)

    if choice == "Bespoke":
        core.initial_attributes(object)
        anthro.bespoke_anthro_attribute_ranges(object)

    elif choice == "Random":
        core.initial_attributes(object)

    elif choice == "Descriptive":
        core.initial_attributes(object)
        anthro.core.descriptive_attributes(object)

    else:
        print("error in bespoke_anthro_attribute methods")

    return


def alien_attacks_bespoke(object: dict) -> None:
    """
    alien attack type and frequency
    """
    methods = ["Random", "Bespoke"]
    choice_comment = "Choose a method for alien ATTACKS?"
    choice = please.choose_this(methods, choice_comment)

    if choice == "Random":
        alien_attacks_per_unit(object)
        alien_attack_type_fresh(object)

    elif choice == "Bespoke":
        print(f"This alien inflicts {object.Damage} HPS per attack")
        attacks = int(input("How many ATTACKS PER UNIT? "))
        if attacks == 0:
            object.Attacks = 1
            object.Attack_Desc = "per 2 units"
        else:
            object.Attacks = attacks
            object.Attack_Desc = "per unit"

        choices = [
            val
            for val in table.alien_attack_type.values()
            if val != "Alien Attack" and val != "1d100"
        ]
        object.Attack_Type = please.choose_this(choices, "Choose an ATTACK TYPE.")


def alien_natural_powers_bespoke(object: dict) -> None:
    """
    determine natural powers (mutations) for bespoke aliens
    """

    ### determine RP anthro mutations
    choices = ["Attribute Determined", "Bespoke", "Random"]
    choice_comment = "What selection method do you want for MUTATIONS?"
    method_type_selection = please.choose_this(choices, choice_comment)

    if method_type_selection == "Attribute Determined":
        alien_natural_powers_fresh(object)

    elif method_type_selection == "Bespoke":
        mutations.pick_bespoke_mutation(object)

    elif method_type_selection == "Random":
        mutations.single_random_mutation(object)

    return


def alien_life_span_bespoke(object: dict) -> None:
    """
    determine alien life span
    """

    methods = ["Random", "Bespoke"]
    choice = please.choose_this(methods, "Choose a method for alien LIFE SPAN?")

    if choice == "Random":
        alien_life_span_fresh(object)

    elif choice == "Bespoke":
        life_span_choices = [key for key in table.alien_life_span_descriptors.keys()]
        choice = please.choose_this(life_span_choices, "Choose a LIFE SPAN DESCRIPTOR.")
        span_data = table.alien_life_span_descriptors[choice]

        ### collect all the data
        base = span_data["base"]
        die_roll = span_data["die_roll"]
        multi = span_data["multiplier"]
        years = "years"

        ### calculate total life span
        life_span = base + please.roll_this(die_roll) * multi
        setattr(object, "Life_Span", [0, life_span])

        ### calculate portion of life span in each stage
        child = life_span * (please.roll_this(table.alien_life_stages["Child"]) / 100)
        adol = life_span * (
            please.roll_this(table.alien_life_stages["Adolescent"]) / 100
        )
        adult = life_span * (please.roll_this(table.alien_life_stages["Adult"]) / 100)
        aged = life_span * (please.roll_this(table.alien_life_stages["Aged"]) / 100)

        ### if life span is short switch to months
        if life_span < 6:
            life_span = life_span * 12
            years = "months"

        ### build life cycle list
        life_cycle = []

        life_cycle.append(
            f"Life Span : 0 to {str(life_span)} {years} Life stages are in {years}"
        )
        life_cycle.append(
            f"Child: 0 to {child:.2f}; Adol: {child:.2f} to {(child + adol):.2f}"
        )
        life_cycle.append(
            f"Adult: {(child + adol):.2f} to {(child + adol + adult):.2f}"
        )
        life_cycle.append(
            f"Old: {(child + adol + adult):.2f} to {(life_span - aged):.2f}; Aged: {(life_span - aged):.2f} to {life_span}"
        )

        object.Life_Cycle = life_cycle

        ### data for future calc of alien age if needed
        object.Age_Adolescent = child + adol
        object.Alien_Age_Suffix = years

        return


def alien_biology_bespoke(object: dict) -> None:
    """
    referee can adjust alien biology for bespoke aliens
    """

    alien_biology = []

    ### preload the alien biology options with the defaults
    biome = please.get_table_result(table.biome_base_list)
    biome_character = please.get_table_result(table.biome_sub_list)
    source = please.get_table_result(table.alien_biology_energy_source)
    procure = please.get_table_result(table.alien_biology_energy_procurement)
    repro = please.get_table_result(table.alien_biology_reproduction)
    home = please.get_table_result(table.alien_biology_domicile)
    aroma = please.get_table_result(table.alien_biology_aroma)
    grouping = please.get_table_result(table.alien_biology_group_size)
    sounds = alien_voice()
    object.Sounds = sounds

    print("\nThe following questions are for the alien's BIOLOGY.")

    ### alien natural biome and characteristic
    if not please.say_yes_to(f"Do you want the existing BIOME: {biome} "):
        biome = please.bespokify_this_table(table.biome_base_list)

    if not please.say_yes_to(
        f"Do you want the existing BIOME CHARACTER: {biome_character}"
    ):
        biome_character = please.bespokify_this_table(table.biome_sub_list)

    ### alien energy source and procurement
    if not please.say_yes_to(f"Do you want the existing ENERGY SOURCE: {source}"):
        source = please.bespokify_this_table(table.alien_biology_energy_source)

    if not please.say_yes_to(
        f"Do you want the existing energy PROCUREMENT type: {procure}"
    ):
        procure = please.bespokify_this_table(table.alien_biology_energy_procurement)

    ### alien reproduction
    if not please.say_yes_to(f"Do you want the existing REPRODUCTION: {repro}"):
        repro = please.bespokify_this_table(table.alien_biology_reproduction)

    ### alien domicile and aroma
    if not please.say_yes_to(f"Do you want the existing DOMICILE: {home}"):
        home = please.bespokify_this_table(table.alien_biology_domicile)

    ### alien aroma
    if not please.say_yes_to(f"Do you want the existing AROMA: {aroma}"):
        aroma = please.bespokify_this_table(table.alien_biology_aroma)

    ### alien noises
    if not please.say_yes_to(f"Do you want the existing NOISES: {sounds}"):
        sounds = please.bespokify_this_table(table.alien_sounds)
        object.Sounds = sounds

    ### alien grouping size
    if not please.say_yes_to(f"Do you want the existing GROUP SIZE: {grouping}"):
        grouping = please.bespokify_this_table(table.alien_biology_group_size)

    ### assign the alien biology to the alien object
    alien_biology.append(f"Biome: {biome_character} {biome}.")
    alien_biology.append(f"Energy Source: {source} Procurement: {procure}.")
    alien_biology.append(f"Reproduction: {repro}.")
    alien_biology.append(f"Domicile: {home} Smell: {aroma}.")
    alien_biology.append(f"Group Size: {grouping}. Group Sound: {sounds}.")

    object.Biology = alien_biology

    return


def alien_society_bespoke(object: dict) -> None:
    """
    first generates a society for the alien
    Second allow player to modify the society
    """

    awe = object.AWE
    cha = object.CHA
    dex = object.DEX
    intel = object.INT
    mstr = object.MSTR

    tool_score = 0
    language = culture = education = vocay = vocay_path = False
    religion = politics = philosophy = False

    alien_tool_score = ["None", "Simple", "Tech", "Computer", "Creator"]

    #########################################
    # set up boolean flags for each society
    # calculate tool score
    #########################################

    # this could be a separate function but I am too lazy

    ### Language Check
    if please.do_1d100_check(intel * 3):
        language = True

    ### initial tool check
    if please.do_1d100_check(dex * 2):
        tool_score += 1

    ### Culture Check
    if language and please.do_1d100_check(cha * 3):  # check culture
        culture = True
        if please.do_1d100_check(intel * 2):  # check tool score if culture is true
            tool_score += 1

        ### religion check
        chance = 2 * intel - mstr
        chance = chance if chance > 0 else 0  # ternary vs -ve chance
        if please.do_1d100_check(chance):
            religion = True
    else:
        if please.do_1d100_check(intel * 2):  # check tool score if culture is false
            tool_score += 1

    ### Education Check
    if culture and please.do_1d100_check(awe * 3):  # check education
        education = True
        if please.do_1d100_check(intel * 2):  # check tool score if education is true
            tool_score += 1

        ### politics check
        if please.do_1d100_check(intel + cha):
            politics = True

    else:
        if please.do_1d100_check(intel * 2):  # check tool score if education is true
            tool_score += 1

    ### Vocation Check
    if education and please.do_1d100_check(awe + dex + intel):  # check vocation
        vocay = True
        if please.do_1d100_check(intel * 2):  # check tool score if vocation is true
            tool_score += 1

        # vocay_path check
        if please.do_1d100_check(intel + awe + dex):
            vocay_path = True

        # philosophy check
        if please.do_1d100_check(intel + awe):
            philosophy = True

    else:
        if please.do_1d100_check(intel * 2):  # check tool score if vocation is false
            tool_score += 1

    #########################################
    # RP Fun the alien society
    #########################################

    print("\nThe following questions are for the alien's SOCIETY")

    ### build the alien society list for the referee persona
    alien_society = []

    ### Choose  tool usage
    print(f"Proposed tool usage is {alien_tool_score[tool_score]}")
    if please.say_yes_to(
        f"Are you okay with an alien tool usage of: {alien_tool_score[tool_score]} aka ({tool_score}/4)?"
    ):
        alien_society.append(
            f"Tool Usage: {alien_tool_score[tool_score]} ({tool_score}/4)."
        )
    else:
        tool_score = alien_tool_score.index(
            please.bespokify_this_table(alien_tool_score)
        )
        alien_society.append(
            f"Tool Usage: {alien_tool_score[tool_score]} ({tool_score}/4)."
        )

    ### choose language
    print(f"Proposed language is {language}")
    if not please.say_yes_to(f"Are you okay with an alien language being: {language}?"):
        language = not language

    ### add in culture
    print(f"Proposed culture is {culture}")
    if not please.say_yes_to(f"Are you okay with an alien culture being: {culture}?"):
        culture = not culture

    print(f"Proposed religion is {religion}")
    if not please.say_yes_to(f"Are you okay with an alien religion being: {religion}?"):
        religion = not religion

    if religion:
        religiousism = please.bespokify_this_table(table.role_play_RP_religion)
        language = True

    print(f"Proposed education is {education}")
    if not please.say_yes_to(
        f"Are you okay with an alien education being: {education}?"
    ):
        education = not education

    print(f"Proposed politics is {politics}")
    if not please.say_yes_to(f"Are you okay with an alien politics being: {politics}?"):
        politics = not politics

    if politics:
        politicism = please.bespokify_this_table(table.role_play_RP_politics)
        language = True

    print(f"Proposed vocation is {vocay}")
    if not please.say_yes_to(f"Are you okay with the alien vocation being: {vocay}?"):
        vocay = not vocay

    if vocay:
        anthro.anthro_vocation_bespoke(object)
        language = True
        culture = True
        education = True
    else:
        setattr(object, "Vocation", "Alien")

    print(f"Proposed philosophy is {philosophy}")
    if not please.say_yes_to(
        f"Are you okay with the alien philosophy being: {philosophy}?"
    ):
        philosophy = not philosophy

    if philosophy:
        philosophism = please.bespokify_this_table(table.role_play_RP_philosophy)

    ### populate the object as needed.

    #########################################
    # build the alien society list
    #########################################

    ### append the language
    if language:
        alien_society.append(f"Species has LANGUAGE. Made up of {object.Sounds}")
    else:
        alien_society.append("Species has NO language.")

    ### append if flora or fauna
    if tool_score == 0 and not language:
        alien_society.append(f"Species is FLORA OR FAUNA.")

    ### append the culture and religion
    if culture and religion:
        alien_society.append(f"Species has CULTURE and religion ({religiousism}).")
    elif culture and not religion:
        alien_society.append(f"Species has CULTURE and no religion.")
    elif not culture and religion:
        alien_society.append(
            f"Species has no CULTURE but has religion ({religiousism})."
        )

    if education and politics:
        alien_society.append(f"Species has EDUCATION and politics ({politicism}).")
    elif education and not politics:
        alien_society.append(f"Species has EDUCATION and no politics.")
    elif not education and politics:
        alien_society.append(
            f"Species has no EDUCATION but has politics ({politicism})."
        )

    if vocay and philosophy:
        alien_society.append(f"Species has VOCATIONS and philosophy ({philosophism}).")
    elif vocay and not philosophy:
        alien_society.append(f"Species has VOCATIONS and no philosophy.")

    elif not vocay and philosophy:
        alien_society.append(
            f"Species has no VOCATIONS but has philosophy ({philosophism})."
        )

    setattr(object, "Tool_Use", alien_tool_score[tool_score])
    setattr(object, "Tool_Score", tool_score)
    setattr(object, "Society", alien_society)
    return


#####################################
# build a FRESH alien persona
#####################################

def fresh_alien():
    """
    builds a fresh alien object as per EXP persona creation
    """

    # clearance for Clarence
    please.clear_console()
    print("\nYou are generating a FRESH ALIEN Persona")

    fresh = table.PersonaRecord()
    fresh.FAMILY = "Alien"
    fresh.Vocation = "Alien"
    fresh.FAMILY_TYPE = "unevolved"
    fresh.FAMILY_SUB = "undiscovered"
    fresh.Date_Created = "Start Evolving"
    fresh.RP = False

    ### get mundane player name
    fresh.Player_Name = input("\nPlease input your MUNDANE TERRAN NAME: ")

    core.initial_attributes(fresh)
    alien_size_fresh(fresh)
    core.wate_allowance(fresh)
    core.hit_points_max(fresh)
    alien_attacks_per_unit(fresh)
    alien_damage_per_attack(fresh)
    alien_attack_type_fresh(fresh)
    core.base_armour_rating(fresh)
    alien_shape_fresh(fresh)
    alien_adornments_fresh(fresh)
    core.movement_rate(fresh)
    alien_quick_description_builder(fresh)
    alien_natural_powers_fresh(fresh)
    alien_life_span_fresh(fresh)
    alien_age_fresh(fresh)
    alien_biology(fresh)
    alien_society_fresh(fresh)
    alien_vocation_check(fresh)
    outputs.outputs_workflow(fresh, "Screen")
    alien_nomenclature(fresh)
    please.assign_id_and_file_name(fresh)

    outputs.alien_review(fresh)
    please.record_storage(fresh)
    return

#####################################
# build a BESPOKE alien persona
#####################################

def bespoke_alien():
    """
    Build a bespoke alien persona usually a referee persona
    """
    
    # clearance for Clarence
    please.clear_console()
    print("\nYou are generating a BESPOKE ALIEN Persona")


    bespoke = table.PersonaRecord()
    bespoke.FAMILY = "Alien"
    bespoke.FAMILY_TYPE = "Undiscovered"
    bespoke.Persona_Name = "Nebulous"
    bespoke.Date_Created = "Still Evolving"
    bespoke.RP = True if please.say_yes_to("Is this a REFEREE persona? ") else False
    setattr(bespoke, "Level", 1)
    setattr(bespoke, "EXPS", 42)
    setattr(bespoke, "FAMILY", "Alien")
    setattr(bespoke, "Vocation", "Alien")

    ### get mundane player name
    bespoke.Player_Name = input("\nPlease input your MUNDANE TERRAN NAME: ")

    alien_attributes_bespoke(bespoke)
    alien_size_bespoke(bespoke)
    core.wate_allowance(bespoke)
    core.hit_points_max(bespoke)
    alien_damage_per_attack(bespoke)
    alien_attacks_bespoke(bespoke)
    core.base_armour_rating(bespoke)
    alien_shape_fresh(bespoke)
    alien_adornments_fresh(bespoke)
    core.movement_rate(bespoke)
    alien_quick_description_builder(bespoke)
    alien_natural_powers_bespoke(bespoke)
    alien_life_span_bespoke(bespoke)
    alien_age_fresh(bespoke)
    vocation.exps_level_picker(bespoke)
    bespoke.EXPS = vocation.convert_levels_to_exps(bespoke)
    alien_biology_bespoke(bespoke)
    alien_society_bespoke(bespoke)
    if bespoke.Vocation != "Alien":
        vocation.set_up_first_time(bespoke)
        if bespoke.Level > 1:
            vocation.update_interests(bespoke, (bespoke.Level - 1))
            vocation.update_skills(bespoke, (bespoke.Level - 1))
    outputs.alien_review(bespoke)
    alien_nomenclature(bespoke)
    please.assign_id_and_file_name(bespoke)
    outputs.alien_review(bespoke)
    please.record_storage(bespoke)
    return

#####################################
# build a RANDO alien persona
#####################################

def rando_alien():
    pass