import math
import secrets
from typing import Sequence


import please
import table

# fix show_details and return_details may not be using build 
# todo allow Fallthrough to skip mutation choices
# fix defects get worse as level increases!

def mutation_workflow() -> None:
    """
    Mutate now avoid the post bomb rush
    """
    # clearance for Clarence
    please.clear_console()

    option_list = ["Random Mutations", "Bespoke Mutations"]
    list_comment = "Cruise through mutations :"
    plan_desired = please.choose_this(option_list, list_comment)

    fake_record = table.PersonaRecord
    fake_record.Mutations ={}

    if plan_desired == "Random Mutations":
        more_random = True
        while more_random:
            single_random_mutation(fake_record, ['any'])
            if not please.say_yes_to("Give me another mutation! "):
                break

    elif plan_desired == "Bespoke Mutations":
        more_random = True
        while more_random:
            pick_bespoke_mutation(fake_record)
            if not please.say_yes_to("Give me another mutation! "):
                break

    return

class Mutation:
    '''super class for mutations holding repeated methods'''

    def title(self) -> str:
        '''
        returns the title of the mutation in upper case
        '''
        return f"{self.name.upper()}"

    def headline(self) -> str:
        '''
        returns the title of the mutation in upper case plus mental vs physical
        '''
        return f"{self.name.upper()} {'mental mutation' if self.is_mental else 'physical mutation'}"

    def param_line(self) -> str:
        '''
        returns the parameters of the mutation
        not all some of these are returned as null
        '''
        return f"{self.calculate_parameter(self.distance)}{self.calculate_parameter(self.frequency)}{self.calculate_parameter(self.duration)}{self.calculate_parameter(self.roll_bonus)}" # space is added in str return from function

    def calculate_parameter(self, parameter) -> str:
        '''
        parameter determines the calc to be made returning nothing or string
        '''
        self.param_pivot = {
            self.distance: "RANGE: ",
            self.frequency: "FREQUENCY: ",
            self.duration: "DURATION: ",
            self.roll_bonus: "BONUS: ",
        }
        self.parameter = parameter

        if isinstance(self.parameter, str):
            return f"{self.param_pivot[self.parameter]}{self.parameter} "

        elif self.parameter is None:
            return ""

        elif isinstance(self.parameter, tuple):
            self.statribute, self.unit, self.divisor = self.parameter
            self.level_adjustment = (
                0 if self.statribute == "Level" else self.object.Level
            )  # corrects for level based parameters not doubling
            return f"{self.param_pivot[self.parameter]}{math.ceil((self.object.__dict__[self.statribute] + self.level_adjustment)/self.divisor)} {self.unit} " # space is important for formatting line

        return


    def post_details(self, subclass):
        self.desc = subclass.build_desc(self)
        print(f"\n{self.headline()}\n{self.desc}\n{self.param_line()}")
        return

    def return_details(self, subclass: any) -> str:
        self.desc = subclass.build_desc(self)
        self.params = self.param_line()
        self.header = self.headline()
        # self.details = f"\n{self.headline()}\n{self.desc}\n{self.param_line()}"
        return self.header, self.desc, self.params
    

    ##################################
    #
    # super() connected methods of Mutation
    #
    ##################################

    def return_perm(self, name:str, table:dict) -> str:
        '''returns a new perm, or protects the perm for MOST mutations'''
        if name in self.object.Mutations:
            return self.object.Mutations[name]
        elif table:
            return please.get_table_result(table)
        else:
            return None

    def add_mutation(self, name:str, perm:str, sentence:str) -> None:
        '''side effect on record to add mutation or returns doing nothing'''
        if name in self.object.Mutations:
            return 
        
        if self.object.Fallthrough:
            self.object.Mutations[name] = perm
            return

        if please.say_yes_to(f'{name.upper()} : {sentence} Add mutation? '):
            self.object.Mutations[name] = perm
        return

#######################################
# MENTAL MUTATIONS
#######################################

class Atestical(Mutation):
    '''
    testing grounds for the class and not used
    '''
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Atestical"
        self.kind = "combat"
        self.distance = "Persona"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "+4"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.mutation_absorbs
        self.link = "#_absorption"

    """ template
    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        # level part here
        description = f''
        #pre_add = len(self.object.Mutations)
        super().add_mutation(self.name, perm, description) # check to add
        if len(self.object.Mutations) > pre_add:
            self.object. 

        return description
    """

    def build_desc(self):
        # level dependent build
        hps_absorbed = self.object.HPM + self.object.Level * 3

        # permanent item build 
        perm = super().return_perm(self.name, self.table_name)
        # build description
        description = f'Absorb {hps_absorbed} HPS from {perm} attacks.'

        self.add_mutation(self.name, perm, description)

        return description


