import a_persona_record
import please
import exp_tables

from secrets import choice
from dataclasses import dataclass, field

@dataclass
class ToyRecord:
    FAMILY: str = "Toy"
    FAMILY_TYPE: str = "unmade"
    FAMILY_SUB: str = "unmade"
    Perms: dict = field(default_factory=dict)
    Vocation: str = "Toy"
    Date_Created: str = "Unmade"
    Date_Updated: str = "Unmade"
    File_Name: str = "None"
    Bin: bool = False


def toy_workflow() -> None:
    """
    Got toys?
    """

    # clearance for Clarence
    please.clear_console()

    toy_workflow_map = {
        "Fresh Toy":fresh_toy, 
        "Bespoke Toy":bespoke_toy,
        }

    list_comment = "Choose a TOY workflow:"
    option_list = list(toy_workflow_map.keys())
    plan_desired = please.choose_this(option_list, list_comment)

    if plan_desired in toy_workflow_map:
        toy_workflow_map[plan_desired]()

def toy_category():
    return please.get_table_result(exp_tables.toy_categories)

def toy_cat_type(toy_type: str = "any") -> str:
    ''' return str place holders for toys'''
    
    if "any" in toy_type:
        toy_type = please.get_table_result(exp_tables.toy_categories)

    return  please.get_table_result(exp_tables.toy_pivot[toy_type])

def fresh_toy() -> None:
    '''prints out toys till you get tired'''

    toy = ToyRecord()
    give_me_more = True

    while give_me_more:
        toy_cat = please.get_table_result(exp_tables.toy_categories)
        toy_type = toy_cat_type(toy_cat)

        toy.FAMILY_TYPE = toy_cat
        toy.FAMILY_SUB = toy_type
    
        shaped = please.get_table_result(exp_tables.base_shape)
        shaped = shaped if shaped != "Descriptive" else please.get_table_result(exp_tables.descriptive_shapes)
        # mangle shape?
        shaped = shaped if please.do_1d100_check(40) else f'{please.get_table_result(exp_tables.shape_mangle)} {shaped}'

        toy.Perms["Desc"] = f'{please.get_table_result(exp_tables.colour_bomb)} and {please.get_table_result(exp_tables.colour_bomb).lower()} {shaped}'


        if not please.say_yes_to(f'{toy_cat}: {toy_type} ({toy.Perms["Desc"]}). Give me another!'):
            a_persona_record.record_chooser()


    return

def bespoke_toy() -> None:
    ''' 
    choose a toy department from Catalogue
    '''

    toy = ToyRecord()
    give_me_more = True

    while give_me_more:
        toy_cat = please.choose_this(please.list_table_choices(exp_tables.toy_categories), "Please choose a toy department")

        if please.say_yes_to(f'Random choice from {toy_cat}?'):
            toy_type = toy_cat_type(toy_cat)

        else:
            toy_list = please.list_table_choices(exp_tables.toy_pivot[toy_cat])
            toy_type = please.choose_this(toy_list, f'Please choose from {toy_cat}?')

        toy.FAMILY_TYPE = toy_cat
        toy.FAMILY_SUB = toy_type
    
        shaped = please.get_table_result(exp_tables.base_shape)
        shaped = shaped if shaped != "Descriptive" else please.get_table_result(exp_tables.descriptive_shapes)
        # mangle shape?
        shaped = shaped if please.do_1d100_check(40) else f'{please.get_table_result(exp_tables.shape_mangle)} {shaped}'

        toy.Perms["Desc"] = f'{please.get_table_result(exp_tables.colour_bomb)} and {please.get_table_result(exp_tables.colour_bomb).lower()} {shaped}'


        if not please.say_yes_to(f'{toy_cat}: {toy_type} ({toy.Perms["Desc"]}). Give me another!'):
            a_persona_record.record_chooser()

    return



