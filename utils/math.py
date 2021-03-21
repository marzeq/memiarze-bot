import random

def calcNextNumber(currNumber: int, rise: bool):
    if rise:
        return min(currNumber + random.uniform(.01, .1), 1.5)
    else:
        return max(currNumber - random.uniform(.01, .1), .25)