class Absorption(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Absorption"
        self.kind = "combat"
        self.distance = "Persona"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "+4"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.mutation_absorbs
        self.link = "#_absorption"
        
    def build_desc(self) -> str:
        '''sentence for mutation side effect adjust Mutations'''
        hps_absorbed = self.object.HPM + self.object.Level * 3  # level part
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Absorb {hps_absorbed} HPS from {perm} attacks.'
        super().add_mutation(self.name, perm, description) # check to add
        return description
    
class AlternateBanishment(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Alternate Banishment"
        self.kind = "combat"
        self.distance = ("Level", "hex", 1)
        self.duration = "Permanent"
        self.frequency = ("MSTR", "per Day", 12)
        self.CR = "+10"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_alternate_banishment"

    def build_desc(self) -> str:
        """returns mutation description and side effect via add_mutation()"""
        level_part = math.ceil(self.object.Wate / 2 + self.object.Level * 5) # level part
        perm = None
        description = f"Banish {level_part} kg sized target to an alternate dimension."
        super().add_mutation(self.name, perm, description) # check to add
        return description

class AlienAttachment(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Alien Attachment"
        self.kind = "non-combat"
        self.distance = "Touch"
        self.duration = "Permanent"
        self.frequency = ("Level", "alien(s)", 7)
        self.CR = "0"
        self.roll_bonus = "+10 on biologist rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_alien_attachment"
		
    def build_desc(self) -> str:
        """returns mutation description and side effect via add_mutation()"""
        alien_wate = math.ceil(self.object.Wate / 2) + (5 * self.object.Level)
        alien_smart = math.ceil(self.object.INT / 3) + self.object.Level
        alien_number = (self.calculate_parameter(self.frequency).split(":")[1].strip())
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f"Befriend {alien_number}. Alien max wate {alien_wate} kgs, max INT {alien_smart}."
        super().add_mutation(self.name, perm, description) # check to add
        return description

class Calculations(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Calculations"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = "+15 on calculation rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_calculations"
		
    def build_desc(self) -> str:
        """returns mutation description and side effect via add_mutation()"""
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = "Rapidly solve complex maths."
        super().add_mutation(self.name, perm, description) # check to add
        return description

class Communicate(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Communicate"
        self.kind = "non-combat"
        self.distance = "Earshot"
        self.duration = "Special"
        self.frequency = "Special"
        self.CR = "0"
        self.roll_bonus = "+15 language rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_communicate"

    def build_desc(self) -> str:
        """returns mutation description and side effect via add_mutation()"""
        perm = super().return_perm(self.name, self.table_name) # perm part
        learn_chance = (self.object.INT + self.object.Level) * 3
        lang_max = self.object.INT + self.object.Level
        description = f"Understand languages. {learn_chance}% to learn. Max {lang_max} languages."
        super().add_mutation(self.name, perm, description) # check to add
        return description

class Cryokinesis(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Cryokinesis"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = ("MSTR", "units", 0.2)
        self.frequency = ("MSTR", "per day", 5.0)
        self.CR = "+3"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_cryokinesis"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Worsening brain freeze per unit. Increasing damage 1d4, 2d4, 3d4, etc per unit.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class DeathFieldGeneration(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Death Field Generation"
        self.kind = "combat"
        self.distance = ("Level", "hex(es)", 1.0)
        self.duration = "Permanent"
        self.frequency = "As Needed"
        self.CR = "*3"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_death_field_generation"

    def build_desc(self) -> str:
        """returns mutation description and side effect via add_mutation()"""
        perm = super().return_perm(self.name, self.table_name) # perm part
        spare =  math.floor(self.object.Level/3)
        description = f'Drain all HPS in range and collapse. Spare {spare} persona(s).'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class DensityControl(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Density Control"
        self.kind = "non-combat"
        self.distance = ("Level", "hexes", 0.6666)
        self.duration = ("MSTR", "units", 0.3333)
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "+3"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_density_control_mental"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Mess with the density of a target.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class Detections(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Detections"
        self.kind = "non-combat"
        self.distance = ("AWE", "hexes", 0.1)
        self.duration = "Special"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = "+20 on searching rolls"
        self.attribute_bonus = None
        self.table_name = table.detection_types
        self.link = "#_detections"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        # building complex perm does not use perm function
        if self.name not in self.object.Mutations:

            perm = "Detect the following: "
            for detects in range(math.ceil(self.object.AWE / 5)):
                perm += (
                    f"{detects + 1 }) {please.get_table_result(self.table_name)} "
                )
        else:          
            perm = super().return_perm(self.name, self.table_name) # perm part
    
        description = perm
        super().add_mutation(self.name, perm, description) # check to add
        return description


class DirectionalSense(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Directional Sense"
        self.kind = "non-combat"
        self.distance = "Special"
        self.duration = "Constant"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = "+30 on wayfinding rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_directional_sense"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'You can always find your way.'
        super().add_mutation(self.name, perm, description) # check to add
        return description



class Empathy(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Empathy"
        self.kind = "non-combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = "Special"
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = "+20 on interpersonal rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_empathy"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Secretly listen to organic emotions'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class EnergyAttraction(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Energy Attraction"
        self.kind = "defect"
        self.distance = ("MSTR", "hexes", 0.1)
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_energy_attraction"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Deadly energies redirect toward persona.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class SeizureProjection(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Seizure Projection"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = "Special"
        self.frequency = ("MSTR", "per day", 1.0)
        self.CR = "+4"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_seizure_projection"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Induce random muscle contractions in organic target.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class ExtraSensoryProjection(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Extra Sensory Projection"
        self.kind = "non-combat"
        self.distance = ("MSTR", "hexes", 0.5)
        self.duration = ("MSTR", "units", 0.5)
        self.frequency = "Special"
        self.CR = "0"
        self.roll_bonus = "+20 on interpersonal rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_extra_sensory_projection"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Listen in on the thoughts of organic personas.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class ForceFieldGeneration(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Force Field Generation"
        self.kind = "combat"
        self.distance = "Persona"
        self.duration = "Until Destroyed"
        self.frequency = "1 per rest"
        self.CR = "*2"
        self.roll_bonus = "None"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_force_field_generation"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        # level part here
        ffabsorbs = 10 * (self.object.MSTR + self.object.Level)
        description = f'Personal energy shield absorbs {ffabsorbs} HPS.'
        super().add_mutation(self.name, perm, description) # check to add
        return description




class Gyrokinesis(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Gyrokinesis"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = ("MSTR", "units", 1.0)
        self.frequency = ("MSTR", "per day", 6.0)
        self.CR = "+3"
        self.roll_bonus = "None"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_gyrokinesis"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Force target to revolve.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class HeightenedBrainTalent(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Heightened Brain Talent"
        self.kind = "non-combat"
        self.distance = "Persona"
        self.duration = "Special"
        self.frequency = "1 per sleep"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_heightened_brain_talent"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        base_chance = 70 + self.object.Level + self.object.INT
        chance = base_chance if base_chance <100 else 98
        description = f'{chance}% chance to figure out, none plot point, problems. Cannot ruin stories.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class HostilityField(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Hostility Field"
        self.kind = "defect"
        self.distance = "1 hex "
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = "-25 on negotiation rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_hostility_field"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Gives off hostile vibes.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class IllusionGeneration(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Illusion Generation"
        self.kind = "non-combat"
        self.distance = ("MSTR", "hexes", 5.0)
        self.duration = "Special"
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_illusion_generation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Place hallucinations into organic targets.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class InformationEradication(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Information Eradication"
        self.kind = "combat"
        self.distance = ("Level", "hexes", 1.0)
        self.duration = "Special"
        self.frequency = ("MSTR", "per day", 5.0)
        self.CR = "+6"
        self.roll_bonus = "+15 on arguing rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_information_eradication"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Force target to forget specific memories.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class Intuition(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Intuition"
        self.kind = "non-combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = "Not Applicable"
        self.frequency = ("MSTR", "per day", 3.0)
        self.CR = "+2"
        self.roll_bonus = "+29 on intuition rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_intuition"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Get a yes/no answer to an imminent question.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class KnowledgeTransmission(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Knowledge Transmission"
        self.kind = "non-combat"
        self.distance = "Touch"
        self.duration = "Special"
        self.frequency = "Special"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_knowledge_transmission"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Walking organic thumb drive.'
        super().add_mutation(self.name, perm, description) # check to add
        return description




class Levitation(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Levitation"
        self.kind = "non-combat"
        self.distance = "Persona"
        self.duration = ("MSTR", "units", 0.0333)
        self.frequency = ("MSTR", "per day", 2.0)
        self.CR = "*4"
        self.roll_bonus = "+10 on sneaking"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_levitation"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        if self.object.FAMILY == "Anthro":
            dexmove = self.object.Move
            mstrmove = table.anthro_movement_rate_and_DEX[self.object.MSTR]
            levimove = (dexmove if dexmove > mstrmove else mstrmove) * 2
        else:
            levimove = self.object.Move

        description = f'Float straight up or down at {levimove} h/u.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class LifeLeech(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Life Leech"
        self.kind = "combat"
        self.distance = "Touch"
        self.duration = "Permanent"
        self.frequency = "Constant"
        self.CR = "special"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_life_leech"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        amount = self.object.Level + 5
        storage = self.object.HPM * 2
        description = f'Drain {amount} HPS per unit. Store up to {storage} HPS.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class LightWaveManipulation(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Light Wave Manipulation"
        self.kind = "non-combat"
        self.distance = "Persona"
        self.duration = ("MSTR", "units", 0.0333)
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "*4"
        self.roll_bonus = "+42 on sneaking, +25 on optics"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_light_wave_manipulation"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Manipulate the light around oneself.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class MagneticControl(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Magnetic Control"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = ("MSTR", "units", 1.0)
        self.frequency = ("MSTR", "per day", 2.0)
        self.CR = "+2"
        self.roll_bonus = "+10 on magnetic rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_magnetic_control"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Become a walking metallic magnet.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class MassMind(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Mass Mind"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = "Special"
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "+4"
        self.roll_bonus = "+10 psionic rolls."
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_mass_mind"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Amplify, combine or deflect psionic attacks.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class MechanicalSense(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Mechanical Sense"
        self.kind = "non-combat"
        self.distance = "Persona"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "*2"
        self.roll_bonus = "+42 on mechanical rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_mechanical_sense"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        chance_talk = (self.object.MSTR + self.object.Level) * 3
        description = f'{chance_talk}% chance to talk with a specific machine. Also 2nd level mechanic.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class MentalBlast(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Mental Blast"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 0.5)
        self.duration = "Permanent"
        self.frequency = "Alternating units"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_mental_blast"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Psionic blast for 2d4+{self.object.Level} HPS damage.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class MentalControl(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Mental Control"
        self.kind = "combat"
        self.distance = ("MSTR", "kms", 1.0)
        self.duration = "Special"
        self.frequency = "Special"
        self.CR = "Special"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_mental_control"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Control the minds of biological targets. Combined INT of all targets is {self.object.INT + self.object.Level}.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class MentalPhysiostasis(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Mental Physiostasis"
        self.kind = "combat"
        self.distance = "Persona"
        self.duration = "Constant"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_mental_physiostasis"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Optimized physiology 1/4 damage, 4 times benefit.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class MentalDefenselessness(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Mental Defenselessness"
        self.kind = "defect"
        self.distance = "Persona"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_mental_defenselessness"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'MSTR is 0 vs mental attacks.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class MolecularDisruption(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Molecular Disruption"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = "Permanent"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_molecular_disruption"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        disruptonnage = math.ceil(self.object.Wate / 2) + self.object.Level       
        description = f'Convert {disruptonnage} kgs matter in to cold gas. 1d20 HPS damage per kg.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class MolecularExamination(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Molecular Examination"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 0.333)
        self.duration = "Not Applicable"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = "+10 on examination rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_molecular_examination"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        aware = self.object.AWE + self.object.Level
        description = f'Find weaknesses. +{aware*10} on attack rolls. +{aware} on task rolls.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class MolecularPhaseTransformation(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Molecular Phase Transformation"
        self.kind = "combat"
        self.distance = "Persona"
        self.duration = ("MSTR", "units", 0.0333)
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_molecular_phase_transformation"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        # level part here
        description = f'Transform self between solid, liquid or gas.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class MolecularPhaseTransmutation(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Molecular Phase Transmutation"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = "Special"
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = "+25 on materiel rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_molecular_phase_transmutation"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        transmutograms = math.ceil(self.object.Wate / 2)
        description = f'Transform {transmutograms} kgs of a target into gas, liquid or solid. 1d8 HPS per kg. HPS = % disintegrate.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class MuscleManipulation(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Muscle Manipulation"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 0.25)
        self.duration = "Special"
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = "+6 on vet rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_muscle_manipulation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Manipulate the muscles of organic targets.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class Neuronegation(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Neuronegation"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 0.5)
        self.duration = "1d6 minutes"
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = "+42 on sedation rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_neuronegation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Disconnect organic target from all senses.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Phase(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Phase"
        self.kind = "combat"
        self.distance = "Persona"
        self.duration = "<1 unit"
        self.frequency = ("MSTR", "per day", 3.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_phase"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        carry = math.floor(self.object.WA / 4) + self.object.Level
        furtherness = math.ceil(self.object.Move * 2) + self.object.Level
        description = f'Phase into hyperspace carrying {carry} kgs and moving {furtherness} hexes.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class PlanalHideAway(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Planal Hide Away"
        self.kind = "combat"
        self.distance = "Special"
        self.duration = "As Needed"
        self.frequency = ("MSTR", "per day", 20.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_planal_hide_away"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Hide from physical space in your own temporal aberration.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class PlanalHoldAway(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Planal Hold Away"
        self.kind = "combat"
        self.distance = "Persona"
        self.duration = "Until Dead"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_planal_hold_away"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        if self.object.FAMILY in ["Anthro", "Alien"]:
            storage = table.wate_allowance_and_PSTR[self.object.MSTR] + self.object.Level
        else:
            storage = math.ceil(self.object.WA / 2)
        description = f'Carry {storage} kgs in your own space time aberration backpack.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class PolarDisruption(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Polar Disruption"
        self.kind = "defect"
        self.distance = ("Wate", "hexes", 20.0)
        self.duration = "1d6 units"
        self.frequency = "Random"
        self.CR = "0"
        self.roll_bonus = "+10 on magnetism rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_polar_disruption"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        draw = math.floor(self.object.WA / 2)
        description = f'Unexpectedly attract metallic objects <{draw} kgs toward mutant.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class PowerDrain(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Power Drain"
        self.kind = "combat"
        self.distance = "Touch"
        self.duration = "Permanent"
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = "+10 on battery rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_power_drain"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Drain battery get 1d10 HPS. Recharge battery take 1d12 HPS.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Precognition(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Precognition"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 0.333)
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = "Cannot be ambushed/"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_precognition"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Psionic pre-alert system to reduce injury.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class ProjectedSense(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Projected Sense"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 0.2)
        self.duration = ("MSTR", "units", 1.0)
        self.frequency = ("MSTR", "per day", 3.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_projected_sense"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Project a selected sense out of the body.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class ProtectionShell(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Protection Shell"
        self.kind = "combat"
        self.distance = ("Level", "hexes", 1.0)
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.protection_shell_options
        self.link = "#_protection_shell"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'{perm} cannot come within {self.object.Level} hexes.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class PsionicDefence(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Psionic Defence"
        self.kind = "combat"
        self.distance = "Persona"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_psionic_defence"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'MSTR is {self.object.MSTR * 2 + self.object.Level} for defensive MSTR rolls.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class Purify(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Purify"
        self.kind = "combat"
        self.distance = "Touch"
        self.duration = "Permanent"
        self.frequency = ("MSTR", "per day", 3.0)
        self.CR = "0"
        self.roll_bonus = "+42 on cleansing rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_purify"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Purify up to {math.ceil(self.object.WA / 10) + self.object.Level} kgs of stuff.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class Pyrokinesis(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Pyrokinesis"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 0.5)
        self.duration = ("MSTR", "units", 0.2)
        self.frequency = ("MSTR", "per day", 2.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_pyrokinesis"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Worsening brain cooking per unit. Increasing damage 1d4, 2d4, 3d4, etc per unit.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class RepulsionFieldGeneration(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Repulsion Field Generation"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = ("MSTR", "units", 1.0)
        self.frequency = ("MSTR", "per day", 6.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_repulsion_field_generation"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Incapacitate organics with nauseous. Spare {math.floor(self.object.Level / 2)} personas.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class Restoration(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Restoration"
        self.kind = "combat"
        self.distance = "Touch"
        self.duration = "Permanent"
        self.frequency = ("MSTR", "per day", 3.0)
        self.CR = "0"
        self.roll_bonus = "+25 on healing rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_restoration"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Heal organic targets with a touch.  Heal amount equals HPS Total (not HPM).'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class SensoryDeprivation(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Sensory Deprivation"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = ("MSTR", "units", 4.0)
        self.frequency = ("MSTR", "per day", 8.0)
        self.CR = "0"
        self.roll_bonus = "+10 on vet rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_sensory_deprivation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        # level part here
        description = f'Deny the target a specific sense (blinding, deafening, etc).'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class SociabilityFieldGeneration(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Sociability Field Generation"
        self.kind = "combat"
        self.distance = ("Level", "hexes", 2.0)
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = "+42 on charisma and +20 on negotiation rolls"
        self.attribute_bonus = ("SOC", 900)
        self.table_name = None
        self.link = "#_sociability_field_generation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'People really really like you. They really, really like you.'
        pre_add = len(self.object.Mutations)
        super().add_mutation(self.name, perm, description) # check to add
        if len(self.object.Mutations) > pre_add:
            self.object.SOC = 900 if self.object.SOC < 900 else self.object.SOC
        return description

class Sonar(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Sonar"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 0.05)
        self.duration = "Until Dead"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = "Triple AWE vs ambush."
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_sonar"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        # level part here
        description = f'Replace boring vision with 360 degree sonar.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class SonicAttack(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Sonic Attack"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 2.0)
        self.duration = "Speed of Sound"
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_sonic_attack"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        distance = math.ceil(self.object.MSTR / 2) + self.object.Level
        description = f'Sound blast range and damage: 1h 4d8 HPS, {math.ceil(distance/2)}h 3d8 HPS, {distance}h 2d8 HPS.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class SonicReproduction(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Sonic Reproduction"
        self.kind = "non-combat"
        self.distance = "Within Hearing"
        self.duration = ("MSTR", "units", 0.5)
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = "+10 on vocal shenanigans"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_sonic_reproduction"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        number = self.object.INT + self.object.Level
        description = f'Perfect audio copies. Store {number} copies up to {number * 2} units duration.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Suggestion(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Suggestion"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 2.0)
        self.duration = "Special"
        self.frequency = ("MSTR", "per day", 1.0)
        self.CR = "0"
        self.roll_bonus = "+40 on negotiation rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_suggestion"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'The more reasonable the more likely to succeed.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Telekinesis(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Telekinesis"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 0.5)
        self.duration = ("MSTR", "units", 0.5)
        self.frequency = ("MSTR", "per day", 3.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_telekinesis"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        speed = table.anthro_movement_rate_and_DEX[self.object.MSTR] + self.object.Level
        amount = table.wate_allowance_and_PSTR[self.object.MSTR] + self.object.Level
        description = f'Move up to {amount} kgs at {speed} h/u with your mind.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class TelekineticArm(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Telekinetic Arm"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = ("MSTR", "units", 1.0)
        self.frequency = ("MSTR", "per day", 3.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_telekinetic_arm"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        arm_wate = table.wate_allowance_and_PSTR[self.object.MSTR] + self.object.Level
        arm_hps = math.ceil(self.object.HPM/2)  + self.object.Level
        description = f'Invisible extra hand with {arm_hps} HPS that can lift {arm_wate} kgs.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class TelekineticFlight(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Telekinetic Flight"
        self.kind = "combat"
        self.distance = "Persona"
        self.duration = ("MSTR", "units", 0.0333)
        self.frequency = ("MSTR", "per day", 3.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_telekinetic_flight"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        speed = table.anthro_movement_rate_and_DEX[self.object.MSTR] * 2 + self.object.Level
        description = f'Fly around at {speed} h/u.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class Telempathy(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Telempathy"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 1.0)
        self.duration = ("MSTR", "units", 0.0333)
        self.frequency = ("MSTR", "per day", 6.0)
        self.CR = "0"
        self.roll_bonus = "+40 on negotiation and +20 on vet rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_telempathy"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        # level part here
        description = f'Push emotions into the mind of an organic target.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class Teleport(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Teleport"
        self.kind = "combat"
        self.distance = ("MSTR", "kms", 0.002)
        self.duration = "Instantaneous"
        self.frequency = ("MSTR", "per day", 12.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_teleport"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Instantly pop to familiar places.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class ThoughtImitation(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Thought Imitation"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 0.25)
        self.duration = "One Use"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = "+42 on learning rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_thought_imitation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Flawlessly copy actions and mutations.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class TimeStop(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Time Stop"
        self.kind = "combat"
        self.distance = "Consciousness"
        self.duration = ("MSTR", "units", 1.0)
        self.frequency = ("MSTR", "per day", 24.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_time_stop"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        lift = table.wate_allowance_and_PSTR[self.object.MSTR] * 10 + self.object.Level
        description = f'Arrest the movement of time. Move freely and lift {lift} kgs.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class TimeTell(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Time Tell"
        self.kind = "non-combat"
        self.distance = "Persona"
        self.duration = "Until time runs out."
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = "+42 on timing rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_time_tell"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Atomic clock precision time telling.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class TotalRecuperation(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Total Recuperation"
        self.kind = "combat"
        self.distance = "Persona"
        self.duration = "Until Dead"
        self.frequency = ("MSTR", "per day", 12.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_total_recuperation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Instantly restore back to full ({self.object.HPM}) HPS.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Ventriloquism(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Ventriloquism"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 0.5)
        self.duration = ("MSTR", "units", 0.0333)
        self.frequency = ("MSTR", "per day", 3.0)
        self.CR = "0"
        self.roll_bonus = "+13 on shenanigans rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_ventriloquism"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Make the voice appear to come from elsewhere.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class WeaponDischarging(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Weapon Discharging"
        self.kind = "defect"
        self.distance = "2 hex"
        self.duration = "Until Dead"
        self.frequency = "1 per day"
        self.CR = "0"
        self.roll_bonus = "+10 on activating things"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_weapon_discharging"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        boom = math.ceil((self.object.MSTR - self.object.Level) / 2)
        boom_boom = boom if boom > 0 else 2

        description = f'A {boom_boom}% chance of accidental activation'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class WeatherTell(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Weather Tell"
        self.kind = "combat"
        self.distance = ("MSTR", "days", 1.0)
        self.duration = "As Needed"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = "+42 on nomad rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_weather_tell"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        # level part here
        description = f'Less accurate the further out.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


#######################################
# PHYSICAL MUTATIONS
#######################################

class AcidicEnzymes(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Acidic Enzymes"
        self.kind = "combat"
        self.distance = ("PSTR", "hex", 1)
        self.duration = "Constant"
        self.frequency = "Alternating Units"
        self.CR = "+2"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_acidic_enzymes"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Spit acid (fling) every other unit 2d8+{self.object.Level} HPS damage.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Adaptation(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Adaptation"
        self.kind = "non-combat"
        self.distance = "Persona"
        self.duration = "Special"
        self.frequency = "Constant"
        self.CR = "*3"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_adaptation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        chancey_pants = self.object.CON + self.object.INT + self.object.Level
        perma_nerma = self.object.Level
        description = f'A {chancey_pants}% chance of temporary immunity. {perma_nerma}% chance becomes permanent. Max {perma_nerma} permanents.'
        super().add_mutation(self.name, perm, description) # check to add
        return description
    

class AttractionOdor(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Attraction Odor"
        self.kind = "non-combat"
        self.distance = ("PSTR", "km", 1)
        self.duration = "Special"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = "+15 on negotiation rolls"
        self.attribute_bonus = ("CHA", 2)
        self.table_name = table.list_of_life_forms
        self.link = "#_attraction_odor"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        # level part here
        description = f'Constantly attracts {perm}.'
        # add attribute bonus check
        pre_add = len(self.object.Mutations)
        super().add_mutation(self.name, perm, description) # check to add
        if len(self.object.Mutations) > pre_add:
            self.object.CHA += 2

        return description

class Arms(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Arms"
        self.kind = "defect"
        self.distance = "Fingertip"
        self.duration = "Permanent"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.table_name = None
        self.attribute_bonus = ("DEX", -1)
        self.link = "#_arms"
   
    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        arm_table = table.family_hit_location_pivot_table[self.object.FAMILY]
        arms_number = please.roll_this("1d4")

        if self.name not in self.object.Mutations:
            arm_table = table.family_hit_location_pivot_table[self.object.FAMILY]
            arms_number = please.roll_this("1d4")
            perm = ""
            for army in range(arms_number):
                perm += f" {army+1}) {please.get_table_result(arm_table)}"

        description = f'Extra arm(s) located:{perm}'

        pre_add = len(self.object.Mutations)
        super().add_mutation(self.name, perm, description) # check to add
        if len(self.object.Mutations) > pre_add and self.object.RP: # DEX penalty if RP
            self.object.DEX -= arms_number

        return description
   
class BodyStructureChange(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Body Structure Change"
        self.kind = "non-combat"
        self.distance = "Persona"
        self.duration = ("CON", "hour", 1.0)
        self.frequency = ("CON", "per day", 6.0)
        self.CR = "0"
        self.roll_bonus = "+100 on disguise rolls."
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_body_structure_change"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Change shape at will.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Carapace(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Carapace"
        self.kind = "combat"
        self.distance = "Skin Deep"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "+1"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_carapace"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part

        if self.name not in self.object.Mutations: #create the perm thickness
            carapaline = please.get_table_result(table.carapace_thickness)
            perm = next(iter(carapaline))
            
        for _, carapacity in table.carapace_thickness.items():
            if perm in carapacity:
                break
        
        # create elements for description and penalties 
        AR_adjust = carapacity[perm]['AR']
        damage_reduction = carapacity[perm]['DA']
        CHA_adjust = carapacity[perm]['cha_penalty']
        DEX_adjust = carapacity[perm]['dex_penalty']
    
        description = f'A protective, but uglifying, {perm.lower()} carapace: damage reduction (damage x {damage_reduction})'

        pre_add = len(self.object.Mutations)
        super().add_mutation(self.name, perm, description) # check to add
        if len(self.object.Mutations) > pre_add: # add bonuses
            self.object.AR += AR_adjust

        if len(self.object.Mutations) > pre_add and self.object.RP:
            self.object.DEX += DEX_adjust
            self.object.CHA += CHA_adjust

        return description


class Chameleon(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Chameleon"
        self.kind = "non-combat"
        self.distance = "Skin Deep"
        self.duration = "As Needed"
        self.frequency = "As Needed"
        self.CR = "+5"
        self.roll_bonus = "+25 on sneaky rolls."
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_chameleon"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Blend into background when naked and motionless.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Decoy(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Decoy"
        self.kind = "non-combat"
        self.distance = "Special"
        self.duration = "Not Applicable"
        self.frequency = "1 sleep to regenerate"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_decoy"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        intensity = math.ceil(self.object.PSTR / 2) + self.object.Level
        description = f'Drop a fleshy decoy that attracts low INT targets. Poison intensity {intensity}.'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class DensityManipulation(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Density Control"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = ("CON", "minutes", 1.0)
        self.frequency = ("PSTR", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = "+15 on wate rolls."
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_density_manipulation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Change density to walk on a liquid or gas.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class DiminishedSense(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Diminished Sense"
        self.kind = "defect"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.diminished_sense
        self.link = "#_diminished_sense"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Mutant has diminished {perm.lower()} '
        super().add_mutation(self.name, perm, description) # check to add
        return description


class DoublePhysicalPain(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Double Physical Pain"
        self.kind = "defect"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_double_physical_pain"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'PAIN is doubled, add 2d8 HPS to any damage, HEAL twice as fast.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class EdibleTissue(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Edible Tissue"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Grows back in 1 sleep"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_edible_tissue"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Thick fleshy strips feed the mutant for a day.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class ElectricShock(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Electric Shock"
        self.kind = "combat"
        self.distance = ("PSTR", "hexes", 2.0)
        self.duration = "Instantaneous"
        self.frequency = "Alternating Units"
        self.CR = "+4"
        self.roll_bonus = "+13 on resuscitation rolls."
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_electric_shock"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        electro_bump = self.object.Level
        description = f'Touch for 1d10+{6 + electro_bump} or shoot bolt for 3d4+{electro_bump}.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class EnthalpyAttack(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Enthalpy Attack"
        self.kind = "combat"
        self.distance = ("PSTR", "hexes", 1.0)
        self.duration = "Permanent"
        self.frequency = "Alternating Units"
        self.CR = "+3"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_enthalpy_attack"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Shoot a blast of cold and ice for 2d8+{self.object.Level}.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class FatCellAccumulation(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Fat Cell Accumulation"
        self.kind = "defect"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "*.9"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_fat_cell_accumulation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        if self.name not in self.object.Mutations:
            perm = please.get_table_result(table.family_hit_location_pivot_table[self.object.FAMILY])
        description = f'Big obvious fat blob on the {perm} of the persona.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class GasGeneration(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Gas Generation"
        self.kind = "combat"
        self.distance = "5 hex radius"
        self.duration = "1d4-1 units"
        self.frequency = ("CON", "per day", 5.0)
        self.CR = "10"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.poison_gas_type
        self.link = "#_gas_generation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'{perm} Intensity {math.ceil(self.object.CON/2) + self.object.Level}.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Haste(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Haste"
        self.kind = "combat"
        self.distance = "Persona Only"
        self.duration = ("CON", "units", 1.0)
        self.frequency = ("CON", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_haste"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Double speed of everything. Double MOVE and half task time.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class HeatGeneration(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Heat Generation"
        self.kind = "combat"
        self.distance = ("CON", "hexes", 1.0)
        self.duration = "Constant"
        self.frequency = "Alternating units."
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_heat_generation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Searing flame attack (shoot) for 3d6+{self.object.Level} HPS damage.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


# todo reassess persona DEX -> move, PSTR -> WA, CON -> HPM
class HeightenedAttribute(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Heightened Attribute"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.heightened_attribute
        self.link = "#_heightened_attribute"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'{perm}'
        pre_add = len(self.object.Mutations)
        super().add_mutation(self.name, perm, description) # check to add
        if len(self.object.Mutations) > pre_add:
            hattribute, _ = perm.split(":")
            old_attribute = getattr(self.object, hattribute)
            new_attribute = (old_attribute + please.roll_this("2d8")) if (old_attribute + please.roll_this("2d8")) > 15 else 15
            if hattribute == "HPM": # HPM is a special case and not 2d8
                new_attribute =  math.ceil(old_attribute * 1.5)         
            setattr(self.object, hattribute, new_attribute)
        return description


class HeightenedVision(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Heightened Vision"
        self.kind = "combat"
        self.distance = "Special"
        self.duration = "Until Dead"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.heightened_vision
        self.link = "#_heightened_vision"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        myopic, _ = perm.split(":")
        if myopic in ['Infravision','Semi Circular']:
            perm_plus = f'Up to {self.object.AWE * 2 + self.object.Level} hexes.'
        elif myopic == "X-Ray":
            perm_plus = f"Up to {math.ceil((self.object.AWE + self.object.Level)/8)} hexes."
        elif myopic == "Telescopic":
            perm_plus = f"Up to {(self.object.AWE + self.object.Level)* 10} hexes."
        else:
            perm_plus = ""

        description = f'{perm} {perm_plus}'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class IncreasedMetabolism(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Increased Metabolism"
        self.kind = "defect"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_increased_metabolism"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Burn twice the energy and need twice the food.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class LaunchableQuills(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Launchable Quills"
        self.kind = "combat"
        self.distance = ("PSTR", "hexes", 1.0)
        self.duration = None
        self.frequency = "Grow back one per rest."
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_launchable_quills"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm check

        # todo consider a random poison effect
        if self.name not in self.object.Mutations: # perm build
            quill_number = please.roll_this("2d6")
            poisonous = 'poisonous stabby' if please.do_1d100_check(self.object.CON) else 'stabby'
            perm = f'{str(quill_number)}: {poisonous}'

        ### build description
        amount,poison = perm.split(":")
        amount = int(amount)
        intensity = "" if "poison" not in poison else f'Poison intensity {self.object.CON + self.object.Level}.'
        hold_back = "all" if amount - self.object.Level < 1 else self.object.Level
        description = f'{amount} launchable {poisonous} quills. Hold back {hold_back} quill(s). 1d8 HPS damage, fling attack. {intensity}'
        super().add_mutation(self.name, perm, description) # check to add
        return description



class LightGeneration(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Light Generation"
        self.kind = "combat"
        self.distance = ("CHA", "hexes", 1.0)
        self.duration = "Special"
        self.frequency = ("CON", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_light_generation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        some_thing = self.object.CHA + self.object.Level
        description = f'Glow 1 hex. Flashlight {some_thing} hexes. Blinding flash intensity {some_thing}.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class MechanicalInsertion(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Mechanical Insertion"
        self.kind = "non-combat"
        self.distance = "Special"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_mechanical_insertion"

    ### todo roll the actual toy type
    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part

        if self.name not in self.object.Mutations:
            insertion_location = please.get_table_result(table.family_hit_location_pivot_table[self.object.FAMILY])
            insertion_type = please.get_table_result(table.toy_categories)
            perm = f'{insertion_location}:{insertion_type}'

        ### build description
        insertion_location, insertion_type = perm.split(":")
        description = f'The artifact {insertion_type} is built into the {insertion_location} of the persona'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Mitosis(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Mitosis"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = "Special"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_mitosis"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Organs grow back. No aging. No ongoing damage.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class MechanicalProsthesis(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Mechanical Prosthesis"
        self.kind = "defect"
        self.distance = "Persona Only"
        self.duration = "Until Removed"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_mechanical_prosthesis"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        if self.name not in self.object.Mutations:
            perm = please.get_table_result(table.family_hit_location_pivot_table[self.object.FAMILY])
        description = f'A noisy prosthesis has replaced the {perm} of this persona.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class MultipleBodyParts(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Multiple Body Parts"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_multiple_body_parts"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''

        if self.name not in self.object.Mutations: # complex perm generation
            perm = f'{please.get_table_result(table.multiple_body_parts)}:{please.roll_this("1d4")}'
        else:
            perm = super().return_perm(self.name, self.table_name) # perm part

        ### Build description
        body_part,number = perm.split(":")
        number = int(number)
        CHA_bump = 0
        AWE_bump = 0
        Move_bump = 0

        print(f'{body_part = }')

        if body_part == "Arms":
            description = f'{number} additional fully functional arms.'

        elif body_part in ["Ears", "Eyes", "Feet", "Fingers"]:
            description = f'{number} additional cosmetic and functional {body_part.lower()}.'
            CHA_bump += number if body_part in ["Ears", "Eyes"] else 0
            AWE_bump += number if body_part in ["Ears", "Eyes"] else 0

        elif body_part in ["Heads","Mouths","Noses"]:
            description = f'{number} additional semi-autonomous unappealing {body_part.lower()}'
            CHA_bump += number*2 if body_part == "Heads" else number
            AWE_bump += number if body_part == "Noses" else 0

        elif body_part == "Legs":
            description = f'{number} additional fully functional {body_part.lower()}.'
            Move_bump = 3 + number

        pre_add = len(self.object.Mutations)
        super().add_mutation(self.name, perm, description) # check to add
        if len(self.object.Mutations) > pre_add:
            self.object.AWE += AWE_bump
            self.object.Move += Move_bump
            if self.object.RP:
                self.object.CHA -= CHA_bump

        return description


class NewOrgan(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "New Organ"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.new_organ_type
        self.link = "#_new_organ"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        ## irritation perm swaps for light and plastics 
        if perm == "Light Emitting Flesh: Creates a radiant glow.":
            perm = "Light Absorbing Flesh: Creates a shadow." if please.do_1d100_check(20) else perm
        if perm == "Plastics Producing Gland: Plastic oozing organ.":
            perm = "Plastics Destroying Gland: Melt away, and eat plastics." if please.do_1d100_check(30) else perm

        title, _ = perm.split(":")
        bonus_info = ""

        if title in ["Light Emitting Flesh", "Light Absorbing Flesh"]:
            bonus_info = f'Radius is {self.object.Level} hexes.'

        elif title == "Blood Draining Proboscis":
            bonus_info = f'Slurp up {math.ceil(self.object.Level/2)}d6 per unit.'

        elif title == "Electricity Storing Organ":
            bonus_info = f'Recharge {self.object.CON} cells. Zap for {math.ceil(self.object.Level/2)}d8 HPS, 1 hex range.'

        elif title == "Ink Producing Gland":
            bonus_info = f'Cloud water as needed. Squirt to blind {math.ceil(self.object.CON/2) + self.object.Level} intensity, {math.ceil(self.object.Level)} hex range, alternating units.' 

        elif title == "Kirlian Energy Reflective Skull":
            bonus_info = f'MSTR is {self.object.MSTR * 2 + self.object.Level} vs mental attacks.'

        description = f'{perm} {bonus_info}'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class NonBreathing(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Non Breathing"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = "+100 on breath holding tantrums."
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_non_breathing"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        # level part here
        description = f'Respiration without air or light.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class NoResistanceToDisease(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "No Resistance To Disease"
        self.kind = "defect"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_no_resistance_to_disease"


    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'CON is {math.ceil(self.object.Level/2)}  vs infectious diseases.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class NoResistanceToPoison(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "No Resistance To Poison"
        self.kind = "defect"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_no_resistance_to_poison"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'CON is {math.ceil(self.object.Level/2)}  vs toxins.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class OversizedBodyPart(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Oversized Body Part"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.oversized_body_part
        self.link = "#_oversized_body_part"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part

        ### build description
        bonus_info = ""
        if perm in ["Ears","Nose: Super taster", "Nose. Super taster"]:
             bonus_info = f"AWE = {self.object.AWE * 2 + self.object.Level} vs ambush."
        elif perm == "Lungs":
            bonus_info = f"Hold breath for {self.object.CON + self.object.Level} minutes."
        description = f'Obviously oversized {perm}. {bonus_info}'

        pre_add = len(self.object.Mutations)
        super().add_mutation(self.name, perm, description) # check to add
        if len(self.object.Mutations) > pre_add:
            if perm == "Arms":
                self.object.PSTR += 2
            
            elif perm == "Brain":
                self.object.INT += 2
                self.object.MSTR += 2

            elif perm in ["Ears","Eyes. See in darkness", "Nose. Super taster"]:
                self.object.AWE += 2

            elif perm == "Loins":
                    self.object.CON += 1
                    self.object.CHA += 1
                    self.object.HPM += please.roll_this("1d8+1")

            elif perm in ["Heart","Lungs"]:
                self.object.CON += 2

            elif perm == "Legs":
                self.object.PSTR += 2
                self.object.Move = math.ceil(self.object.Move * 1.5)

        return description


class PhotosyntheticSkin(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Photosynthetic Skin"
        self.kind = "non-combat"
        self.distance = "Skin Deep"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_photosynthetic_skin"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        bonus_info = "" if self.object.FAMILY_TYPE != "Florian" else "Double healing rate (florian)."
        description = f'Respiration via photosynthesis. Hold breath indefinitely. {bonus_info}'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class PhosphorescentSkin(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Phosphorescent Skin"
        self.kind = "defect"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_phosphorescent_skin"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Continuous infuriating glow.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Pockets(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Pockets"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = "+30 on concealment rolls."
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_pockets"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Create up to {self.object.Level} pocket(s) hiding up to {math.ceil(self.object.Wate * 0.05) + self.object.Level} kgs.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class PressurizedBody(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Pressurized Body"
        self.kind = "combat"
        self.distance = "Special"
        self.duration = ("PSTR", "units", 1.0)
        self.frequency = ("CON", "per day", 1.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_pressurized_body"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Negate crushing attacks. Fall {self.object.Level + self.object.PSTR} hexes no damage.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class RadiatingEyes(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Radiating Eyes"
        self.kind = "combat"
        self.distance = ("AWE", "hexes", 1.0)
        self.duration = None
        self.frequency = "Alternating units"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_radiating_eyes"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Bright beams of radiation shoot from the eyes. Intensity 2d6+{self.object.Level}.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Regeneration(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Regeneration"
        self.kind = "combat"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = None
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_regeneration"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        base_heal = self.object.CON + self.object.Level
        description = f"Heal {math.ceil(base_heal/5)} HPS per unit. Massive regen {math.ceil(base_heal/2)} HPS once a day"
        super().add_mutation(self.name, perm, description) # check to add
        return description


class RubberySkin(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Rubbery Skin"
        self.kind = "non-combat"
        self.distance = "Skin Deep"
        self.duration = "Long after death"
        self.frequency = None
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_rubbery_skin"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        # level part here
        description = f'Inorganic rubbery exterior layer. '
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Rust(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Rust"
        self.kind = "combat"
        self.distance = "Touch"
        self.duration = "Permanent"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_rust"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Instantaneous metallic oxidation. 10d10 vs robots with strike attack.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class SelfDestruction(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Self Destruction"
        self.kind = "defect"
        self.distance = ("Level", "hexes", 0.5)
        self.duration = None
        self.frequency = "Once"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_self_destruction"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Spontaneous violent combustion possible. {self.object.CON}d20 HPS damage, {self.object.Level} hex radius.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class ShapeChange(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Shape Change"
        self.kind = "combat"
        self.distance = "Persona Only"
        self.duration = ("CHA", "minutes", 1.0)
        self.frequency = ("CON", "per day", 5.0)
        self.CR = "0"
        self.roll_bonus = "+150 on disguise rolls"
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_shape_change"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Cosmetically change into any organic shape.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class SizeManipulation(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Size Manipulation"
        self.kind = "combat"
        self.distance = "Persona Only"
        self.duration = ("CHA", "minutes", 1.0)
        self.frequency = ("CON", "per day", 3.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_size_manipulation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        two_sizes = self.object.Hite
        one_pstr = self.object.PSTR
        da_a = math.ceil((one_pstr / 2) * 1.5)
        description = f"Shrink to {math.floor(two_sizes * .25)} cms (AR {self.object.AR + 75}). Enlarge to {math.ceil(two_sizes * 1.5)} cms (Strike attack force {da_a} HPS)."
        super().add_mutation(self.name, perm, description) # check to add
        return description


class SkinStructureChange(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Skin Structure Change"
        self.kind = "combat"
        self.distance = "Skin Deep"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.skin_structure_change
        self.link = "#_skin_structure_change"
        # self.add_mutation() removed for complex perm

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        skin_change, AR_bump = perm.split(":")
        AR_bump = int(AR_bump)
        description = f'{skin_change}.'
        pre_add = len(self.object.Mutations)
        super().add_mutation(self.name, perm, description) # check to add
        if len(self.object.Mutations) > pre_add:
            self.object.AR += AR_bump
        return description


class SmokeScreen(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Smoke Screen"
        self.kind = "combat"
        self.distance = None
        self.duration = "1d12 minutes"
        self.frequency = ("CON", "per day", 2.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_smoke_screen"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        diameter = math.ceil((self.object.PSTR + self.object.Level) / 3)
        length = diameter * self.object.Move 
        description =  f"Smoke cloud {diameter} hexes or smoke fence {length} hexes."
        super().add_mutation(self.name, perm, description) # check to add
        return description


class SonarAttack(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Sonar Attack"
        self.kind = "combat"
        self.distance = ("MSTR", "hexes", 2.0)
        self.duration = "Speed of Sound"
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_sonar_attack"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        distance = math.ceil(self.object.MSTR / 2) + self.object.Level
        description = f'Sound blast: 1h 4d8, {math.ceil(distance/2)}h 3d8, {distance}h 2d8'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class SpitPoison(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Spit Poison"
        self.kind = "combat"
        self.distance = ("PSTR", "hexes", 1.0)
        self.duration = "Special"
        self.frequency = "Alternating units"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.poison_spittle_type
        self.link = "#_spit_poison"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        intensity = f'intensity 1d8+{self.object.Level}. Incapacitated 1 unit per intensity' if perm != "Killing poison" else  f'intensity 1d8+{self.object.Level}. 1d4 HPS per intensity.'
        description = f'{perm}, {intensity}'
        super().add_mutation(self.name, perm, description) # check to add
        return description

class StaticQuills(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Static Quills"
        self.kind = "combat"
        self.distance = "Persona Only"
        self.duration = "Permanent"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_static_quills"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Spines and quills hurt attackers. 1d6+{self.object.Level} HPS vs punches.'
        pre_add = len(self.object.Mutations)
        super().add_mutation(self.name, perm, description) # check to add
        if len(self.object.Mutations) > pre_add:
            self.object.AR += 101 
        return description


class StrangeNewBodyPart(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Strange New Body Part"
        self.kind = "combat"
        self.distance = "Persona Only"
        self.duration = "Permanent"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.strange_new_body_part
        self.link = "#_strange_new_body_part"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part

        bonus_info = ""
        if perm in [
            "Antennae replace ears. Listen around corners.",
            "Ears fold up and down like an accordion.",
            "Eyes are concave reflectors.",
            "Eye Stalks (30cms) replace eye sockets. Look around corners.",
            "Nose is a long flexible tube. Smell around corners.",
            ]:
            bonus_info = f"AWE = {2* self.object.AWE} vs ambush."
            
        elif perm in [
            "Fins attached to arms, and legs. Swim like an aquarian.",
            "Gills for breathing underwater. Swim like an aquarian.",]:
            bonus_info = f"Swim at {self.object.Move} h/u."
            if self.object.FAMILY_TYPE == "Aquarian":
                bonus_info = f"Swim at {self.object.Move * 2} h/u. (Aquarian)"
        description = f'{perm} {bonus_info}'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class SymbioticAttachment(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Symbiotic Attachment"
        self.kind = "combat"
        self.distance = "1 hex"
        self.duration = "Permanent"
        self.frequency = None
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_symbiotic_attachment"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Control organic target via nerve tentacle.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class TearAwayBodyPart(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Tear Away Body Part"
        self.kind = "combat"
        self.distance = ("AWE", "hexes", 1.0)
        self.duration = ("CON", "hours", 1.0)
        self.frequency = None
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_tear_away_body_part"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Tear off {self.object.Level} parts per day. Each part has {math.ceil(self.object.HPM / 10) + self.object.Level} HPS.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class UndersizedBodyPart(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Undersized Body Part"
        self.kind = "defect"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.undersized_body_part
        self.link = "#_undersized_body_part"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        # level part here
        description = f'Obviously undersized {perm}. Cannot hide it. No deficits.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Vibrations(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Vibrations"
        self.kind = "combat"
        self.distance = "Touch"
        self.duration = ("DEX", "units", 3.0)
        self.frequency = ("DEX", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = "+42 on massage rolls."
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_vibrations"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        description = f'Ranges from a nice massage to damaging strike attack. 3d4+{self.object.Level} HPS damage. +97 on strike attack roll.'
        super().add_mutation(self.name, perm, description) # check to add
        return description


class WateManipulation(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Wate Manipulation"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = ("CON", "units", 0.333)
        self.frequency = ("CON", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_wate_manipulation"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        wait = self.object.Wate
        da_a = math.ceil(self.object.PSTR * 0.75)  # mix of 1/2 times 1.5
        movit = math.ceil(self.object.Move * 1.25)
        description =  f"Shrink to {math.ceil(wait * .666)} kgs, and Move = {movit} h/u. Enlarge to {wait * 3} kgs, and Strike Force = {da_a} HPS."
        super().add_mutation(self.name, perm, description) # check to add
        return description


class Wings(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Wings"
        self.kind = "combat"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "As Needed"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_wings"

    def build_desc(self) -> str:
        '''returns mutation description and side effect via add_mutation()'''
        perm = super().return_perm(self.name, self.table_name) # perm part
        move_rate = self.object.Move if self.object.Move > 8 else 8
        if self.object.FAMILY_TYPE == "Avarian":
            move_rate *= 2

        description =  f"Big wings for flying at {move_rate} h/u."
        super().add_mutation(self.name, perm, description) # check to add
        return description


#######################################
#
# mutation support functions
#
#######################################

def biologic_mutations_number(mutation_number: table.PersonaRecord) -> int:
    '''returns the number of mental and physical mutations for anthros and aliens'''

    ## anthros get mutations 
    if mutation_number.FAMILY == "Anthro":

        ## determine chances of mental and physical mutations
        anthro_type = mutation_number.FAMILY_TYPE
        mentchance = table.anthro_type_mutation_chance[anthro_type]["mentchance"]
        physchance = table.anthro_type_mutation_chance[anthro_type]["physchance"]

        if not mutation_number.Fallthrough:
            if please.say_yes_to("Do you want to mutate? "):
                mentchance = mentchance * 2 if anthro_type != "Humanoid" else 100
                physchance = physchance * 2 if anthro_type != "Humanoid" else 100

        ## assign amount of mutations then zero if not change
        mental_amount = please.roll_this(table.anthro_type_mutation_chance[anthro_type]["mentnumber"])
        physical_amount = please.roll_this(table.anthro_type_mutation_chance[anthro_type]["physnumber"])       

        if not please.do_1d100_check(mentchance):
            mental_amount = 0
        if not please.do_1d100_check(physchance):
            physical_amount =  0 

    ## aliens get powers 
    if mutation_number.FAMILY == "Alien":
        mental_amount = 0
        while please.do_1d100_check(mutation_number.MSTR):
            mental_amount += 1

        physical_amount = 0
        while please.do_1d100_check(mutation_number.CON):
            physical_amount += 1

    return mental_amount, physical_amount

def mutation_assignment(mutating_persona: table.PersonaRecord, mental_amount: int = 0, physical_amount: int = 0, allowed:str = "any") -> table.PersonaRecord:
    """
    adjust PersonaRecord.Mutations to add mutations
    """
    mutation_tables = [mental_mutation_random, physical_mutation_random]
    amount_tuple = (mental_amount, physical_amount)
    directions_to_allowed = {
        "any": ['combat','non-combat','defect'],
        "combat":['combat'],
        "non-combat":['non-combat'],
        "no-defect":['combat','non-combat'],
        "defect":["defect"]
    }

    ##### all  Mutation generation
    counter_number_added = 1
    counter_total_amount = mental_amount + physical_amount
    
    for table_to_use in mutation_tables:
        number_added = 0
        while number_added < amount_tuple[mutation_tables.index(table_to_use)]: 
            kind_allowed = directions_to_allowed[allowed]
            mutation_tuple = please.get_table_result(table_to_use)
            working_mutation = mutation_tuple[1](mutating_persona) # todo this SHOULD  activate record changes the mutation subclass
            working_name = working_mutation.__dict__["name"]
            working_kind = working_mutation.__dict__["kind"]

            if working_kind not in kind_allowed:
                print("this kind not allowed")
                continue

            if working_name in mutating_persona.Mutations:
                print("repeats not allowed")
                continue

            pre_add_length = len(mutating_persona.Mutations.keys()) # length pre possible add

            print(f'\nMUTATION {counter_number_added}/{counter_total_amount}:', end="")
            working_mutation.build_desc()
        
            if pre_add_length < len(mutating_persona.Mutations.keys()) and working_kind != "defect":
                number_added +=1
                counter_number_added += 1

    return mutating_persona # modified by side effect in mutations method add_mutation


def mutation_list_builder(directions:list = ['any']) -> list:
    '''returns a bespoke list of tuples  *val cannot have a default value'''
    ALLOWED_LIST = ['any', 'mental', 'physical','combat','non-combat','defect', 'no-defect']
    fake_record = table.PersonaRecord
    build_mutations = []

    # todo this may be redundant now that list is built
    ## input safety checking
    if not directions:
        directions = ['any']
    elif len(directions) == 1 or not any(item in directions for item in ['any','mental','physical']):
        directions.append('any') 
    else:
        for element in directions:
            if element not in ALLOWED_LIST:
                input(f'{element} is not allowed. Please select from:\n{ALLOWED_LIST}. [Ret -> continue]')
                mutation_list_builder(['any'])
    

    mental_list = [val for val in mental_mutation_random.values() if isinstance(val,tuple)]
    physical_list = [val for val in physical_mutation_random.values() if isinstance(val,tuple)]

    ### build_mutations is a list of desired mutations mental, physical or both
    if 'mental' in directions:
        build_mutations = sorted(mental_list)
    elif 'physical' in directions:
        build_mutations = sorted(physical_list)
    elif 'any' in directions:
        build_mutations = sorted(mental_list + physical_list)

    ## if only containing any, mental or physical and not effects return all as is
    if len(directions) == 1:
        return build_mutations
    
    ## if only defects of any, mental, physical ready to return
    if 'defect' in directions:
        return [mutuple for mutuple in build_mutations if mutuple[1](fake_record).__dict__["kind"] == 'defect']

    ### if no-defect then strips build of but not ready for return
    if 'no-defect' in directions:
        build_mutations = [mutuple for mutuple in build_mutations if mutuple[1](fake_record).__dict__["kind"] != 'defect']

    elif 'combat' in directions:
        build_mutations = [mutuple for mutuple in build_mutations if mutuple[1](fake_record).__dict__["kind"] == 'combat']

    elif 'non-combat' in directions:
        build_mutations = [mutuple for mutuple in build_mutations if mutuple[1](fake_record).__dict__["kind"] == 'non-combat']

    if not build_mutations:
        print('you eliminated all mutations')
        return ["you eliminated all mutations"]

    return build_mutations

def single_random_mutation(random_mutating:table.PersonaRecord, directions:list =['any']) -> table.PersonaRecord:
    """
    return or add a mutation ['any', 'mental', 'physical','combat','non-combat','defect', 'no-defect']
    """
    mutuple_list = mutation_list_builder(directions)
    mutuple = secrets.choice(mutuple_list)
    working_mutation = mutuple[1](random_mutating)
    working_mutation.build_desc()

    return random_mutating # adjusted by side effect  in build_desc


def pick_bespoke_mutation(bespoke_mutating:table.PersonaRecord) -> table.PersonaRecord:
    '''choose specific mutations from chosen list and add to persona'''
    
    ALLOWED_LIST = ['any', 'mental', 'physical','combat','non-combat','defect', 'no-defect']

    build_directions = []
    chosen = ""
    ALLOWED_LIST.insert(0, "EXIT")
    while chosen!= "EXIT":
        chosen = please.choose_this(ALLOWED_LIST, "Choose mutation kinds. ")
        if chosen == "EXIT":
            break
        build_directions.append(chosen)

    if not build_directions:
        build_directions = "any"


    mutuples_list = mutation_list_builder(build_directions)
    mutation_choices = [name[0] for name in mutuples_list]

    mutation_name = ""
    mutation_choices.insert(0, "EXIT")
    while mutation_name != "EXIT":
        mutation_name = please.choose_this(mutation_choices, "Pick the mutation.")
        if mutation_name == "EXIT":
            break
        mutuple = next((t for t in mutuples_list if t[0] == mutation_name), None)
        working_mutation = mutuple[1](bespoke_mutating)
        working_mutation.build_desc()

    return bespoke_mutating # altered by side effects in .build_desc func


mental_mutation_random = {
    (1, 3):('Absorption', Absorption),
    (4, 4):('Alternate Banishment', AlternateBanishment),
    (5, 6):('Alien Attachment', AlienAttachment),
    (7, 8):('Calculations', Calculations),
    (9, 10):('Communicate', Communicate),
    (11, 11):('Cryokinesis', Cryokinesis),
    (12, 12):('Death Field Generation', DeathFieldGeneration),
    (13, 13):('Density Control', DensityControl),
    (14, 15):('Detections', Detections),
    (16, 17):('Directional Sense', DirectionalSense),
    (18, 18):('Empathy', Empathy),
    (19, 20):('Energy Attraction', EnergyAttraction),
    (21, 21):('Seizure Projection', SeizureProjection),
    (22, 22):('Extra Sensory Projection', ExtraSensoryProjection),
    (23, 23):('Force Field Generation', ForceFieldGeneration),
    (24, 24):('Gyrokinesis', Gyrokinesis),
    (25, 26):('Heightened Brain Talent', HeightenedBrainTalent),
    (27, 28):('Hostility Field', HostilityField),
    (29, 29):('Illusion Generation', IllusionGeneration),
    (30, 31):('Information Eradication', InformationEradication),
    (32, 33):('Intuition', Intuition),
    (34, 35):('Knowledge Transmission', KnowledgeTransmission),
    (36, 36):('Levitation', Levitation),
    (37, 37):('Life Leech', LifeLeech),
    (38, 38):('Light Wave Manipulation', LightWaveManipulation),
    (39, 40):('Magnetic Control', MagneticControl),
    (41, 41):('Mass Mind', MassMind),
    (42, 43):('Mechanical Sense', MechanicalSense),
    (44, 44):('Mental Blast', MentalBlast),
    (45, 45):('Mental Control', MentalControl),
    (46, 46):('Mental Physiostasis', MentalPhysiostasis),
    (47, 48):('Mental Defenselessness', MentalDefenselessness),
    (49, 49):('Molecular Disruption', MolecularDisruption),
    (50, 51):('Molecular Examination', MolecularExamination),
    (52, 52):('Molecular Phase Transformation', MolecularPhaseTransformation),
    (53, 53):('Molecular Phase Transmutation', MolecularPhaseTransmutation),
    (54, 54):('Muscle Manipulation', MuscleManipulation),
    (55, 55):('Neuronegation', Neuronegation),
    (56, 56):('Phase', Phase),
    (57, 58):('Planal Hide Away', PlanalHideAway),
    (59, 60):('Planal Hold Away', PlanalHoldAway),
    (61, 62):('Polar Disruption', PolarDisruption),
    (63, 64):('Power Drain', PowerDrain),
    (65, 66):('Precognition', Precognition),
    (67, 67):('Projected Sense', ProjectedSense),
    (68, 68):('Protection Shell', ProtectionShell),
    (69, 69):('Psionic Defence', PsionicDefence),
    (70, 70):('Purify', Purify),
    (71, 72):('Pyrokinesis', Pyrokinesis),
    (73, 74):('Repulsion Field Generation', RepulsionFieldGeneration),
    (75, 76):('Restoration', Restoration),
    (77, 78):('Sensory Deprivation', SensoryDeprivation),
    (79, 79):('Sociability Field Generation', SociabilityFieldGeneration),
    (80, 81):('Sonar', Sonar),
    (82, 82):('Sonic Attack', SonicAttack),
    (83, 84):('Sonic Reproduction', SonicReproduction),
    (85, 85):('Suggestion', Suggestion),
    (86, 86):('Telekinesis', Telekinesis),
    (87, 87):('Telekinetic Arm', TelekineticArm),
    (88, 88):('Telekinetic Flight', TelekineticFlight),
    (89, 89):('Telempathy', Telempathy),
    (90, 90):('Teleport', Teleport),
    (91, 91):('Thought Imitation', ThoughtImitation),
    (92, 92):('Time Stop', TimeStop),
    (93, 94):('Time Tell', TimeTell),
    (95, 95):('Total Recuperation', TotalRecuperation),
    (96, 96):('Ventriloquism', Ventriloquism),
    (97, 98):('Weapon Discharging', WeaponDischarging),
    (99, 100):('Weather Tell', WeatherTell),
    "name": "Mental Mutations",
    "die_roll": "1d100",
} 
 
physical_mutation_random = {
    (1, 3):('Acidic Enzymes', AcidicEnzymes),
    (4, 4):('Adaptation', Adaptation),
    (5, 7):('Attraction Odor', AttractionOdor),
    (8, 9):('Arms', Arms),
    (10, 10):('Body Structure Change', BodyStructureChange),
    (11, 12):('Carapace', Carapace),
    (13, 14):('Chameleon', Chameleon),
    (15, 16):('Decoy', Decoy),
    (17, 18):('Density Manipulation', DensityManipulation),
    (19, 20):('Diminished Sense', DiminishedSense),
    (21, 22):('Double Physical Pain', DoublePhysicalPain),
    (23, 24):('Edible Tissue', EdibleTissue),
    (25, 25):('Electric Shock', ElectricShock),
    (26, 26):('Enthalpy Attack', EnthalpyAttack),
    (27, 28):('Fat Cell Accumulation', FatCellAccumulation),
    (29, 29):('Haste', Haste),
    (30, 30):('Gas Generation', GasGeneration),
    (31, 32):('Heat Generation', HeatGeneration),
    (33, 36):('Heightened Attribute', HeightenedAttribute),
    (37, 38):('Heightened Vision', HeightenedVision),
    (39, 40):('Increased Metabolism', IncreasedMetabolism),
    (41, 42):('Launchable Quills', LaunchableQuills),
    (43, 44):('Light Generation', LightGeneration),
    (45, 45):('Mechanical Insertion', MechanicalInsertion),
    (46, 47):('Mechanical Prosthesis', MechanicalProsthesis),
    (48, 48):('Mitosis', Mitosis),
    (49, 50):('Multiple Body Parts', MultipleBodyParts),
    (51, 51):('New Organ', NewOrgan),
    (52, 52):('Non Breathing', NonBreathing),
    (53, 54):('No Resistance To Disease', NoResistanceToDisease),
    (55, 56):('No Resistance To Poison', NoResistanceToPoison),
    (57, 57):('Oversized Body Part', OversizedBodyPart),
    (58, 58):('Photosynthetic Skin', PhotosyntheticSkin),
    (59, 61):('Phosphorescent Skin', PhosphorescentSkin),
    (62, 64):('Pockets', Pockets),
    (65, 66):('Pressurized Body', PressurizedBody),
    (67, 68):('Radiating Eyes', RadiatingEyes),
    (69, 70):('Regeneration', Regeneration),
    (71, 72):('Rubbery Skin', RubberySkin),
    (73, 74):('Rust', Rust),
    (75, 75):('Self Destruction', SelfDestruction),
    (76, 76):('Shape Change', ShapeChange),
    (77, 77):('Size Manipulation', SizeManipulation),
    (78, 78):('Skin Structure Change', SkinStructureChange),
    (79, 79):('Smoke Screen', SmokeScreen),
    (80, 80):('Sonar Attack', SonarAttack),
    (81, 81):('Spit Poison', SpitPoison),
    (82, 83):('Static Quills', StaticQuills),
    (84, 85):('Strange New Body Part', StrangeNewBodyPart),
    (86, 86):('Symbiotic Attachment', SymbioticAttachment),
    (87, 87):('Tear Away Body Part', TearAwayBodyPart),
    (88, 90):('Undersized Body Part', UndersizedBodyPart),
    (91, 93):('Vibrations', Vibrations),
    (95, 96):('Wate Manipulation', WateManipulation),
    (97, 100):('Wings', Wings),
    "name": "Physical Mutations",
    "die_roll": "1d100",
} 
