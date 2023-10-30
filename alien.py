import math
from secrets import choice
from collections import Counter
from dataclasses import dataclass

import please
import table
import vocation
import mutations
import outputs
import core

# set up AlienRecord
@dataclass
class AlienRecord(exp_tables.Alienic):
    pass


def alien_workflow() -> None:
    """
    player alien versus referee person vs persona maintenance
    """
    please.clear_console()

    print('You are about to embark on an ALIEN Build')
    nom_de_bom = please.input_this("\nPlease input your MUNDANE TERRAN NAME: ")

    option_function_map = {
        "Fresh Alien (New Player)":lambda: fresh_alien(nom_de_bom), 
        "Bespoke Alien":lambda:bespoke_alien(nom_de_bom), 
        "Random Alien":lambda:rando_alien(nom_de_bom),
        "Maintenance":please.do_referee_maintenance
    }
    please.clear_console()
    option_list = list(option_function_map.keys())
    list_comment = "Choose an ALIEN workflow:"
    plan_desired = please.choose_this(option_list, list_comment)

    if plan_desired in option_function_map:
        option_function_map[plan_desired]()

####################################
# FRESH ALIEN FUNCTIONS
####################################

def alien_attack_number(attacker: AlienRecord) -> int:
    '''determine the number of alien attacks per unit'''

    if attacker.RP and not attacker.Fallthrough:
        if please.say_yes_to("Would you like to choose your own NUMBER of ATTACKS per unit? "):
            attack_no = int(please.input_this("How many ATTACKS PER UNIT? "))
            if attack_no > 5 and not please.say_no_to(f'{attack_no} per unit is hella lot of attack rolls. You sure? '):
                return alien_attack_number(attacker)
            else:
                return attack_no

    attack_no = please.get_table_result(exp_tables.attacks_per_unit)
    attacker.Alternating = True if attack_no == 0 else False
    attack_no = 1 if attack_no == 0 else attack_no    

    return attack_no

def alien_attack_types(attacktyper: AlienRecord, attack_no:int) -> AlienRecord:
    ''' assign strike, fling or shoot attack types in a list'''

    if attacktyper.RP and not attacktyper.Fallthrough:
        if please.say_yes_to("Would you like to choose your own ATTACK TYPES? "):
            print(f'The alien has {attack_no} attack(s) that need ATTACK TYPES.')
            for indxr in range(attack_no):
                attacktyper.Attacks.append(please.choose_this(["Strike", "Fling", "Shoot"], f"Choose ATTACK TYPE for attack #{indxr+1}. "))
            return attacktyper # modified by side effe

    for _ in range(attack_no):
        attacktyper.Attacks.append(f'{please.get_table_result(exp_tables.alien_attack_type)}')

    return 

def alien_damage_list(damaging: AlienRecord) -> list:
    """
    damage per attack depends on Size and PSTR
    """

    alien_size = damaging.Size_Cat
    pstr = damaging.PSTR
    damages = []
    ### pull the damage line for a alien PSTR
    for strange, damage_line in exp_tables.alien_attack_damage.items():
        if pstr >= strange[0] and pstr <= strange[1]:
            break

    ### build the damage list from smallest to biggest until match
    for size,dmg in damage_line.items():
        damages.append(dmg)
        if alien_size == size:
            break

    damages = damages[::-1] # this reverses the list
    while len(damages) < 3:
        damages.append(damages[-1])
    damages = damages[:3] 

    return damages

def alien_attack_description(descriptor: AlienRecord) -> list:
    '''
    build alien attack description in sentence form
    '''

    breadth = len(set(descriptor.Attacks))
    damages = alien_damage_list(descriptor)
    attacks_counted = Counter(descriptor.Attacks)
    attack_no = len(descriptor.Attacks)

    attack_desc = ""
    if breadth == 1:
        alternating = "alternating units." if descriptor.Alternating else "every unit."
        attack_type = descriptor.Attacks[0]
        attack_desc += f'{exp_tables.numbers_2_words[attack_no]} {attack_type} attack{"s" if attack_no > 1 else ""} ({damages[0]}) {alternating} '
       
    elif breadth > 1:
        for i, (attack_type, attack_no) in enumerate(attacks_counted.items()):
            attack_desc += f'{exp_tables.numbers_2_words[attack_no]} {attack_type} attack{"s" if attack_no > 1 else ""} ({damages[i]}), '
        attack_desc = attack_desc[:-2] + " every unit."

    attack_desc = attack_desc.capitalize()
    descriptor.Attack_Desc = attack_desc
    return attack_desc # also persona record altered by side effect

