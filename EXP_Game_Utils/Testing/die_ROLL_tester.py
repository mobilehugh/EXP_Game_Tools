from please import roll_this
import random

for __ in range(20):
    number = str(random.randint(1, 20))
    dietype = [4, 6, 8, 10, 12, 20, 30, 50, 100, 1000]
    dice = str(dietype[random.randint(0, 9)])
    modifier = ["D", "-", "+"]
    moddy = modifier[random.randint(0, 2)]
    print(roll_this(number + "d" + dice + moddy + number))
