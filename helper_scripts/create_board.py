import numpy as np
from omegaconf import OmegaConf

cfg = OmegaConf.load("../config.yaml")
board = np.random.randint(5, size=cfg.sim.board_size).tolist()
output_path = f"{cfg.paths.nature_boards_dir}/grid_{cfg.sim.board_size[0]}X{cfg.sim.board_size[1]}.txt"
np.savetxt(output_path, board, fmt="%d")