def alien_base_shape_random(shaping:AlienRecord) -> AlienRecord:
    ''' assigns a random animal shape to each body part '''
    four_quarter_parts = ["Head", "Body", "Arms", "Legs"]

    for part in four_quarter_parts:
        part_shape = choice(exp_tables.alien_quarter_shapes)
        setattr(shaping, part, part_shape)

    return shaping # adjusted by side effects in this function

def alien_base_shape_bespoke(shaping:AlienRecord) -> AlienRecord:
    ''' player assigned quarter shapes '''
    alien_base_shape_random(shaping)

    four_quarter_parts = ["Head", "Body", "Arms", "Legs"]

    for part in four_quarter_parts:
        quarter = getattr(shaping, part)
        if not please.say_yes_to(f'Proposed alien {part}: {quarter} '):
            new_quarter = please.choose_this(exp_tables.alien_quarter_shapes, f"Choose alien's {part.upper}: ")
            setattr(shaping, part, new_quarter)

def adornalizer(part:str, adornment:str) -> str:
    """
    Returns a descriptive adornment sentence
    """
    if part == "Nil (s)":
        return " "

    # random descriptors
    sizes = ["small", "", "large", "", "tiny", ""]
    amounts = ["one", "one", "two", "many", "several", "many", "a"]
    connectors = [
        "adorned with",
        "sporting",
        "adorned with",
        "connected to",
        "adorned with",
        "sporting",
        "supporting",
        "revealing",
    ]

    size = choice(sizes)
    amount = choice(amounts)
    connector = choice(connectors)

    adorning = f'{connector} {amount} {size}{" " if len(size) > 0 else ""}{adornment}{"s" if amount in ["two", "many", "several"] else ""}'

    if part == "Arms":
        adorning = f'with {size}{" " if len(size) > 0 else ""}{adornment}s'

    return adorning

def alien_shape_adornments(adornable:AlienRecord) -> AlienRecord:
    quarter_part_pivot = {
        "Head": exp_tables.alien_head_adornments,
        "Body": exp_tables.alien_body_adornments,
        "Arms": exp_tables.alien_arm_adornments,
    }

    ## fabricate the three adornments
    for part, adorn_table in quarter_part_pivot.items():
        body_part = getattr(adornable, part).split(' (')[0]

        if body_part == "Nil (s)":
            continue
        adornment = adornalizer(part, choice(adorn_table))
        setattr(adornable, f'{part}_Adorn', f'{adornment}' )

        if adornable.Fallthrough:
            drop = True if please.do_1d100_check(50) else False
        else:
            drop = False if please.say_yes_to(f'Would you like your {body_part} {part} {adornment.lower()}? ') else True

        if drop:
            setattr(adornable, f'{part}_Adorn', "" )
        
    return adornable # is altered by side effect

# todo move terrain movements to calculated in outputs, and not stored
def assign_terrain_movements(moving_time: AlienRecord) -> AlienRecord:
    '''assigns alien movements (head, body, arms, legs) -> land, air, water (l,a,w)'''
    four_quarter_parts = ["Head", "Body", "Arms", "Legs"]
    movements = []
    ### build a list of combined terrain types (l, a, w, s, s-w)
    for part in four_quarter_parts:
        terrains = getattr(moving_time, part).split(' (')[1][:-1]

        if "," in terrains:
            multiple_terrains = terrains.split(",")
            movements.extend(multiple_terrains)
        else:
            movements.append(terrains)

    moving_time.Move_Land = math.ceil(moving_time.DEX * (movements.count("l") / 4))
    moving_time.Move_Air = math.ceil(moving_time.DEX * (movements.count("a") / 4))
    moving_time.Move_Water = math.ceil(moving_time.DEX * (movements.count("w") / 4))

    return moving_time # is altered by side effect

