import math
from secrets import choice
from collections import Counter

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

def alien_attacks(type_casting: table.PersonaRecord) -> table.PersonaRecord:
    ''' 
    determine the alien attack types
    '''
    attack_no = please.get_table_result(table.attacks_per_unit)
    type_casting.Alternating = True if attack_no == 0 else False
    attack_no = 1 if attack_no == 0 else attack_no

    for _ in range(attack_no):
        type_casting.Attacks.append(f'{please.get_table_result(table.alien_attack_type)}')
       
    return type_casting # filled by side effects


# todo apply this to PROFs as damage + level 
def alien_damage_list(damaging: table.PersonaRecord) -> list:
    """
    damage per attack depends on Size and PSTR
    """

    alien_size = damaging.Size_Cat
    pstr = damaging.PSTR
    damages = []
    ### pull the damage line for a alien PSTR
    for strange, damage_line in table.alien_attack_damage.items():
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

def alien_attack_description(descriptor: table.PersonaRecord) -> list:
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
        attack_desc += f'{table.numbers_2_words[attack_no]} {attack_type} attack{"s" if attack_no > 1 else ""} ({damages[0]}) {alternating} '
       
    elif breadth > 1:
        for i, (attack_type, attack_no) in enumerate(attacks_counted.items()):
            attack_desc += f'{table.numbers_2_words[attack_no]} {attack_type} attack{"s" if attack_no > 1 else ""} ({damages[i]}), '
        attack_desc = attack_desc[:-2] + " every unit."

    attack_desc = attack_desc.capitalize()
    descriptor.Attack_Desc = attack_desc
    return attack_desc # also persona record altered by side effect

def alien_base_shape(shaping:table.PersonaRecord) -> table.PersonaRecord:
    ''' assigns a random animal shape to each body part '''
    four_quarter_parts = ["Head", "Body", "Arms", "Legs"]

    for part in four_quarter_parts:
        part_shape = choice(table.alien_quarter_shapes)
        setattr(shaping, part, part_shape)

    return shaping # adjusted by side effects in this function

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

