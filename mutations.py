import math
import secrets

import a_persona_record
import please
import table


class Mutation:

    # methods that create output from the object


    # def __str__(self):
    #     return self.headline()

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
        return f"{self.calculate_parameter(self.distance)}  {self.calculate_parameter(self.frequency)}  {self.calculate_parameter(self.duration)}  {self.calculate_parameter(self.roll_bonus)}"

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
            return f"{self.param_pivot[self.parameter]}{self.parameter}"

        elif self.parameter is None:
            return ""

        elif isinstance(self.parameter, tuple):
            self.statribute, self.unit, self.divisor = self.parameter
            self.level_adjustment = (
                0 if self.statribute == "Level" else self.object.Level
            )  # corrects for level based parameters not doubling
            return f"{self.param_pivot[self.parameter]}{math.ceil((self.object.__dict__[self.statribute] + self.level_adjustment)/self.divisor)} {self.unit}"

        return

    # methods that regulate the object

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

    def add_mutation(self):
        # ultimately will manage FAMILY and TOY information
        if self.name not in self.object.Mutations and self.table_name is not None:
            self.perm = please.get_table_result(self.table_name)
        elif self.name not in self.object.Mutations and self.table_name is None:
            self.perm = None
        elif self.name in self.object.Mutations:
            self.perm = self.object.Mutations[self.name]

        self.object.Mutations[self.name] = self.perm
        return

    def show_mutation_data(self):
        print("\nWelcome to show_mutation_data")
        print(self.headline())
        tuple = self.return_details(self)
        print(tuple)
        
        
        
        
        
        
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


    def build_desc(self):
        self.perm = self.object.Mutations[self.name]
        self.hps_absorbed = self.object.HPM + self.object.Level * 3
        return f"Absorb {self.hps_absorbed} HPS from {self.perm} attacks."


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
        self.add_mutation()

    def build_desc(self):
        self.perm = self.object.Mutations[self.name]
        self.hps_absorbed = self.object.HPM + self.object.Level * 3
        return f"Absorb {self.hps_absorbed} HPS from {self.perm} attacks."

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
        self.add_mutation()

    def build_desc(self):
        self.wate_banished = math.ceil(self.object.Wate / 2 + self.object.Level * 5)
        return f"Banish up to {self.wate_banished} kg of target to an alternate dimension. Save vs MSTR."


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
        self.add_mutation()

    def build_desc(self):
        self.alien_wate = math.ceil(self.object.Wate / 2)
        self.alien_smart = math.ceil(self.object.INT / 3)
        self.alien_number = (
            self.calculate_parameter(self.frequency).split(":")[1].strip()
        )
        return f"Befriend up to {self.alien_number} at once. Max wate {self.alien_wate} Wate and max INT {self.alien_smart} each."


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
        self.add_mutation()

    def build_desc(self):
        return "Rapidly solve complex maths."


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
        self.add_mutation()

    def build_desc(self):
        self.learn_chance = (self.object.INT + self.object.Level) * 3
        self.lang_max = self.object.INT + self.object.Level
        return f"Understand languages. {self.learn_chance}% chance to learn, maximum {self.lang_max} languages."


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
        self.add_mutation()

    def build_desc(self):
        return "Brain freeze targets. 1d4, then 2d4, and so on each unit."


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
        self.add_mutation()

    def build_desc(self):
        self.desc = f"Drain all HPS in range and collapse. Spare {math.floor(self.object.Level/3)} persona(s)."


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
        self.add_mutation()

    def build_desc(self):
        return "Change a target's density."


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

        self.line_of_detections = "Detect: "
        for detects in range(math.ceil(self.object.AWE / 5)):
            self.line_of_detections += (
                f"{detects + 1 }) {please.get_table_result(self.table_name)} "
            )

        self.perm = self.line_of_detections
        if self.name not in self.object.Mutations:
            self.object.Mutations[self.name] = self.perm  # equivalent of add_mutation()

    def build_desc(self):
        return self.object.Mutations[self.name]


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
        self.add_mutation()

    def build_desc(self):
        return "Can always find their way."


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
        self.add_mutation()

    def build_desc(self):
        return "Listen in on organic persona emotions."


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
        self.add_mutation()

    def build_desc(self):
        return "Deadly energy redirects to mutant."


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
        self.roll_bonus = "None"
        None
        self.table_name = None
        self.link = "#_seizure_projection"

        self.add_mutation()

    def build_desc(self):
        return "Induce random muscle contractions on an organic target."


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
        None
        self.table_name = None
        self.link = "#_extra_sensory_projection"

        self.add_mutation()

    def build_desc(self):
        return "Listen in on the thoughts of nearby personas."


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
        None
        self.table_name = None
        self.link = "#_force_field_generation"

        self.add_mutation()

    def build_desc(self):
        self.ffabsorbs = 10 * (self.object.MSTR + self.object.Level)
        return f"Personal energy shield absorbs {self.ffabsorbs} HPS."


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
        None
        self.table_name = None
        self.link = "#_gyrokinesis"

        self.add_mutation()

    def build_desc(self):
        return "Force target to revolve against it's will."


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
        self.add_mutation()

    def build_desc(self):
        self.perm = (
            (90 + self.object.Level + self.object.INT)
            if (90 + self.object.Level + self.object.INT) < 100
            else 99
        )
        return f"{self.perm}% chance to figure something out. Cannot ruin story plots."


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

        self.add_mutation()

    def build_desc(self):
        return "Gives off hostile vibes."


