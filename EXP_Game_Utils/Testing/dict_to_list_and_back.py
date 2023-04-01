import os
import sys

# allowing access to modules in another folder
sys.path.append('../..')

import alien
import anthropomorph
import mutations
import please
import robot
import toy

record_type_function_map = {
    "Anthro": anthropomorph.anthro_generator_selector,
    "Alien": alien.alien_generator_selector,
    "Robot": robot.robot_generator_selector,
    "Toy": toy.toy_generator_selector,
    "Mutation": mutations.mutation_generation_selector,
    "Maintenance": please.do_referee_maintenance,
    "Quit": please.say_goodnight_marsha,
}



choices = list(record_type_function_map.keys())


print(record_type_function_map, choices)
