import a_persona_record
import please
import table


def toy_workflow() -> None:
    """
    Got toys?
    """

    # clearance for Clarence
    please.clear_console()

    toy_workflow_map = {
        "Fresh Toy":fresh_toy, 
        "Bespoke Toy":fresh_toy,
        "Maintenance":please.do_referee_maintenance, 
        }

    list_comment = "Choose a TOY workflow:"
    option_list = list(toy_workflow_map.keys())
    plan_desired = please.choose_this(option_list, list_comment)

    if plan_desired in toy_workflow_map:
        toy_workflow_map[plan_desired]()

def toy_category():
    return please.get_table_result(table.toy_categories)

def gimme_one(toy_type: str = "any") -> str:
    ''' return str place holders for toys'''
    
    if "any" in toy_type:
        toy_type = please.get_table_result(table.toy_categories)

    return  please.get_table_result(table.toy_pivot[toy_type])



def fresh_toy() -> None:
    '''prints out toys till you get tired'''

    give_me_more = True
    while give_me_more:
        toy_cat = please.get_table_result(table.toy_categories)
        toy_type = gimme_one(toy_cat)

        if please.say_yes_to(f'{toy_cat}: {toy_type}. Stop here?'):
            give_me_more = False

    return


def bespoke_toy():
   pass
