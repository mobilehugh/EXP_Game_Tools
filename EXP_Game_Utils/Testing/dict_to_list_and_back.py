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
    "Anthro": anthropomorph.anthro_workflow,
    "Alien": alien.alien_workflow,
    "Robot": robot.robot_workflow,
    "Toy": toy.toy_workflow,
    "Mutation": mutations.mutation_workflow,
    "Maintenance": please.do_referee_maintenance,
    "Quit": please.say_goodnight_marsha,
}



choices = list(record_type_function_map.keys())


print(record_type_function_map, choices)
