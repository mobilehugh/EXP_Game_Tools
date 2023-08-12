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
        "Maintenance":fresh_toy, 
        }

    list_comment = "Choose a TOY workflow:"
    option_list = list(toy_workflow_map.keys())
    plan_desired = please.choose_this(option_list, list_comment)

    if plan_desired in toy_workflow_map:
        toy_workflow_map[plan_desired]()

def toy_category():
    return please.get_table_result(table.toy_categories)



def gimme_one(toy_type: str) -> str:
    ''' return str place holders for toys'''
    if "Any" in toy_type:
        toy_type = please.get_table_result(table.toy_categories)

    if toy


def fresh_toy():
    toy_cat = toy_category()
    print(f"{toy_cat}")
    input("hit return to continue...")

    return


def bespoke_toy():
    fresh_toy()
    return