def alien_shape_adornments(adornable:table.PersonaRecord) -> table.PersonaRecord:
    quarter_part_pivot = {
        "Head": table.alien_head_adornments,
        "Body": table.alien_body_adornments,
        "Arms": table.alien_arm_adornments,
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
def assign_terrain_movements(moving_time: table.PersonaRecord) -> table.PersonaRecord:
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


def alien_quick_description_builder(describing: table.PersonaRecord) -> table.PersonaRecord:
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


def alien_life_stages(staging:table.PersonaRecord, life_span:int = 42) -> dict:
    ''' creates a dict of the life stages for alien'''
    age_suffix = "years" if life_span > 6 else "months"
    life_span = life_span if life_span > 6 else life_span * 12

    ### calculate portion of life span in each stage
    # percent of age spent in each phase, times life_span = years spent in each stage
    child = life_span * (please.roll_this(table.alien_life_stages["Child"]) / 100)
    adol = life_span * (please.roll_this(table.alien_life_stages["Adolescent"])/ 100)
    adult = life_span * (please.roll_this(table.alien_life_stages["Adult"]) / 100)
    aged = life_span * (please.roll_this(table.alien_life_stages["Aged"]) / 100)

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
    die_roll, multi = please.get_table_result(table.alien_life_span_data)
    life_span = please.roll_this(die_roll) * multi

    return life_span # also aging modified by side effect

def alien_age(aging:table.PersonaRecord, stage:int = "Adol") -> int:
    ''' alien age based on age category'''
    tuple_ = aging.Life_Stages[stage]
    age = choice(range(tuple_[0],tuple_[1]+1))

    return age

def alien_voice() -> str:
    """
    returns a random alien noise
    """
    sound_one = please.get_table_result(table.alien_sounds)
    sound_two = please.get_table_result(table.alien_sounds)
    while sound_one == sound_two:
        sound_two = please.get_table_result(table.alien_sounds)

    return f"{sound_one}s and {sound_two}s"

def alien_biology(biologically:table.PersonaRecord) -> table.PersonaRecord:
    ''' create list of biological info'''

    alien_biology = []
    for bio_name, bio_table in table.core_biology.items():
        alien_biology.append(f'{bio_name}: {please.get_table_result(bio_table)}')

    ### alien sounds
    sounds = alien_voice()
    alien_biology.append(f'Sounds: {sounds}.')
    biologically.Sounds = sounds

    biologically.Biology = alien_biology

    return biologically # altered by side effect

def society_output(socializing: table.PersonaRecord) -> list:
    '''returns a list of strings describing society'''

    social_list = []

    ### add in tool usage
    for component,result in socializing.Society.items():
        if result != "None":
            social_list.append(f'{component}: {result}')

    return social_list

def alien_society(socialize: table.PersonaRecord) -> table.PersonaRecord:
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

    alien_society = {}
    alien_society["Tools"] = "Flora or Fauna" if table.alien_tool_score[tool_score] == "None" and not language else table.alien_tool_score[tool_score]
    alien_society["Language"] = "None" if not language else socialize.Sounds
    alien_society["Culture"] = "None" if not culture else "Yes"
    alien_society["Religion"] = "None" if not religion else please.get_table_result(table.role_play_RP_religion)
    alien_society["Education"] = "None" if not education else "Yes"
    alien_society["Politics"] = "None" if not politics else please.get_table_result(table.role_play_RP_politics)
    alien_society["Vocation"] = "None" if not vocay else "Yes"
    alien_society["Philosophy"] = "None" if not philosophy else please.get_table_result(table.role_play_RP_philosophy)
 
    socialize.Society = alien_society

    return socialize # altered by side effects

def alien_society_bespoke(bespoken: table.PersonaRecord) -> table.PersonaRecord:
    """
    first generates a society for the alien
    Second allow player to modify the society
    """
    alien_society(bespoken)

    methods = ["Random", "Bespoke"]
    chosen = please.choose_this(methods, "Choose a method for alien SOCIETY? ")

    if chosen == 'Random': 
        return

    for soc_name, value in bespoken.Society.items():
        if please.say_yes_to(f'{soc_name} = {value}, Is this okay? '):
            continue
        else:
            if soc_name in ["Tools", "Language", "Culture", "Education", "Vocation"]:
                chosen = please.choose_this(table.core_society[soc_name], f'Choose a new value for {soc_name}')
                bespoken.Society[soc_name] = chosen

            elif soc_name in ["Philosophy", "Politics","Religion"]:
                choice_list = [val for key,val in table.core_society[soc_name].items() if key not in ["name", "die_roll"]]
                chosen = please.choose_this(choice_list, f'Choose a new value for {soc_name}')
                bespoken.Society[soc_name] = chosen

    return bespoken # altered here by side effect

def alien_vocation_check(get_a_job:table.PersonaRecord) -> table.PersonaRecord:
    '''assigns a vocation to an alien if appropriate'''

    if get_a_job.Vocation == "Alien": return

    # todo vocation random could be a function
    if get_a_job.Fallthrough:    
        get_a_job.Vocation = choice([x for x in table.vocations_gifts_pivot])
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


def alien_nomenclature(naming: table.PersonaRecord) -> table.PersonaRecord:
    ''' get persona name and species name'''

    alien_species = please.input_this("What is the name of your entire ALIEN SPECIES? ")
    naming.FAMILY_TYPE = alien_species

    core.assign_persona_name

    return

####################################
# BESPOKE ALIEN FUNCTIONS
####################################

def alien_hite_wate_calc(picking_sizes: table.PersonaRecord) -> table.PersonaRecord :
    ''' 
    return actual wate and wate_suffix based on size_cat
    '''
    picking_sizes.Wate = please.roll_this(table.alien_size_wate[picking_sizes.Size_Cat])
    
    if picking_sizes.Size_Cat == "Minute":
        picking_sizes.Wate_Suffix = "gms"
        picking_sizes.PSTR = math.ceil(picking_sizes.PSTR * (picking_sizes.Wate / 1000))
        picking_sizes.HPM = math.ceil(picking_sizes.HPM * (picking_sizes.Wate / 1000))

    # todo humongous needs  * to dice suffix
    if picking_sizes.Size_Cat == "Humongous":
        picking_sizes.Wate *= 6 # 6d50 is different from 1d50*6
        picking_sizes.Wate_Suffix = "Tonnes"   

    return picking_sizes # modified by side effects


def alien_size_bespoke(choosing_sizes: table.PersonaRecord) -> table.PersonaRecord:
    """
    generate alien size_cat including minute and humongous
    """
    def fallthrough_diversion(m_or_h: table.PersonaRecord) -> table.PersonaRecord:
        m_or_h.Size_Cat = please.get_table_result(table.alien_size_fresh)

        if m_or_h.Size_Cat == "Tiny" and please.do_1d100_check(16):
            m_or_h.Size_Cat = "Minute"

        elif m_or_h.Size_Cat == "Gigantic" and please.do_1d100_check(16):
            m_or_h.Size_Cat = "Humongous"

        return # stays within bespoke

    if choosing_sizes.Fallthrough:
        fallthrough_diversion(choosing_sizes)
        return # choosing_sizes is altered by side effect

    methods = ["Random", "Bespoke"]
    choice_comment = "Choose a method for alien SIZE?"
    chosen = please.choose_this(methods, choice_comment)

    if chosen == "Random":
        fallthrough_diversion(choosing_sizes)

    elif chosen == "Bespoke":
        size_choices = [sizes for sizes in table.alien_size_and_WA.keys()]
        choosing_sizes.Size_Cat = please.choose_this(size_choices, "Choose a SIZE for your alien.")

    return choosing_sizes # adjusted by side effects


def alien_attributes_bespoke(attributions: table.PersonaRecord) -> table.PersonaRecord:
    """
    determine attributes
    """

    if attributions.Fallthrough:
        core.initial_attributes(attributions)
        return attributions # altered by side effect

    methods = ["Random", "Manual", "Descriptive"]
    choice_comment = "Choose a method for alien ATTRIBUTES?"
    chosen = please.choose_this(methods, choice_comment)

    if chosen == "Manual":
        core.initial_attributes(attributions)
        core.manual_persona_update(attributions)

    elif chosen == "Random":
        core.initial_attributes(attributions)

    elif chosen == "Descriptive":
        core.initial_attributes(attributions)
        core.descriptive_attributes(attributions)

    return attributions # altered by side effect


def alien_attacks_bespoke(attacking: table.PersonaRecord) -> table.PersonaRecord:
    """
    alien attack type and frequency
    """

    if attacking.Fallthrough:
        alien_attacks(attacking)
        
    methods = ["Random", "Bespoke"]
    choice_comment = "Choose a method for alien ATTACKS?"
    chosen = please.choose_this(methods, choice_comment)

    if chosen == "Random":
        alien_attacks(attacking)

    elif chosen == "Bespoke":
        attack_no = int(please.input_this("How many ATTACKS PER UNIT? "))
        for _ in range(attack_no):
            attacking.Attacks.append(f'{please.get_table_result(table.alien_attack_type)}')

    return attacking # is modified by side effect


def alien_life_span_bespoke(lifer: table.PersonaRecord) -> table.PersonaRecord:
    """
    determine alien life span
    """

    if lifer.Fallthrough:
        life_span = alien_life_span()
        alien_life_stages(lifer, life_span)
        return lifer # modified by side effect


    methods = ["Random", "Bespoke"]
    chosen = please.choose_this(methods, "Choose a method for alien LIFE SPAN?")

    if chosen == "Random":
        life_span = alien_life_span()
        alien_life_stages(lifer,life_span)

    elif chosen == "Bespoke":
        life_span_choices = [key for key in table.alien_life_span_descriptors.keys()]
        chosen = please.choose_this(life_span_choices, "Choose a LIFE SPAN DESCRIPTOR.")
        die_roll, multi = table.alien_life_span_descriptors[chosen]
        life_span = please.roll_this(die_roll) * multi
        alien_life_stages(lifer, life_span)

        if chosen == "Progeny - Short":
            lifer.Age_Suffix = choice(['Seconds', 'Minutes', 'Days'])
        elif chosen == "Progeny":
            lifer.Age_Suffix = choice(["Days","Weeks","Months"])

        return


def alien_biology_bespoke(biological: table.PersonaRecord) -> table.PersonaRecord:
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
                choices = [value for key, value in table.core_biology[bio_title].items() if key not in ["name","die_roll"] ]
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
    fresh.FAMILY_TYPE = "undiscovered"
    fresh.FAMILY_SUB = "undiscovered"
    fresh.Date_Created = "Unevolved"
    fresh.RP = False
    fresh.Attacks = []
    fresh.Alternating = False
    fresh.Attack_Desc = ""
    fresh.Life_Stages = {}
    fresh.Society = {}


    ### get mundane player name
    fresh.Player_Name = please.input_this("\nPlease input your MUNDANE TERRAN NAME: ")

    core.initial_attributes(fresh)
    fresh.Size_Cat = please.get_table_result(table.alien_size_fresh)
    core.hit_points_max(fresh)
    alien_hite_wate_calc(fresh)
    core.wate_allowance(fresh)
    alien_attacks(fresh)
    alien_attack_description(fresh)
    core.base_armour_rating(fresh)
    alien_base_shape(fresh)
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
    outputs.outputs_workflow(fresh, "screen")
    alien_nomenclature(fresh)
    please.assign_id_and_file_name(fresh)
    outputs.outputs_workflow(fresh, "screen")
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
    bespoke.Vocation = "Alien"
    bespoke.FAMILY_TYPE = "undiscovered"
    bespoke.FAMILY_SUB = "undiscovered"
    bespoke.Date_Created = "Unevolved"
    bespoke.RP = True
    bespoke.Attacks = []
    bespoke.Alternating = False
    bespoke.Attack_Desc = ""
    bespoke.Life_Stages = {}
    bespoke.Biology = []
    bespoke.Society = {}

    ### get mundane player name
    bespoke.Player_Name = please.input_this("\nPlease input your MUNDANE TERRAN NAME: ")

    alien_attributes_bespoke(bespoke)
    alien_size_bespoke(bespoke)
    core.wate_allowance(bespoke)
    core.hit_points_max(bespoke)
    alien_hite_wate_calc(bespoke)
    alien_attacks_bespoke(bespoke)
    alien_attack_description(bespoke)
    core.base_armour_rating(bespoke)
    alien_base_shape(bespoke)
    alien_shape_adornments(bespoke)
    core.movement_rate(bespoke)
    alien_quick_description_builder(bespoke)
    core.mutations_bespoke(bespoke)
    alien_life_span_bespoke(bespoke)
    alien_age(bespoke)
    vocation.exps_level_picker(bespoke)
    bespoke.EXPS = vocation.convert_levels_to_exps(bespoke)
    alien_biology_bespoke(bespoke)
    alien_society_bespoke(bespoke)
    if bespoke.Vocation != "Alien":
        vocation.set_up_first_time(bespoke)
        if bespoke.Level > 1:
            vocation.update_interests(bespoke, (bespoke.Level - 1))
            vocation.update_skills(bespoke, (bespoke.Level - 1))
    outputs.outputs_workflow(bespoke, "screen")
    alien_nomenclature(bespoke)
    please.assign_id_and_file_name(bespoke)
    outputs.outputs_workflow(bespoke, "screen")
    please.record_storage(bespoke)
    return

#####################################
# build a RANDO alien persona
#####################################

def rando_alien():
    pass