def alien_quick_description_builder(describing: AlienRecord) -> AlienRecord:
    ''' make a little ditty describing the alien '''

    head = describing.Head.split("(")[0].strip()
    body = describing.Body.split("(")[0].strip()

    fly_swim_run = {
        (True, False, False): "flies",
        (False, True, False): "swims",
        (False, False, True): "runs",
        (True, True, False): "flies and swims",
        (True, False, True): "flies and runs",
        (False, True, True): "swims and runs",
        (True, True, True): "flies, swims, and runs",
        (False, False, False): "is sessile",
    }

    description = "A "
    description += "medium sized " if describing.Size_Cat == "Medium" else f'{describing.Size_Cat.lower()} '
    description += f'{head.lower()} headed ' if head != "Nil" else "headless "
    description += f'{body.lower()} that ' if body != "Nil" else "bodyless thing that "
   
    # build air water land  terrain moves tuple
    air = True if describing.Move_Air > 0 else False
    water = True if describing.Move_Water > 0 else False
    land = True if describing.Move_Land > 0 else False
    terrain_moves = (air, water, land)

    description += f'{fly_swim_run[terrain_moves]}.'

    describing.Quick_Description = description

    return description

def alien_life_stages(staging:AlienRecord, life_span:int = 42) -> dict:
    ''' creates a dict of the life stages for alien'''
    life_span = int(life_span)
    age_suffix = "years" if life_span > 6 else "months"
    life_span = life_span if life_span > 6 else life_span * 12

    ### calculate portion of life span in each stage
    # percent of age spent in each phase, times life_span = years spent in each stage
    child = life_span * (please.roll_this(exp_tables.alien_life_stages["Child"]) / 100)
    adol = life_span * (please.roll_this(exp_tables.alien_life_stages["Adolescent"])/ 100)
    adult = life_span * (please.roll_this(exp_tables.alien_life_stages["Adult"]) / 100)
    aged = life_span * (please.roll_this(exp_tables.alien_life_stages["Aged"]) / 100)

    ### build life cycle dict
    life_cycle ={}
    
    child = 1 if child<1 else child
    adol = 1 if adol<1 else adol

    life_cycle["Life Span"] = (0, life_span)
    life_cycle["Child"] = (0,child)
    life_cycle["Adol"] = (child + 1,child + adol)
    life_cycle["Adult"] = (child + adol + 1, child + adol + adult)
    life_cycle["Older"] = (child + adol + adult + 1, life_span - aged)
    life_cycle["Aged"] = (life_span - aged + 1,life_span)
    
    # clear the fucking float fuck 
    for key in life_cycle:
        tuple_ = life_cycle[key]
        lower, upper = tuple_    
        life_cycle[key] = (int(lower), int(upper))

    staging.Life_Stages = life_cycle
    staging.Age_Suffix = age_suffix

    return life_cycle # also aging modified by side effect

def alien_life_span() -> int:
    '''build the alien life pan dictionary'''
    die_roll, multi = please.get_table_result(exp_tables.alien_life_span_data)
    life_span = please.roll_this(die_roll) * multi

    return life_span # also aging modified by side effect

def alien_age(aging:AlienRecord, stage:str = "Adol") -> int:
    ''' alien age based on age category'''
    tuple_ = aging.Life_Stages[stage]
    age = choice(range(tuple_[0],tuple_[1]+1))

    return age

def alien_voice() -> str:
    """
    returns a random alien noise
    """
    sound_one = please.get_table_result(exp_tables.alien_sounds)
    sound_two = please.get_table_result(exp_tables.alien_sounds)
    while sound_one == sound_two:
        sound_two = please.get_table_result(exp_tables.alien_sounds)

    return f"{sound_one}s and {sound_two}s"

def alien_biology(biologically:AlienRecord) -> AlienRecord:
    ''' create list of biological info'''

    alien_biology = []
    for bio_name, bio_table in exp_tables.core_biology.items():
        alien_biology.append(f'{bio_name}: {please.get_table_result(bio_table)}')

    ### alien sounds
    sounds = alien_voice()
    alien_biology.append(f'Sounds: {sounds}.')
    biologically.Sounds = sounds

    biologically.Biology = alien_biology

    return biologically # altered by side effect

