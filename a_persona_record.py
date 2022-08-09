import os

import please
import anthropomorph
import alien
import robot
import toy
import mutations
import table


def record_chooser():
    """
    get player name, and choose record type
    wipe old object,
    direct to record type
    """

    record_type_desired = ""
    while record_type_desired != "Quit":
        # clearance for Clarence
        os.system("cls")

        choices = [
            "Anthro",
            "Alien",
            "Robot",
            "Toy",
            "Mutation",
            "Maintenance",
            "Quit",
        ]

        choices_comment = "What do you want to do? "
        record_type_desired = please.choose_this(choices, choices_comment)

        if record_type_desired == "Anthro":
            anthropomorph.anthro_generator_selector()
        elif record_type_desired == "Alien":
            alien.alien_generator_selector()
        elif record_type_desired == "Robot":
            robot.robot_generator_selector()
        elif record_type_desired == "Toy":
            toy.toy_generator_selector()
        elif record_type_desired == "Mutation":
            mutations.mutation_generation_selector()
        elif record_type_desired == "Maintenance":
            #object = table.PersonaRecord()
            please.do_referee_maintenance()

        else:
            please.say_goodnight_marsha()


if __name__ == "__main__":
    # introduction
    # clearance for Clarence
    os.system("cls")
    print("\nWelcome to the record generator for EXP GAME.")
    print("Decreasing crunchiness and increasing fun.")
    print("For all your persona, toy, and mutation needs.")

    if please.say_yes_to("Do you wish to continue..."):
        record_chooser()
    else:
        print()
        print("".center(31, "*"))
        print("* Thank you for your service. *")
        print("".center(31, "*"))
        print()
        quit()
        
