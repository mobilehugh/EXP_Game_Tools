import sys
import secrets
import re
import os
import math

sys.path.insert(0, "C:\\Users\mobil\OneDrive\Documents\Persona Record\EXP_Game_Tools")
import table
from please import roll_this


###############################################################
# place only ONE function here
###############################################################
def get_table_result(table):
    """
    if table has special results like Choose, Extra Roll or Ref's Own Table
    must go through gate_keeper()  to avoid errors

    if repeats are not desired only type('str') can be the result
    """
    random = roll_this(table["die_roll"])

    # print("Random Roll", random, type(random))
    for key in table:
        # print(key, type(key), end="")
        # print(table[key], type(table[key]))
        if random in key:
            result = table[key]
            # print("The machine chose ", result)
            break

    return result




###############################################################
# set up for testing the ONE function
###############################################################

""" 
class Record:
    pass


object = Record()


anthro_attributes_fresh(object)
anthro_hit_points_fresh(object)
object.Level = 1
 """

anthro_snap_hit_location = {
    range(1, 2): "Leg, Left",
    range(2, 3): "Leg, Right",
    range(3, 4): "Groin/Butt",
    range(4, 6): "Stomach/Back",
    range(6, 7): "Arm, Left",
    range(7, 8): "Arm, Right",
    range(8, 10): "Chest/Back",
    range(10, 11): "Face/Head",
    "type": "Anthro Snap Hit Location",
    "die_roll": "1d10",
}

alien_snap_hit_location = {
    range(1, 2): "Legs, Left",
    range(2, 3): "Legs, Right",
    range(3, 5): "Torso, Back",
    range(5, 8): "Torso, Front",
    range(8, 9): "Arms, Left",
    range(9, 10): "Arms, Right",
    range(10, 11): "Head",
    "type": "Alien Snap Hit Location",
    "die_roll": "1d10",
}

robot_snap_hit_location = {
    range(1, 4): "Locomotion",
    range(4, 6): "Power Plant",
    range(6, 7): "Peripheral",
    range(7, 8): "Articulation",
    range(8, 9): "Control Unit",
    range(9, 10): "Sensors",
    range(10, 11): "Brain Case",
    "type": "Robot Snap Hit Location",
    "die_roll": "1d10",
}


print()
for __ in range(10):
    print(get_table_result(anthro_snap_hit_location))

print()
for __ in range(10):
    print(get_table_result(alien_snap_hit_location))

print()
for __ in range(10):
    print(get_table_result(robot_snap_hit_location))
    
    
    

