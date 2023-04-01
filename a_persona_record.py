"""
This is the main for a collection of python programs that create personas for EXP
EXP The game of technological chaos is a table top role playing game.
This package creates persona records for players and referees. 
The persona records are stored as <mangled> JSON, can be updated and printed out as PDFs
Yet to come: full robots, TOYs and isolated mutations. 
exp.sciencyfiction.com
"""

import alien
import anthropomorph
import mutations
import please
import robot
import toy

def record_chooser():
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
            "Anthro": anthropomorph.anthro_generator_selector,
            "Alien": alien.alien_generator_selector,
            "Robot": robot.robot_generator_selector,
            "Toy": toy.toy_generator_selector,
            "Mutation": mutations.mutation_generation_selector,
            "Maintenance": please.do_referee_maintenance,
            "Quit": please.say_goodnight_marsha,
        }

        choices_comment = "What do you want to do? "
        choices = list(choices_function_map.keys())
        record_type_desired = please.choose_this(choices, choices_comment)

        if record_type_desired in choices_function_map:
            choices_function_map[record_type_desired]()


def main():
    # Introduction
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