def alien_society(socialize: AlienRecord) -> AlienRecord:
    ''' set up a tool use, language, and society'''

    awe = socialize.AWE
    cha = socialize.CHA
    dex = socialize.DEX
    intel = socialize.INT
    mstr = socialize.MSTR

    tool_score = 0
    language = culture = education = vocay = vocay_path = False
    religion = politics = philosophy = False

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

    elif please.do_1d100_check(intel * 2):  # check tool score if culture is false
            tool_score += 1

    ### Education Check
    if culture and please.do_1d100_check(awe * 3):  # check education
        education = True
        if please.do_1d100_check(intel * 2):  # check tool score if education is true
            tool_score += 1

        ### politics check
        if please.do_1d100_check(intel + cha):
            politics = True

    elif please.do_1d100_check(intel * 2):  # check tool score if education is true
            tool_score += 1

    ### Vocation Check
    if education and please.do_1d100_check(awe + dex + intel):  # check vocation
        vocay = True
        alien_vocation_check(socialize)

        if please.do_1d100_check(intel * 2):  # check tool score if vocation is true
            tool_score += 1

        # philosophy check
        if please.do_1d100_check(intel + awe):
            philosophy = True

    elif please.do_1d100_check(intel * 2):  # check tool score if vocation is false
            tool_score += 1

    ######################################################
    # build alien society dict
    ######################################################

    society = {}
    society["Tools"] = "Flora or Fauna" if exp_tables.alien_tool_score[tool_score] == "None" and not language else exp_tables.alien_tool_score[tool_score]
    society["Language"] = "None" if not language else socialize.Sounds
    society["Culture"] = "None" if not culture else "Yes"
    society["Religion"] = "None" if not religion else please.get_table_result(exp_tables.role_play_RP_religion)
    society["Education"] = "None" if not education else "Yes"
    society["Politics"] = "None" if not politics else please.get_table_result(exp_tables.role_play_RP_politics)
    society["Vocation"] = "None" if not vocay else "Yes"
    society["Philosophy"] = "None" if not philosophy else please.get_table_result(exp_tables.role_play_RP_philosophy)
 
    socialize.Society = society

    return socialize # altered by side effects

def alien_society_bespoke(bespoken: AlienRecord) -> AlienRecord:
    """
    first generates a society for the alien
    Second allow player to modify the society
    """
    alien_society(bespoken)

    if bespoken.Fallthrough: return

    methods = ["Random", "Bespoke"]
    chosen = please.choose_this(methods, "Choose a method for alien SOCIETY? ")

    if chosen == 'Random': 
        return

    for soc_name, value in bespoken.Society.items():
        if please.say_yes_to(f'{soc_name} = {value}, Is this okay? '):
            continue
        else:
            if soc_name in ["Tools", "Language", "Culture", "Education", "Vocation"]:
                chosen = please.choose_this(exp_tables.core_society[soc_name], f'Choose a new value for {soc_name}')
                bespoken.Society[soc_name] = chosen

            elif soc_name in ["Philosophy", "Politics","Religion"]:
                choice_list = [val for key,val in exp_tables.core_society[soc_name].items() if key not in ["name", "die_roll"]]
                chosen = please.choose_this(choice_list, f'Choose a new value for {soc_name}')
                bespoken.Society[soc_name] = chosen

    return bespoken # altered here by side effect

def alien_vocation_check(get_a_job:AlienRecord) -> AlienRecord:
    '''assigns a vocation to an alien if appropriate'''

    if get_a_job.Vocation == "Alien": return

    if get_a_job.Fallthrough:    
        get_a_job.Vocation = choice([x for x in exp_tables.vocations_gifts_pivot])
        vocation.set_up_first_time(get_a_job)

    ### add additional interests and skills
        if get_a_job.Level > 1:
            get_a_job.Interests.extend(vocation.update_interests(get_a_job, (get_a_job.Level - 1)))
            get_a_job.Skills.extend(vocation.update_skills(get_a_job, (get_a_job.Level - 1)))

    if please.say_yes_to("Would your alien like to pursue a VOCATION?"):
        ### choose vocation type
        choices = vocation.attribute_determined(get_a_job)
        choice_comment = "Which VOCATION do you want?"
        type_choice = please.choose_this(choices, choice_comment)
        get_a_job.Vocation = type_choice
        vocation.set_up_first_time(get_a_job)
    else:
        get_a_job.Vocation = "Alien"

    return get_a_job # altered by side effect

