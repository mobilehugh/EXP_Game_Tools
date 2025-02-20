"""
This is the main for a collection of python programs that create personas for EXP
EXP The game of technological chaos is a table top role playing game.
This package creates persona records for players and referees. 
The persona records are stored as <mangled> JSON, can be updated and printed out as PDFs
Yet to come: full robots, TOYs and isolated mutations. 
rules.expgame.com
"""

import  alien
import  anthro
import  mutations
import  robot 
import  toy 
import  please



def record_chooser()->None:
    """
    Interactively prompt the user to choose a record type, then generate the
    corresponding record using the appropriate module. The user can continue
    choosing record types until they decide to quit.
    """

    record_type_desired = ""
    while record_type_desired != "Quit":
        # clearance for Clarence
        please.clear_console()

        choices_function_map = {
            "Anthros": anthro.anthro_workflow,
            "Aliens": alien.alien_workflow,
            "Robots": robot.robot_workflow,
            "Toys": toy.toy_workflow,
            "Mutations": mutations.mutation_workflow,
            "Maintenance": please.maintenance_workflow,
        }

        choices_comment = "What are you exploring? "
        choices = list(choices_function_map.keys())
        record_type_desired = please.choose_this(choices, choices_comment)
        
        if record_type_desired in choices_function_map:
            choices_function_map[record_type_desired]()


def main() -> None:
    '''
    this is where is all starts
    '''
    please.clear_console()
    print("\nWelcome to the record generator for EXP The game of technological chaos.")
    print("Decreasing crunchiness and increasing fun.")
    print("For all your persona, toy, and mutation needs.")

    if please.say_yes_to("Do you wish to continue..."):
        record_chooser()
    else:
        please.say_goodnight_marsha()

if __name__ == "__main__":
    main()
