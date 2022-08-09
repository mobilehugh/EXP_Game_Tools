import math
import os

import a_persona_record
import please
import table


def toy_generator_selector() -> None:
    """
    Got toys?
    """

    # clearance for Clarence
    os.system("cls")

    option_list = ["Fresh Toy", "Bespoke Toy", "Maintenance", "Back"]
    list_comment = "Please Choose:"
    plan_desired = please.choose_this(option_list, list_comment)

    if plan_desired == "Fresh Toy":
        fresh_toy()
    elif plan_desired == "Bespoke Toy":
        bespoke_toy()
    elif plan_desired == "Maintenance":
        object = please.collect_required_records("Toys")
        please.do_toy_maintenance(object)
    elif plan_desired == "Back":
        a_persona_record.record_chooser()
    else:
        # BuildSupport(object)
        print("Bad toy methods were chosen some how")
    return


def toy_category():
    return please.get_table_result(table.toy_categories)


def fresh_toy():
    toy_cat = toy_category()
    print(f"{toy_cat}")
    input("hit return to continue...")

    return


def bespoke_toy():
    return