def alien_speciesizer_list(naming: AlienRecord) -> list:
    ''' generate a faux latin list'''

    # todo nomenclature mutations  "Mutations": {"Wings": null}
    # todo nomenclature terrain types   "Move_Land": 8, "Move_Air": 4, "Move_Water": 4, 
    # todo nomenclature size "Size_Cat": "Medium",
    # todo nomenclature BIOLOGY "Life_Stages": {"Life Span": [0, 10],
    # todo nomenclature attacks "Attacks": ["Strike", "Strike", "Shoot"]
    # todo nomenclature "Biology": ["Biome: Tropic Grassland", "Biome Characteristic: Normal", "Energy Source: Carnivore", "Energy Procurement: Infesting", "Reproduction: Parasitic", "Domicile: Hollow", "Aroma: Lemons", "Group Size: Pack", "Sounds: Blubs and Clangs."],

    ### options based on quarter parts
    latini = []
    for part in ["Head", "Body", "Arms", "Legs"]:
        faux = getattr(naming, part).split(" (")[0]
        tableau = exp_tables.latinicize_shapes[faux]
        latini.append(choice(tableau))



    return latini

def alien_culturizer(naming: AlienRecord) -> list:
    if naming.Society["Language"] == "None":
        return
    # todo nomenclature alien culture names 
    # todo nomenclature SOCIETY
    # todo nomenclature  "Society": {"Tools": "None", "Language": "Blubs and Clangs", "Culture": "Yes", "Religion": "None", "Education": "None", "Politics": "None", "Vocation": "None", "Philosophy": "None"}, 

    return ["weedameeples"]

def alien_nomenclature(naming: AlienRecord) -> AlienRecord:
    '''FAMILY = Alien, FAMILY_TYPE = species name, FAMILY_SUB = cultural name, persona name'''
    please.clear_console()
    print(f'\n{naming.Player_Name} you are NAMING an ALIEN persona.')
    print(f'The ALIEN looks like: {naming.Quick_Description}')

    ### species name 
    print(f'This ALIEN needs a SPECIES name')
    latini = alien_speciesizer_list(naming)
    species = f'{choice(latini)} {choice(latini)}'

    while not please.say_yes_to(f'Do you like the species name {species}? '):
        species = f'{choice(latini)} {choice(latini)}'
    naming.FAMILY_SUB = species
    
    ### society name
    # todo society name for alien randomizer and parameters
    please.clear_console()
    print(f'This ALIEN needs a SOCIETY name')
    print(f'The ALIEN looks like: {naming.Quick_Description}\nSPECIES name:{naming.FAMILY_SUB}')
    print(f'Tool Usage: {naming.Society["Tools"]}, Language: {naming.Society["Language"]}')

    if naming.Society["Tools"] == "Flora or Fauna" or naming.Society["Language"] == "None":
        print(f'{naming.FAMILY_SUB} CANNOT name itself.')
        naming.FAMILY_TYPE = please.input_this("What is the species called? ")
    else:
        print(f'A language of {naming.Sounds.lower()}. ',end="")
        for element in ["Religion", "Politics", "Philosophy"]:
            if naming.Society[element] != "None":
                print(f'{element}: {naming.Society[element]}', end='')
        print(f'{naming.FAMILY_SUB} can name itself.')
        naming.FAMILY_TYPE = please.input_this("What is the SOCIETY name? ")

    ### persona name
    please.clear_console()
    print(f'This ALIEN needs a personal PERSONA name')
    print(f'The ALIEN looks like: {naming.Quick_Description}\nSPECIES name:{naming.FAMILY_SUB} ')
    naming.Persona_Name = please.input_this(f"\nPlease input the PERSONA NAME: ")

    # todo use alien_culturizer()

    return naming # modified by side effect

####################################
# BESPOKE ALIEN FUNCTIONS
####################################

def alien_hite_wate_calc(picking_sizes: AlienRecord) -> AlienRecord :
    ''' 
    return actual wate and wate_suffix based on size_cat
    '''
    picking_sizes.Wate = please.roll_this(exp_tables.alien_size_wate[picking_sizes.Size_Cat])
    
    if picking_sizes.Size_Cat == "Minute":
        picking_sizes.Wate_Suffix = "gms"
        picking_sizes.PSTR = math.ceil(picking_sizes.PSTR * (picking_sizes.Wate / 1000))
        picking_sizes.HPM = math.ceil(picking_sizes.HPM * (picking_sizes.Wate / 1000))

    if picking_sizes.Size_Cat == "Humongous":
        picking_sizes.Wate_Suffix = "Tonnes"   

    return picking_sizes # modified by side effects

