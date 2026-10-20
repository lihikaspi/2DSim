import copy
from pathlib import Path
import numpy as np
from PIL import Image

LIVE = "1"
DEAD = "0"
PRINT_LIVE = "*"
PRINT_DEAD = "."


class GOLSimulation:
    def __init__(self, seed, steps):
        self.seed = seed
        self.initial_grid, self.num_rows, self.num_cols = self.load_seed(seed)
        self.states = [self.initial_grid]
        self.curr_state = self.states[0]
        self.live_count_grid = []
        self.total_steps = steps
        self.curr_step = 0
        self.pretty_print(initial=True)

    def load_seed(self, seed):
        seed = seed.strip()
        seed_path = Path(f"seed_templates/{seed}.txt")
        if not seed_path.is_file():
            raise ValueError("Seed is not valid")
        with open(seed_path, "r") as file:
            initial_grid = [list(line.strip()) for line in file if line.strip()]
            num_rows = len(initial_grid)
            num_cols = len(initial_grid[0])
        return initial_grid, num_rows, num_cols

    def check_in_grid(self, r, c):
        if r < 0 or r >= self.num_rows or c < 0 or c >= self.num_cols:
            return False
        return True

    def update_count_grid(self):
        live_count_grid = np.zeros((self.num_rows, self.num_cols), dtype=int)
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                for i in range(r - 1, r + 2):
                    for j in range(c - 1, c + 2):
                        if r == i and c == j:
                            continue
                        if self.check_in_grid(i, j):
                            if self.curr_state[r][c] == LIVE:
                                live_count_grid[i][j] += 1
        self.live_count_grid = live_count_grid

    def step(self):
        self.curr_step += 1
        next_state = copy.deepcopy(self.curr_state)
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.curr_state[r][c] == LIVE:
                    if self.live_count_grid[r][c] < 2 or self.live_count_grid[r][c] > 3:
                        next_state[r][c] = DEAD
                elif self.curr_state[r][c] == DEAD:
                    if self.live_count_grid[r][c] == 3:
                        next_state[r][c] = LIVE
        self.states.append(next_state)
        self.curr_state = self.states[-1]

    def visualize_sim(self):
        images = []
        pixel_size = 15  # Size of each cell in pixels
        grid_color = 200  # Gray level for gridlines (0-255)

        for state in self.states:
            grid = np.array(state, dtype=int)
            rows, cols = grid.shape

            pixel_array = ((1 - grid) * 255).astype(np.uint8)

            img = Image.fromarray(pixel_array, mode="L")
            img_resized = img.resize(
                (cols * pixel_size, rows * pixel_size), resample=Image.NEAREST
            ).convert("RGB")

            img_arr = np.array(img_resized)
            img_arr[:, ::pixel_size] = [grid_color, grid_color, grid_color]
            img_arr[::pixel_size, :] = [grid_color, grid_color, grid_color]

            images.append(Image.fromarray(img_arr))

        images[0].save(
            f"animation_{self.seed}_{self.total_steps}.gif",
            save_all=True,
            append_images=images[1:],
            duration=250,  # 250 ms per frame (4 fps)
            loop=0,  # Loop forever
        )

    def pretty_print(self, initial=False):
        print("\nINITIAL SEED:" if initial else f"\nSTEP {self.curr_step}:")
        board = self.initial_grid if initial else self.curr_state
        to_print = []
        for r in range(self.num_rows):
            line = " ".join(board[r])
            line = line.replace(LIVE, PRINT_LIVE)
            line = line.replace(DEAD, PRINT_DEAD)
            to_print.append(line)
        for p in to_print:
            print(p)


    def run_simulation(self):
        while self.curr_step < self.total_steps:
            self.update_count_grid()
            self.step()
            self.pretty_print()
        self.visualize_sim()
        print("*********** END GAME! ***********")


def main():
    print("*********** START GAME! ***********")
    print("choose seed:")
    seed = input()
    print("choose number of total steps:")
    steps = int(input())
    sim = GOLSimulation(seed, steps)
    sim.run_simulation()


if __name__ == "__main__":
    main()
