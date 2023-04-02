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
        "Back":a_persona_record.record_chooser
        }

    list_comment = "Choose a TOY workflow:"
    option_list = list(toy_workflow_map.keys())
    plan_desired = please.choose_this(option_list, list_comment)

    if plan_desired in toy_workflow_map:
        toy_workflow_map[plan_desired]()

def toy_category():
    return please.get_table_result(table.toy_categories)

def fresh_toy():
    toy_cat = toy_category()
    print(f"{toy_cat}")
    input("hit return to continue...")

    return


def bespoke_toy():
    fresh_toy()
    return
