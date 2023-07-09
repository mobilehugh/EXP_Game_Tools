import table
import please


def attributes_fresh(attributes_creating:table.PersonaRecord) -> table.PersonaRecord:
    """
    generates initial attributes for anthro, alien and robot personae 
    """
    # anthro core attributes DIE ROLLS dictionary comprehension
    attribute_die_rolls = {
        key: value["dice"]
        for (key, value) in table.suggested_anthro_attribute_ranges.items()
        if key != "HPM"
    }

    # alien adjustments to CON, DEX, INT, MSTR, PSTR
    if attributes_creating.FAMILY == "Alien":
        for attribute,deets in table.alien_attribute_ranges.items():
            attribute_die_rolls[attribute]["dice"] = deets["dice"] 

    # robot adjustments to CON, DEX, INT, PSTR
    if attributes_creating.FAMILY == "Robot":
        # must assign robot primes
        attributes_creating.CON_Prime = please.roll_this("1d4")
        attributes_creating.DEX_Prime = please.roll_this("1d4")
        attributes_creating.INT_Prime = please.roll_this("1d4")
        attributes_creating.PSTR_Prime = please.roll_this("1d4")

        # reassign die rolls based on primes
        attribute_die_rolls["CON"]["dice"] = table.robot_attributes[object.CON_Prime]["CON"]
        attribute_die_rolls["DEX"]["dice"] = table.robot_attributes[object.DEX_Prime]["DEX"]
        attribute_die_rolls["INT"]["dice"] = table.robot_attributes[object.INT_Prime]["INT"] 
        attribute_die_rolls["PSTR"]["dice"] = table.robot_attributes[object.PSTR_Prime]["PSTR"]

    # use die roll list to generate new attributes
    for attribute in attribute_die_rolls:
        die_roll = please.roll_this(attribute_die_rolls[attribute])
        setattr(attributes_creating, attribute, die_roll)

    # must reassign robotic MSTR to zero
    if attributes_creating.FAMILY == "Robot":
            attributes_creating.MSTR = 0

    return attributes_creating # modified by side effects
