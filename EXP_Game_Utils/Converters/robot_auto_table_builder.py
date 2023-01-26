"""
this function builds a dictionary to automatically return a list of eligible robot types based on prime attributes

"""


def robot_type_selector(CON_Prime, DEX_Prime, INT_Prime, PSTR_Prime):
    # dictionary containing robot types per prime attribute
    Robotula_Selecta = {
        "con": ["DHIJMSTV", "CDIMSV", "PT", "ACEIR"],
        "dex": ["DHJST", "DEHIJMRS", "HIM", "ACPRTV"],
        "int": ["CEIJT", "IJMR", "CHMPRSTV", "ADEHMSTV"],
        "pstr": ["DHJMRSTV", "DJT", "EPR", "ACI"],
    }

    # dictionary for bot labels to names and freq chosen
    Robotula_Rasa = {
        "A": {"name": "Android", "score": 0},
        "C": {"name": "Combat", "score": 0},
        "D": {"name": "Datalyzer", "score": 0},
        "E": {"name": "Explorations", "score": 0},
        "H": {"name": "Hobbot", "score": 0},
        "I": {"name": "Industrial", "score": 0},
        "J": {"name": "Janitorial", "score": 0},
        "M": {"name": "Maintenance", "score": 0},
        "P": {"name": "Police", "score": 0},
        "R": {"name": "Rescue", "score": 0},
        "S": {"name": "Social", "score": 0},
        "T": {"name": "Transport", "score": 0},
        "V": {"name": "Veterinarian", "score": 0},
    }

    # prime attributes minus one to not offend lists
    con = CON_Prime - 1
    dex = DEX_Prime - 1
    intel = INT_Prime - 1
    pstr = PSTR_Prime - 1

    # reseting score needed for tester, may no longer be needed.
    for key in Robotula_Rasa:
        Robotula_Rasa[key]["score"] = 0

    # you could change this to a list of con, dex, int, and pstr.

    # SCORING FOR CON
    letter_set = Robotula_Selecta["con"][con]
    for x in range(len(letter_set)):
        Robotula_Rasa[letter_set[x]]["score"] += 1

    # SCORING FOR DEX
    letter_set = Robotula_Selecta["dex"][dex]
    for x in range(len(letter_set)):
        Robotula_Rasa[letter_set[x]]["score"] += 1

    # SCORING FOR INT
    letter_set = Robotula_Selecta["int"][intel]
    for x in range(len(letter_set)):
        Robotula_Rasa[letter_set[x]]["score"] += 1

    # SCORING FOR PSTR
    letter_set = Robotula_Selecta["pstr"][pstr]
    for x in range(len(letter_set)):
        Robotula_Rasa[letter_set[x]]["score"] += 1

    # makes a list of tuples using bot letter and score
    sortable = []
    for letter in Robotula_Rasa:
        sortable.append((letter, Robotula_Rasa[letter]["score"]))

    sortable = sorted(sortable, key=lambda tup: tup[1], reverse=True)

    # searches through sorted tuples for find frequency drop ie, 3,3,3,2
    for x in range(len(sortable)):
        if sortable[x][1] > sortable[x + 1][1]:
            # remember range is up to not including top +1 to avoid offending lists
            cutter = x + 1
            break

    # prepare choices for player to decide
    choices = []
    for x in range(cutter):
        choices.append(Robotula_Rasa[sortable[x][0]]["name"])
    # print(choices)

    return choices


iteration = 0
for CON_Prime in range(1, 5):
    for DEX_Prime in range(1, 5):
        for INT_Prime in range(1, 5):
            for PSTR_Prime in range(1, 5):
                iteration += 1
                options = robot_type_selector(
                    CON_Prime, DEX_Prime, INT_Prime, PSTR_Prime
                )
                print(f"'{CON_Prime}{DEX_Prime}{INT_Prime}{PSTR_Prime}': {options},")
