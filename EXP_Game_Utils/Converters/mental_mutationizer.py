import please
import random
import math
import table
from mental_mutation import *


"""
mutationizer will now return one mutation that matches the type
the calling function will determine the number of times
formatting is the responsibility of the calling function

kind needs four types 
1)combat 
2)non-combat 
3)defect
4)!defect (no defect)
5)any (any kind)

This will be rolled into mental_mutation, 
leaving this as a testing function

RECALL RESETING OF mental_mutation_list to 1d8

"""


def mental(object, kind):
    
    # using shrunken mental mutation list table
    mutation_details = please.get_table_result(table.mental_mutation_random)(object)
    
    mutation_kind = mutation_details[0]["kind"]
    
    if kind == "Any":
        return  mutation_details
    
    elif kind == "!defect" and mutation_kind == "defect":
        return mental(object, kind)
        
    elif (mutation_kind == kind) or (kind == "!defect" and mutation_kind != "defect"):
        return  mutation_details  
    
    elif mutation_kind != kind:
        return mental(object, kind)
        
    return  mutation_details



