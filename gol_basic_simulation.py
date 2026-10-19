import numpy as np
import pandas as pd

LIVE = 0
DEAD = 1

class CellState:
    def __init__(self, x, y, state):
        self.x = x
        self.y = y
        self.state = state

    def change_state(self, new_state):
        self.state = new_state

class GOLSimulation:
    def __init__(self, seed):
        self.seed = seed
        self.curr_state = None



def main():


if __name__ == "__main__":
    main()