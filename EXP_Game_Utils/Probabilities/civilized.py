import please

# does not work unless please.py is in the same directory as this file or symlinked
# test chances for various level of civilization

generation = 1
generations = 10000
tool_score = {"none": 0, "simp": 0, "tech": 0, "comp": 0, "AI": 0}
tool_trans = ["none", "simp", "tech", "comp", "AI"]
language = 0
culture = 0
education = 0
vocation = 0


while generation <= generations:
    # create the attributes of the alien
    AWE = please.roll_this("3d6")
    CHA = please.roll_this("3d6")
    DEX = please.roll_this("5d6-5")
    INT = please.roll_this("5d6-5")
    MSTR = please.roll_this("5d6-5")

    print(f"========= Species # {generation}")
    print(f"AWE={AWE}, CHA={CHA}, DEX={DEX}, INT={INT}, MSTR={MSTR}")
    print("societal: ", end=" ")
    temp_tool_score = 0
    # tool use score check one
    if please.roll_this("1d100") <= (INT * 3):
        temp_tool_score += 1

    # language check
    if please.roll_this("1d100") <= (INT * 3):
        language += 1
        print("language!", end=" ")

        # tool use score check two
        if please.roll_this("1d100") <= (INT * 3):
            temp_tool_score += 1

        # culture check
        if please.roll_this("1d100") <= (CHA * 3):
            culture += 1
            print("culture!", end=" ")

            # tool use score check three
            if please.roll_this("1d100") <= (INT * 3):
                temp_tool_score += 1

            # education check
            if please.roll_this("1d100") <= (AWE * 3):
                education += 1
                print("education!", end=" ")

                # tool use score check four
                if please.roll_this("1d100") <= (INT * 2):
                    temp_tool_score += 1

                # vocation check
                if please.roll_this("1d100") <= (DEX * 3):
                    vocation += 1
                    print("vocation!", end=" ")

    print(f"TTS={temp_tool_score}")
    tool_score[tool_trans[temp_tool_score]] += 1
    print(
        f"language = {language}, culture = {culture}, education = {education}, vocation = {vocation}"
    )
    print(tool_score)
    print(f"=========")
    generation += 1

print("")
print("********************** summary ***********************")
print(f"species tested = {generations}")
print(
    f"societals: language = {language/generations}, culture = {culture/generations},  education = {education/generations}, vocation = {vocation/generations}"
)
print(
    f'tools: none = {tool_score["none"]/generations}, simp = {tool_score["simp"]/generations}, tech = {tool_score["tech"]/generations}, comp = {tool_score["comp"]/generations}, AI = {tool_score["AI"]/generations}'
)