def alien_size_cat_rando(sizer:AlienRecord) -> AlienRecord:
    ''' returns a size cat that includes Minute and Humongous'''
    sizer.Size_Cat = please.get_table_result(exp_tables.alien_size_fresh)
    sizer.Size_Cat = "Minute" if sizer.Size_Cat == "Tiny" and please.do_1d100_check(16) else "Tiny"
    sizer.Size_Cat = "Humongous" if sizer.Size_Cat == "Gigantic" and please.do_1d100_check(16) else "Gigantic"
    return # sizer is altered by side effect

def alien_size_cat_bespoke(sizer: AlienRecord) -> AlienRecord:  # side effects
    """
    generate alien size_cat including minute and humongous
    """
    if please.say_yes_to("Random alien SIZE? "):
        alien_size_cat_rando(sizer)
        return # sizer is altered by side effect
    else:
        methods = please.list_table_choices(exp_tables.alien_size_fresh) + ["Humongous", "Minute"]
        choice_comment = "Choose a SIZE for your alien."
        sizer.Size_Cat = please.choose_this(methods, choice_comment)
        return


def alien_attributes_bespoke(attributions: AlienRecord) -> AlienRecord:
    """
    determine alien attributes
    """
    core.initial_attributes(attributions)

    if attributions.Fallthrough:
        return attributions # altered by side effect

    methods = ["Random", "Descriptive", "Specific <- painful"]
    choice_comment = "Choose a method for alien ATTRIBUTES?"
    chosen = please.choose_this(methods, choice_comment)

    if chosen == "Specific <- painful":
        core.manual_persona_update(attributions)

    elif chosen == "Random":
        return attributions # altered by side effect

    elif chosen == "Descriptive":
        core.descriptive_attributes(attributions)

    return attributions # altered by side effect


def alien_life_span_bespoke(lifer: AlienRecord) -> AlienRecord:
    """
    determine alien life span
    """

    methods = ["Random", "Extreme"]
    chosen = please.choose_this(methods, "Choose a method for alien LIFE SPAN?")

    if chosen == "Random":
        life_span = alien_life_span()
        alien_life_stages(lifer,life_span)

    elif chosen == "Extreme":
        life_span_choices = [key for key in exp_tables.alien_life_span_descriptors.keys()]
        chosen = please.choose_this(life_span_choices, "Choose an EXTREME life. ")

        die_roll, multi = exp_tables.alien_life_span_descriptors[chosen]
        life_span = please.roll_this(die_roll) * multi
        alien_life_stages(lifer, life_span)

        if chosen == "Progeny - Short":
            lifer.Age_Suffix = choice(['Seconds', 'Minutes', 'Days'])
        elif chosen == "Progeny":
            lifer.Age_Suffix = choice(["Days","Weeks","Months"])

        # todo test progenic rationalization
        if chosen in ["Progeny - Short", "Progeny"] and please.say_yes_to(f"Rationalize size for short life span? "):
                ''' major fix for short lived'''
                if lifer.Size_Cat not in ["Tiny","Minute"]:
                    lifer.Size_Cat = choice(["Tiny","Minute"])
                    alien_hite_wate_calc(lifer)
                    core.wate_allowance(lifer)

        return

def alien_biology_bespoke(biological: AlienRecord) -> AlienRecord:
    """
    referee can adjust alien biology for bespoke aliens
    """
    alien_biology(biological)
    biology_list = biological.Biology
    if biological.Fallthrough:
        return

    methods = ["Random", "Bespoke"]
    chosen = please.choose_this(methods, "Choose a method for alien BIOLOGY? ")

    if chosen == "Bespoke":
        for i, bio_line in enumerate(biological.Biology[:-1]):
            bio_title = bio_line.split(":")[0]
            if please.say_yes_to(f'{bio_line} keep this? '):
                continue
            else:
                choices = [value for key, value in exp_tables.core_biology[bio_title].items() if key not in ["name","die_roll"] ]
                comment = f'Choose new value for {bio_title} '
                chosen = please.choose_this(choices, comment)
            biology_list[i] = f'{bio_title}: {choice}'

        ### alien sounds are different
        while not please.say_yes_to(f'{biological.Biology[-1]} keep this? '):
            sounds = alien_voice()
            biological.Biology[-1] = (f'Sounds: {sounds}.')
            biological.Sounds = sounds

        biological.Biology = biology_list

    return biological # is altered by side effect here