class IllusionGeneration(Mutation):
    def __init__(self, object):
        self.is_mental = True
        self.object = object
        self.name = "Illusion Generation"
        self.kind = "non-combat"
        self.distance = ("MSTR", "per day", 5.0)
        self.duration = "Special"
        self.frequency = ("MSTR", "per day", 4.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_illusion_generation"
        self.add_mutation()

    def build_desc(self):
        return "Place hallucinations into organic targets."


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

        self.add_mutation()

    def build_desc(self):
        return "Force target to forget specific memories."


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

        self.add_mutation()

    def build_desc(self):
        return "Get a yes/no answer to an imminent question."


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

        self.add_mutation()

    def build_desc(self):
        return "Walking organic thumb drive."


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

        self.add_mutation()

    # does not work for robots or aliens.
    def build_desc(self):

        if self.object.FAMILY == "Anthro":
            dexmove = self.object.Move
            mstrmove = table.anthro_movement_rate_and_DEX[self.object.MSTR]
            levimove = (dexmove if dexmove > mstrmove else mstrmove) * 2

        else:
            levimove = self.object.Move

        return f"Fly up or down at {levimove} h/u."


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
        self.add_mutation()

    def build_desc(self):
        self.amount = self.object.Level + 5
        self.well = self.object.HPM * 2
        return f"Drain {self.amount} HPS per unit. Max storage is {self.well} HPS. "


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

        self.add_mutation()

    def build_desc(self):
        return "Manipulate the light around oneself."


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

        self.add_mutation()

    def build_desc(self):
        return "Become a walking metallic magnet."


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

        self.add_mutation()

    def build_desc(self):
        return "Amplify, combine or deflect psionic attacks."


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
        self.add_mutation()

    # organic mechanical sense is not possible
    # recommendation is to split into two mutations
    # one for organic and one for mechanical

    def build_desc(self):
        chance_talk = (self.object.MSTR + self.object.Level) * 3
        return f"Talk with machines {chance_talk}% of the time. Also 2nd level mechanic"


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
        self.add_mutation()

    def build_desc(self):
        return f"Psionic blast for 2d4+{self.object.Level} HPS damage."


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
        self.add_mutation()

    def build_desc(self):
        return (
            f"Control the minds of targets. Total INT of targets is {self.object.INT}."
        )


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

        self.add_mutation()

    def build_desc(self):
        return "Optimized physiology 1/4 damage, 4 times benefit."


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

        self.add_mutation()

    def build_desc(self):
        return "MSTR vs mental attacks reduced to zero."


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
        self.add_mutation()

    def build_desc(self):
        disruptonnage = math.ceil(self.object.Wate / 2)
        return (
            f"Convert {disruptonnage} kgs matter in to cold gas. 1d20 per kg disrupted."
        )


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
        self.add_mutation()

    def build_desc(self):
        aware = self.object.AWE
        return f"Find weaknesses. MSTR save or {aware*10} attack roll and +{aware} on task rolls."


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

        self.add_mutation()

    def build_desc(self):
        return "Transform oneself between solid, liquid or gas."


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

        self.add_mutation()

    def build_desc(self):
        transmutograms = math.ceil(self.object.Wate / 2)
        return f"Transform {transmutograms} kgs of a target into gas, liquid or solid. 1d8 HPS per kg.\nDamage = change total transmutation."


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

        self.add_mutation()

    def build_desc(self):
        return "Manipulate the muscles of organic targets."


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

        self.add_mutation()

    def build_desc(self):
        return "Target's consciousness loses contact to all senses and collapses."


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

        self.add_mutation()

    def build_desc(self):
        carry = math.floor(self.object.WA / 4)
        furtherness = math.ceil(self.object.Move * 2)
        return f"Phase into hyperspace carrying {carry} kgs and moving {furtherness} hexes."


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

        self.add_mutation()

    def build_desc(self):
        return "Hide from physical space in your own temporal aberration."


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
        self.add_mutation()

    # this does no work for robots!!
    def build_desc(self):

        if self.object.FAMILY == "Anthro":
            pstrallowance = self.object.WA
            mstrallowance = table.wate_allowance_and_PSTR[self.object.MSTR]
            storage = math.ceil(
                (pstrallowance if pstrallowance > mstrallowance else mstrallowance) / 2
            )
        else:
            storage = math.ceil(self.object.WA / 2)

        return f"Carry {storage} kgs in your own space time aberration backpack."


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

        self.add_mutation()

    def build_desc(self):
        draw = math.floor(self.object.WA / 2)
        return f"Unexpectedly attract metallic objects <{draw} kgs toward mutant."


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
        self.add_mutation()

    def build_desc(self):
        return f"Drain batteries to heal 1d10 HPS. Recharge batteries for 1d12 HPS."


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

        self.add_mutation()

    def build_desc(self):
        return "Psionic pre-alert system prevents injury."


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

        self.add_mutation()

    def build_desc(self):
        return "Project a selected sense out of the body."


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
        self.add_mutation()

    def build_desc(self):
        self.perm = self.object.Mutations[self.name]
        return f"{self.perm} cannot come within {self.object.Level} hexes."


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

        self.add_mutation()

    def build_desc(self):
        return f"MSTR is {self.object.MSTR * 2} for defensive MSTR rolls."


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
        self.add_mutation()

    def build_desc(self):
        return f"Purify up to {math.ceil(self.object.WA / 10)} kgs of stuff ."


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

        self.add_mutation()

    def build_desc(self):
        return "Heat target for 1d4, 2d4, 3d4, etc HPS damage each unit."


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

        self.add_mutation()

    def build_desc(self):
        spares = math.floor(self.object.Level / 2)
        return f"Fell organics with nauseous incapacitation spare {spares} personas."


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
        self.add_mutation()

    def build_desc(self):
        return f"Heal organic targets for {self.object.HPM} HPS with a touch."


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

        self.add_mutation()

    def build_desc(self):
        return "Deny the target of a specific sense."


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

        self.add_mutation()

    def build_desc(self):
        return "People really really like you."


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

        self.add_mutation()

    def build_desc(self):
        return "Can replace normal vision with 360 degree sonar."


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

        self.add_mutation()

    def build_desc(self):
        distance = math.ceil(self.object.MSTR / 2)
        return f"Sound blast: 1h 4d8, {math.ceil(distance/2)}h 3d8, {distance}h 2d8"


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

        self.add_mutation()

    def build_desc(self):
        number = math.ceil(self.object.INT + self.object.Level)
        return f"Reproduce audio clips {number * 2} units long and a total of {number}"


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

        self.add_mutation()

    def build_desc(self):
        return "The more reasonable the more likely."


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

        self.add_mutation()

    def build_desc(self):
        speed = table.anthro_movement_rate_and_DEX[self.object.MSTR]
        amount = math.ceil(self.object.Wate / 2)
        return f"Move up to {amount} kgs at {speed} h/u with your mind."


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

        self.add_mutation()

    def build_desc(self):
        arm_wate = table.wate_allowance_and_PSTR[self.object.MSTR]
        return f"Invisible hand with {math.ceil(self.object.HPM/2)} HPS that can lift {arm_wate} kgs."


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

        self.add_mutation()

    def build_desc(self):
        speed = table.anthro_movement_rate_and_DEX[self.object.MSTR] * 3
        return f"Fly around at {speed} h/u."


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

        self.add_mutation()

    def build_desc(self):
        return "Push emotions into the target's mind."


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

        self.add_mutation()

    def build_desc(self):
        return "Instantly pop to familiar places."


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

        self.add_mutation()

    def build_desc(self):
        return "Flawlessly copy actions and mutations."


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
        self.add_mutation()

    def build_desc(self):
        lift = table.wate_allowance_and_PSTR[self.object.MSTR] * 10
        return f"Arrest the movement of time. Move freely and lift {lift} kgs."


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

        self.add_mutation()

    def build_desc(self):
        return "Atomic clock precision time telling."


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

        self.add_mutation()

    def build_desc(self):
        return f"Instantly restore back to {self.object.HPM} HPS."


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

        self.add_mutation()

    def build_desc(self):
        return "Make the voice appear to come from elsewhere."


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

        self.add_mutation()

    def build_desc(self):
        boom_boom = (
            (self.object.MSTR - self.object.Level)
            if (self.object.MSTR - self.object.Level) > 0
            else 1
        )
        boom_boom = math.ceil(boom_boom / 2)
        return f"A {boom_boom}% chance of accidental activation"


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

        self.add_mutation()

    def build_desc(self):
        return "Less accurate the further out."


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
        self.add_mutation()

    def build_desc(self):
        self.spit_damage = f"2d8+{self.object.Level}"
        return f"Spit acid (type B) every other unit {self.spit_damage} HPS damage."


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
        self.add_mutation()

    def build_desc(self):
        chancey_pants = self.object.CON + self.object.INT + self.object.Level
        perma_nerma = self.object.Level
        return f"A {chancey_pants}% of temporary immunity. {perma_nerma}% permanent. Max {perma_nerma} permanents."


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
        # self.add_mutation() removed for complex perm

        self.perm = please.get_table_result(self.table_name)
        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = self.perm
            # apply attribute changes
            if please.say_yes_to("Attraction Odor has a +2 CHA bonus APPLY it? "):
                self.object.CHA += 2

    def build_desc(self):
        return f"Constantly attracts {self.object.Mutations[self.name]}."


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
        self.attribute_bonus = ("DEX", -1)
        self.link = "#_arms"
        # self.add_mutation() removed for complex perm

        self.family_type = self.object.FAMILY
        self.table_name = table.family_hit_location_pivot_table[self.family_type]
        arm_carry = "Arm location(s):"
        dex_penalty = please.roll_this("1d4")

        for army in range(dex_penalty):
            arm_carry += f"{army+1}) {please.get_table_result(self.table_name)} "

        self.perm = arm_carry
        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = self.perm
            # apply attribute changes
            if please.say_yes_to(f"Arms has a -{dex_penalty} DEX penalty. APPLY it? "):
                self.object.DEX = self.object.DEX - dex_penalty

            self.object.Mutations[self.name] = self.perm  # equivalent of add_mutation()

    def build_desc(self):
        return self.object.Mutations[self.name]


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
        self.add_mutation()

    def build_desc(self):
        return "Change shape at will. "


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
        self.table_name = table.carapace_thickness
        self.link = "#_carapace"
        # self.add_mutation() removed for complex perm

        thickness = please.get_table_result(self.table_name)
        damage_reduction = (
            f'Reduce damage by {thickness["DA"]}'
            if thickness["DA"] != "1.0"
            else "No damage reduction."
        )
        self.perm = f'{thickness["covering"]} covering. {damage_reduction}'

        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = self.perm
            # apply attribute changes
            if please.say_yes_to(
                f'Carapace has an AR Bonus of +{str(thickness["AR"])}. APPLY it?'
            ):
                self.object.AR += thickness["AR"]
            if please.say_yes_to(
                f'Carapace has a DEX penalty of {str(thickness["dex_penalty"])}. APPLY it?'
            ):
                self.object.DEX += thickness["dex_penalty"]
            if please.say_yes_to(
                f'Carapace has a CHA penalty of {str(thickness["cha_penalty"])}. APPLY it?'
            ):
                self.object.CHA += thickness["cha_penalty"]

    def build_desc(self):
        desc = self.object.Mutations[self.name]
        return desc


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

        self.add_mutation()

    def build_desc(self):
        return "When naked and motionless blend into background."


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

        self.add_mutation()

    def build_desc(self):
        intensity = math.ceil(self.object.PSTR / 2)
        return f"Drop a fleshy decoy that attracts low INT targets. Poison intensity {intensity}."


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

        self.add_mutation()

    def build_desc(self):
        return "Change density to walk on a liquid or gas. "


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
        self.add_mutation()

    def build_desc(self):
        return f"Mutant has no {self.object.Mutations[self.name]}. Consult rule set for effects."


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

        self.add_mutation()

    def build_desc(self):
        return "Pain is doubled, add 2d8 HPS damage. Heal twice as fast."


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

        self.add_mutation()

    def build_desc(self):
        return "Thick fleshy strips feed the mutant for a day."


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
        self.add_mutation()

    def build_desc(self):
        electro_bump = self.object.Level
        return (
            f"Touch for 1d10+{6 + electro_bump} or shoot bolt for 3d4+{electro_bump}."
        )


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

        self.add_mutation()

    def build_desc(self):
        return f"Shoot a blast of cold and ice for 2d8+{self.object.Level}."


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
        self.table_name = table.family_hit_location_pivot_table
        self.link = "#_fat_cell_accumulation"

        self.family_type = self.object.FAMILY
        self.table_name = table.family_hit_location_pivot_table[self.family_type]
        blobcation = please.get_table_result(self.table_name)

        if self.name not in self.object.Mutations:
            self.object.Mutations[
                self.name
            ] = blobcation  # equivalent of add_mutation()

    def build_desc(self):
        return f"Big obvious blob of fat located on {self.object.Mutations[self.name]}"


class GasGeneration(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Gas Generation"
        self.kind = "combat"
        self.distance = "5 hex radius"
        self.duration = "1d4-1"
        self.frequency = ("CON", "per day", 5.0)
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = table.poison_gas_type
        self.link = "#_gas_generation"
        # self.add_mutation() removed for complex perm

        gas_belch = please.get_table_result(self.table_name)

        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = gas_belch  # equivalent of add_mutation()

    def build_desc(self):
        belcher = self.object.Mutations[self.name]
        return f"Intensity {math.ceil(self.object.CON/2) + self.object.Level} {belcher}"


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
        self.add_mutation()

    def build_desc(self):
        return f"Double speed of everything. Move at {self.object.Move * 2} h/u."


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

        self.add_mutation()

    def build_desc(self):
        return f"Shoot searing flame attack (C) for 3d6+{self.object.Level} HPS damage."


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
        # self.add_mutation() removed for complex perm

        self.perm = please.get_table_result(self.table_name)
        hattribute, __ = self.perm.split(":")
        old_attribute = getattr(self.object, hattribute)
        hattribute_bump = please.roll_this("2d8")

        # final heightened attribute cannot be less than 15 or 60 for HPM
        if hattribute in ["AWE", "CHA", "CON", "DEX", "INT", "PSTR"]:
            hattribute_bump = (
                hattribute_bump
                if (hattribute_bump + old_attribute) > 15
                else (15 - old_attribute)
            )

        elif hattribute == "HPM":
            hattribute_bump = math.ceil(old_attribute * (hattribute_bump / 10))
            hattribute_bump = (
                hattribute_bump
                if (hattribute_bump + old_attribute) > 60
                else (60 - old_attribute)
            )

        # Check to avoid repeats
        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = self.perm  # equivalent of add_mutation()
            if please.say_yes_to(
                f"Increase {hattribute} from {old_attribute} to {old_attribute + hattribute_bump}. APPLY it? "
            ):
                setattr(self.object, hattribute, old_attribute + hattribute_bump)

    def build_desc(self):
        return f"{self.object.Mutations[self.name]}"


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
        # self.add_mutation() removed for complex perm

        self.perm = please.get_table_result(self.table_name)

        # Check to avoid repeats
        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = self.perm  # equivalent of add_mutation()

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        some_thing_else = 42
        if some_thing == "Infravision: Thermal based see in the dark.":
            some_thing_else = f"Up to {self.object.AWE * 2} hexes."
        elif some_thing == "Semi Circular: 270 degree field of vision.":
            some_thing_else = f"AWE is {self.object.AWE * 2} vs ambush."
        elif some_thing == "Telescopic: Zoom in 10x. +100 on sniping attack rolls.":
            some_thing_else = (
                f"Up to {(self.object.AWE + self.object.Level)* 10} hexes."
            )
        elif some_thing == "X Ray: Penetrating and dangerous. +30 on x-ray rolls.":
            some_thing_else = (
                f"Up to {math.ceil((self.object.AWE + self.object.Level)/8)} hexes. "
            )
        else:
            some_thing_else = ""

        return f"{some_thing} {some_thing_else}"


class IncreasedMetabolism(Mutation):
    def __init__(self, object):
        self.is_mental = False
        self.object = object
        self.name = "Increased Metabolism"
        self.kind = "non-combat"
        self.distance = "Persona Only"
        self.duration = "Until Dead"
        self.frequency = "Constant"
        self.CR = "0"
        self.roll_bonus = None
        self.attribute_bonus = None
        self.table_name = None
        self.link = "#_increased_metabolism"

        self.add_mutation()

    def build_desc(self):
        return f"Burns twice the energy needs twice the food."


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
        # self.add_mutation() removed for complex perm

        quill_number = please.roll_this("2d8")
        poison = True if please.do_1d100_check(self.object.CON) else False

        if poison:
            self.perm = f"{quill_number} launchable (B) poisonous quills."
        else:
            self.perm = f"{quill_number} launchable (B) quills. 1d8 HPS per quill."

        # Check to avoid repeats
        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = self.perm  # equivalent of add_mutation()

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        some_thing_else = " "
        if "poisonous" in some_thing:
            some_thing_else = f"Intensity {self.object.CON}."

        return f"{some_thing} Hold back {self.object.Level} quill(s). {some_thing_else}"


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
        self.add_mutation()

    def build_desc(self):
        some_thing = self.object.CHA
        return f"Glow 1 hex. Flashlight {some_thing} hexes. Blinding flash intensity {some_thing}."


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
        self.table_name = table.family_hit_location_pivot_table
        self.link = "#_mechanical_insertion"
        # self.add_mutation() removed for complex perm

        self.family_type = self.object.FAMILY
        self.table_name = table.family_hit_location_pivot_table[self.family_type]
        toycation = please.get_table_result(self.table_name)

        cat_toy = please.get_table_result(table.mechanical_insertions)

        self.perm = f"{cat_toy} located in/on {toycation}."

        # Check to avoid repeats
        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = self.perm  # equivalent of add_mutation()

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        return f"{some_thing}"


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

        self.add_mutation()

    def build_desc(self):
        return f"Organs grow back. No aging. No ongoing damage."


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
        self.table_name = table.family_hit_location_pivot_table
        self.link = "#_mechanical_prosthesis"
        # self.add_mutation() removed for complex perm

        self.family_type = self.object.FAMILY
        self.table_name = table.family_hit_location_pivot_table[self.family_type]
        prosthesis = please.get_table_result(self.table_name)

        self.perm = f"{prosthesis} is replaced with a prosthesis."

        # Check to avoid repeats
        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = self.perm  # equivalent of add_mutation()

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        return f"{some_thing}"


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
        self.table_name = table.multiple_body_parts
        self.link = "#_multiple_body_parts"
        # self.add_mutation() removed for complex perm

        multi_part = please.get_table_result(self.table_name)

        if multi_part == "Arms":
            army = please.roll_this("1d4")
            self.perm = f"Mutant has {army} additional fully functional {multi_part}(s)"

        elif multi_part == "Ears":
            eary = please.roll_this("1d6")
            # ears 1, 3 , 5 work and increase AWE per ear and penalize CHA by 2
            # ears 2, 4, 6 are cosmetic
            if eary % 2 == 0:
                cha_bump = 0
                # only 2, 4 or 6 ears
                if eary == 2:
                    self.perm = f"Mutant has 2 extra ears. 1 functional and 1 cosmetic."
                    awe_bump = 1
                elif eary == 4:
                    self.perm = f"Mutant has 4 extra ears. 2 functional and 2 cosmetic."
                    awe_bump = 2
                elif eary == 6:
                    self.perm = f"Mutant has 6 extra ears. 3 functional and 3 cosmetic."
                    awe_bump = 3

            else:
                # only 1, 3, or 5 ears
                cha_bump = -2
                if eary == 1:
                    self.perm = f"Mutant has 1 extra functional ear."
                    awe_bump = 1
                elif eary == 3:
                    self.perm = f"Mutant has 3 extra ears. 2 functional and 1 cosmetic."
                    awe_bump = 2
                elif eary == 5:
                    self.perm = f"Mutant has 5 extra ears. 3 functional and 2 cosmetic."
                    awe_bump = 3

            if self.name not in self.object.Mutations:
                # check on attribute bumps
                if please.say_yes_to(
                    f"Multiple body parts {multi_part} has an AWE bump of {awe_bump}. APPLY it?"
                ):
                    self.object.AWE += awe_bump
                if please.say_yes_to(
                    f"Multiple body parts {multi_part} has a CHA penalty of {cha_bump}. APPLY it?"
                ):
                    self.object.CHA += cha_bump

        elif multi_part == "Eyes":
            eye_eye_captain = please.roll_this("1d6")
            # eyes 1, 3 , 5 work and increase AWE per eye and penalize CHA by 2
            # eyes 2, 4, 6 are cosmetic
            if eye_eye_captain % 2 == 0:
                # only 2, 4 or 6 eyes
                if eye_eye_captain == 2:
                    self.perm = f"Mutant has 2 extra eyes. 1 functional and 1 blind."
                    awe_bump = 1
                elif eye_eye_captain == 4:
                    self.perm = f"Mutant has 4 extra eyes. 2 functional and 2 blind."
                    awe_bump = 2
                elif eye_eye_captain == 6:
                    self.perm = f"Mutant has 6 extra eyes. 3 functional and 3 blind."
                    awe_bump = 3

            else:
                # only 1, 3, or 5 eyes
                cha_bump = -2
                if eye_eye_captain == 1:
                    self.perm = f"Mutant has 1 extra eye."
                    awe_bump = 1
                elif eye_eye_captain == 3:
                    self.perm = f"Mutant has 3 extra eyes. 2 functional and 1 blind."
                    awe_bump = 2
                elif eye_eye_captain == 5:
                    self.perm = f"Mutant has 5 extra eyes. 3 functional and 2 blind."
                    awe_bump = 3

            if self.name not in self.object.Mutations:
                # check on attribute bumps
                if please.say_yes_to(
                    f"Multiple body parts {multi_part} has an AWE bump of {awe_bump}. APPLY it?"
                ):
                    self.object.AWE += awe_bump

        elif multi_part == "Feet":
            best_feet_forward = please.roll_this("1d2+1")
            self.perm = f"Each leg has {best_feet_forward} feet. No impairments."

        elif multi_part == "Fingers":
            fisties = please.roll_this("1d3+5")
            self.perm = f"Each hand has {fisties} fingers. No impairments."

        elif multi_part == "Head":
            cha_bump = -4
            self.perm = f"Mutant has a semi-autonomous, unhidable extra head."
            if please.say_yes_to(
                f"Multiple body parts {multi_part} has a CHA penalty of {cha_bump}. APPLY it?"
            ):
                self.object.CHA += cha_bump

        elif multi_part == "Legs":
            move = self.object.Move
            leg_ups = please.roll_this("1d6")
            move_bump = math.ceil((1 + leg_ups / 10) * move)
            self.perm = f"Mutant has {leg_ups + 2} legs. No impairments."
            if please.say_yes_to(
                f"Multiple {multi_part} has a Move bump of {move} -> {move_bump}. APPLY it?"
            ):
                self.object.Move = move_bump

        elif multi_part == "Mouthes":
            mouthy = please.roll_this("1d4")
            self.perm = f"Mutant has {mouthy} extra semi-autonomous, drooling, speechless mouth(es)"
            if please.say_yes_to(
                f"Multiple body parts {multi_part} has a CHA penalty of {mouthy}. APPLY it?"
            ):
                self.object.CHA -= mouthy

        elif multi_part == "Noses":
            nosey_nellie = please.roll_this("1d8")
            self.perm = f"Mutant has {nosey_nellie} additional nose(s), and all associated hassles."

        else:
            print("Something went wrong with the multiple body part table")

        # Check to avoid repeats
        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = self.perm  # equivalent of add_mutation()

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        return f"{some_thing}"


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
        # self.add_mutation() removed for complex perm

        new_organ = please.get_table_result(self.table_name)

        if new_organ == "Light Tissue:" and please.do_1d100_check(20):
            new_organ = "Dark Tissue:"

        self.perm = new_organ

        # Check to avoid repeats
        if self.name not in self.object.Mutations:
            # replaces add_mutation() above
            self.object.Mutations[self.name] = self.perm  # equivalent of add_mutation()

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        some_thing_else = ""

        if some_thing == "Blood Draining Proboscis:":
            some_thing_else = f"Drains {self.object.Level}d6 HPS per unit."

        elif some_thing == "Electricity Storing Organ:":
            some_thing_else = f"Store {self.object.CON} cells. Zap for {self.object.Level}d8 HPS, 1 hex range."

        elif some_thing == "Ink Producing Gland: Endless writing.":
            some_thing_else = f"Squirting a cloud in water. \nBlinding ink for {math.ceil(self.object.CON/2)} intensity, 6 hex range, {math.ceil(self.object.CON/4)} per day."

        elif some_thing == "Light Tissue:":
            some_thing_else = f"{self.object.Level} hex radius of light."

        elif some_thing == "Dark Tissue:":
            some_thing_else = f"Absorbs light. {self.object.Level} hex radius of darkness. +20 sneaky rolls in dark."

        elif some_thing == "Kirlian Energy Absorptive Skull:":
            some_thing_else = f"MSTR = {(self.object.MSTR + self.object.Level) * 2} vs mental attacks."

        return f"{some_thing} {some_thing_else}"


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

        self.add_mutation()

    def build_desc(self):
        return f"Respiration without air or light."


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

        self.add_mutation()

    def build_desc(self):
        return f"CON is 1d4-1 versus disease rolls."


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

        self.add_mutation()

    def build_desc(self):
        return f"CON is 1d4-1 versus poison attacks."


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

        big_booty = please.get_table_result(table.oversized_body_part)

        self.perm = big_booty
        if self.name not in self.object.Mutations:
            self.object.Mutations[self.name] = self.perm

            # oversize_body_part has attribute bumps!
            if big_booty == "Arms":
                if please.say_yes_to("Oversized arms gives +2 PSTR. APPLY? "):
                    self.object.PSTR += 2

            elif big_booty == "Brain":
                if please.say_yes_to("Oversized brain gives +2 INT. APPLY? "):
                    self.object.INT += 2
                if please.say_yes_to("Oversized brain gives +2 MSTR. APPLY? "):
                    self.object.MSTR += 2

            elif big_booty == "Ears":
                if please.say_yes_to("Oversized ears gives +2 AWE. APPLY? "):
                    self.object.AWE += 2

            elif big_booty == "Eyes. See in darkness":
                if please.say_yes_to("Oversized eyes gives +1 AWE. APPLY? "):
                    self.object.AWE += 1

            elif big_booty == "Loins":
                if please.say_yes_to("Oversized loins gives +1 CON. APPLY? "):
                    self.object.CON += 1
                if please.say_yes_to("Oversized loins gives +1 CHA. APPLY? "):
                    self.object.CHA += 1

            elif big_booty == "Lungs":
                if please.say_yes_to("Oversized lungs gives +1 CON. APPLY? "):
                    self.object.CON += 1

            elif big_booty == "Heart":
                if please.say_yes_to("Oversized heart gives +2 CON. APPLY? "):
                    self.object.CON += 2

            elif big_booty == "Legs":
                if please.say_yes_to("Oversized legs gives +2 PSTR. APPLY? "):
                    self.object.PSTR += 2
                if please.say_yes_to("Oversized legs gives Move bonus. APPLY? "):
                    self.object.Move = math.ceil(self.object.Move * 1.5)

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        some_thing_else = ""

        if some_thing == "Ears":
            some_thing_else = f"AWE = {self.object.AWE * 2} for ambush."

        elif some_thing == "Lungs":
            some_thing_else = f"Hold breath for {self.object.CON} minutes."

        elif some_thing == "Nose: Super taster":
            some_thing_else = f"AWE = {self.object.AWE * 2} for ambush."

        return f"Obviously oversized {some_thing}. {some_thing_else}"


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

        if self.object.FAMILY == "Anthro" and self.object.FAMILY_TYPE== "Florian":
            self.perm = "Double healing rate for florian with photosynthetic skin"
        else:
            self.perm = "Respiration via photosynthesis. Hold breath indefinitely."

        if self.name not in self.object.Mutations:
            self.object.Mutations[self.name] = self.perm

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        return f"{some_thing}"


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
        self.add_mutation()

    def build_desc(self):
        return f"Glows continuously. Can't hide in the dark."


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
        self.add_mutation()

    def build_desc(self):
        some_thing = math.ceil(self.object.Wate * 0.05)
        return f"Create body pockets. Total storage wate is {some_thing} kgs."


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
        self.add_mutation()

    def build_desc(self):
        some_thing = self.object.Level + self.object.PSTR
        return f"Protect self from crushing attacks. Fall {some_thing} hexes no damage."


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
        self.add_mutation()

    def build_desc(self):
        return f"Obvious radiation beams attack at intensity 2d6+{self.object.Level}."


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
        self.add_mutation()

    def build_desc(self):
        base_heal = self.object.CON + self.object.Level
        return f"Heal {math.ceil(base_heal/5)} HPS per unit. Massive regen {math.ceil(base_heal/2)} HPS once a day"


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
        self.add_mutation()

    def build_desc(self):
        return f"Inorganic rubbery exterior layer. "


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
        self.add_mutation()

    def build_desc(self):
        return f"Instantaneous metallic oxidation. 10d10 vs robots."


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
        self.add_mutation()

    def build_desc(self):
        return f"Spontaneous violent combustion possible. {self.object.Level}d20 HPS damage."


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
        self.add_mutation()

    def build_desc(self):
        return f"Cosmetically change into any organic shape."


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
        self.add_mutation()

    def build_desc(self):
        two_sizes = self.object.Hite
        one_pstr = self.object.PSTR
        da_a = math.ceil((one_pstr / 2) * 1.5)
        da_b = math.ceil((one_pstr / 4) * 1.5)
        return f"Shrink to {math.floor(two_sizes * .25)} cms -> AR {self.object.AR + 75}. \nEnlarge to {math.ceil(two_sizes * 1.5)} cms -> DA-A {da_a} and DA-B {da_b}."


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

        skinny_dip = please.get_table_result(self.table_name)
        self.perm, ar_bump = skinny_dip[0], skinny_dip[1]

        if self.name not in self.object.Mutations:
            self.object.Mutations[self.name] = self.perm  # replaces self.add_mutation()

            if please.say_yes_to(
                f"{skinny_dip[0]} has an AR bump of {skinny_dip[1]} APPLY it?"
            ):
                self.object.AR += ar_bump

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        return f"{some_thing}"


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

        self.add_mutation()

    def build_desc(self):
        diameter = math.ceil((self.object.PSTR + self.object.Level) / 3)
        length = diameter * self.object.Move
        return f"Smoke cloud {diameter} hexes or smoke fence {length} hexes."


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

        self.add_mutation()

    def build_desc(self):
        distance = math.ceil(self.object.MSTR / 2)
        return f"Sound blast: 1h 4d8, {math.ceil(distance/2)}h 3d8, {distance}h 2d8"


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
        self.add_mutation()

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        return f"{some_thing} Intensity 1d8+{self.object.Level}"


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
        self.add_mutation()

        if self.name not in self.object.Mutations:
            if please.say_yes_to(f"Static quills boosts AR by 101. APPLY it?"):
                self.object.AR += 101

    def build_desc(self):
        return (
            f"Spines and quills hurt attackers. 1d6+{self.object.Level} HPS to punches."
        )


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

        stranger_things = please.get_table_result(self.table_name)
        self.perm = stranger_things

        if stranger_things == "Horns on head.":
            self.perm = f"{self.perm}  {please.roll_this('1d4')} pairs."

        # this does not reflect the random nature of EXP, should be random by random
        if stranger_things == "Fully articulate tentacles!":
            tenties = please.roll_this("1d4")
            if tenties == 1:
                self.perm = f"{self.perm} Left arm is a tentacle."
            elif tenties == 2:
                self.perm = f"{self.perm} Both arms are tentacles."
            elif tenties == 3:
                self.perm = f"{self.perm}  Both arms, left leg are tentacles."
            elif tenties == 4:
                self.perm = f"{self.perm}  Both arms, both legs are tentacles."
            else:
                print("ERROR: Strange New Body Part")

        if (
            stranger_things
            in ["Fins attached to arms, and legs.", "Gills for breathing underwater."]
            and self.object.FAMILY_TYPE== "Aquarian"
        ):
            if please.say_yes_to("Do you an aquarian to have fishy things REALLY? "):
                pass
            else:
                return

        if self.name not in self.object.Mutations:
            self.object.Mutations[self.name] = self.perm

            if stranger_things == "Turtle Shell that mutant can retract into.":
                if please.say_yes_to("Turtle shell increases AR to 777. APPLY this? "):
                    self.object.AR = 777

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        some_thing_else = ""

        if some_thing in [
            "Ears fold up and down accordion like.",
            "Eyes are concave reflectors.",
        ]:
            some_thing_else = f"AWE {2* self.object.AWE} vs ambush."
        elif some_thing == "Fins attached to arms, and legs.":
            some_thing_else = f"Swim at {self.object.Move} h/u."

        return f"{some_thing} {some_thing_else}"


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

        self.add_mutation()

    def build_desc(self):
        return f"Control target via nerve tentacle."


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

        self.add_mutation()

    def build_desc(self):
        return f"Tear off {self.object.Level} parts per day. Each has {math.ceil(self.object.HPM / 10)} HPS."


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

        self.add_mutation()

    def build_desc(self):
        some_thing = self.object.Mutations[self.name]
        return f"Obviously small {some_thing}. No deficits."


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

        self.add_mutation()

    def build_desc(self):
        return f"Soothing massage to Type A attack. 3d4+{self.object.Level} HPS damage. +97 on attack roll."


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

        self.add_mutation()

    def build_desc(self):
        wait = self.object.Wate
        da_a = math.ceil(self.object.PSTR * 0.75)  # mix of 1/2 times 1.5
        movit = math.ceil(self.object.Move * 1.25)
        return f"Drop to {math.ceil(wait * .666)} kgs -> move {movit} h/u. Increase to {wait * 3} kgs -> DA type A = {da_a} HPS."


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
        self.add_mutation()

    def build_desc(self):
        some_thing = self.object.Move if self.object.Move > 8 else 8
        return f"Big beautiful wings for flying at {some_thing} h/u."


def mutation_workflow():
    """
    Mutate now avoid the post bomb rush
    """

    # clearance for Clarence
    please.clear_console()

    option_list = ["Fresh Mutation", "Bespoke Mutation", "Back"]
    list_comment = "Please Choose:"
    plan_desired = please.choose_this(option_list, list_comment)

    if plan_desired == "Fresh Mutation":
        pass
    elif plan_desired == "Bespoke Mutation":
        pass
    elif plan_desired == "Maintenance":
        pass
    elif plan_desired == "Back":
        a_persona_record.record_chooser()
    else:
        # BuildSupport(object)
        print("Bad mutation methods were chosen some how")
    return



def list_all_mutations():
    mental_comprehension = {
        name[0]: name[1]
        for (lose, name) in table.mental_mutation_random.items()
        if lose != "name" and lose != "die_roll"
    }
    physical_comprehension = {
        name[0]: name[1]
        for (lose, name) in table.physical_mutation_random.items()
        if lose != "name" and lose != "die_roll"
    }
    return {**mental_comprehension, **physical_comprehension}


def single_random_mutation(object):
    """
    return a mutation of either type.
    """

    if hasattr(object, "Mutations"):
        pass
    else:
        object.Mutations = {}

    all_mutations = list_all_mutations()
    choice_list = list(all_mutations)
    mutation_chosen = secrets.choice(choice_list)

    if please.say_yes_to(f"Do you want to add {mutation_chosen.upper()}?"):
        working_mutation = all_mutations[mutation_chosen](object)
        print(working_mutation)

    else:
        print("Ok. Mutation skipped.")



    if please.say_yes_to("Do you want to add another mutation? "):
        single_random_mutation(object)
    else:
        pass

    return


def pick_bespoke_mutation(object):

    if hasattr(object, "Mutations"):
        pass
    else:
        object.Mutations = {}

    all_mutations = list_all_mutations()

    choice_list = sorted(list(all_mutations))
    choice_comment = "Here is a list of all mutations?"
    mutation_chosen = please.choose_this(choice_list, choice_comment)

    if please.say_yes_to(f"Do you want to add {mutation_chosen}? "):
        working_mutation = all_mutations[mutation_chosen](object)
        print(working_mutation)

    else:
        print("Ok. Mutation skipped.")

    if please.say_yes_to("Do you want to add another mutation? "):
        pick_bespoke_mutation(object)
    else:
        return