### build a FRESH alien persona
def fresh_alien(player_name:str) -> None:
    """
    builds a fresh alien object as per EXP persona creation
    """
    fresh = AlienRecord()
    fresh.Player_Name = player_name
    please.setup_persona(fresh)

    core.initial_attributes(fresh)
    fresh.Size_Cat = please.get_table_result(exp_tables.alien_size_fresh)
    fresh.HPM = core.hit_points_max(fresh)
    alien_hite_wate_calc(fresh)
    core.wate_allowance(fresh)

    attack_no = alien_attack_number(fresh)
    alien_attack_types(fresh, attack_no)
    alien_attack_description(fresh)


    core.base_armour_rating(fresh)
    alien_base_shape_random(fresh)
    alien_shape_adornments(fresh)
    core.movement_rate(fresh)
    alien_quick_description_builder(fresh)
    mental_amount, physical_amount = mutations.biologic_mutations_number(fresh)
    mutations.mutation_assignment(fresh, mental_amount, physical_amount,"any")
    
    life_span  = alien_life_span()
    alien_life_stages(fresh, life_span)
    fresh.Age = alien_age(fresh)

    alien_biology(fresh)
    alien_society(fresh)
    alien_vocation_check(fresh)
    please.wrap_up_persona(fresh)

### build a BESPOKE alien persona
def bespoke_alien(player_name:str) -> None:
    """
    Build a bespoke alien persona usually a referee persona
    """
    bespoke = AlienRecord()
    bespoke.Bespoke = True
    bespoke.Player_Name = player_name
    please.setup_persona(bespoke)

    alien_attributes_bespoke(bespoke)
    alien_size_cat_bespoke(bespoke)
    core.wate_allowance(bespoke)
    bespoke.HPM = core.hit_points_max(bespoke)
    alien_hite_wate_calc(bespoke)

    attack_no = alien_attack_number(bespoke)
    alien_attack_types(bespoke, attack_no)
    alien_attack_description(bespoke)

    core.base_armour_rating(bespoke)
    alien_base_shape_bespoke(bespoke)
    alien_shape_adornments(bespoke)
    core.movement_rate(bespoke)

    core.mutations_bespoke(bespoke)

    alien_life_span_bespoke(bespoke)
    bespoke.Age = alien_age(bespoke)

    vocation.exps_level_picker(bespoke)
    bespoke.EXPS = vocation.convert_levels_to_exps(bespoke)
    alien_biology_bespoke(bespoke)
    alien_society_bespoke(bespoke)

    alien_quick_description_builder(bespoke)

    if bespoke.RP_Cues:
        core.build_RP_role_play(bespoke) 

    if bespoke.Vocation != "Alien":
        vocation.set_up_first_time(bespoke)
        if bespoke.Level > 1:
            vocation.update_interests(bespoke, (bespoke.Level - 1))
            vocation.update_skills(bespoke, (bespoke.Level - 1))

    please.wrap_up_persona(bespoke)


### build a RANDO alien persona
def rando_alien(player_name:str) -> None:
    '''create an instant random alien'''
    rando = AlienRecord()
    rando.Fallthrough = True
    rando.Player_Name = player_name
    please.setup_persona(rando)

    core.initial_attributes(rando)
    alien_size_cat_rando(rando)
    core.wate_allowance(rando)
    rando.HPM = core.hit_points_max(rando)
    alien_hite_wate_calc(rando)

    attack_no = alien_attack_number(rando)
    alien_attack_types(rando, attack_no)
    alien_attack_description(rando)

    core.base_armour_rating(rando)

    alien_base_shape_random(rando)
    alien_shape_adornments(rando)
    core.movement_rate(rando)
    alien_quick_description_builder(rando)

    mental_amount, physical_amount = mutations.biologic_mutations_number(rando)
    mutations.mutation_assignment(rando, mental_amount, physical_amount,"any")
    
    life_span = alien_life_span()
    alien_life_stages(rando, life_span)
    rando.Age = alien_age(rando)

    vocation.exps_level_picker(rando)
    rando.EXPS = vocation.convert_levels_to_exps(rando)
    alien_biology_bespoke(rando)
    alien_society_bespoke(rando)

    if rando.RP_Cues:
        core.build_RP_role_play(rando) 

    if rando.Vocation != "Alien":
        vocation.set_up_first_time(rando)
        if rando.Level > 1:
            vocation.update_interests(rando, (rando.Level - 1))
            vocation.update_skills(rando, (rando.Level - 1))

    please.wrap_up_persona(rando)
