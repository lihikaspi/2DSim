from omegaconf import OmegaConf
from pathlib import Path

class ENTITIES:
    T_PLANT = 10
    T_HERBIVORE = 15
    R_HERBIVORE_SIGHT = 3
    T_COOLDOWN = 20
    T_PREDATOR = 20
    R_PREDATOR_SIGHT = 5
    PLANT_SPAWN_THRESHOLD = 0.5

class SIM:
    BOARD_SIZE = (30,30)
    TOTAL_STEPS = 200

class PRETTY_PRINT:
    EMPTY = '.'
    TREE = '^'
    PLANT = '*'
    HERBIVORE = 'H'
    PREDATOR = 'P'

class PATHS:
    NATURE_BOARDS_DIR = "../nature_boards/"

def class_to_dict(cls):
    return {
        k.lower(): v
        for k, v in cls.__dict__.items()
        if not k.startswith("__") and not callable(v)
    }


def load_indexed_boards(boards_dir_path: str):
    """
    Returns a dict with integer keys where each value is a tuple-like list:
    [board_name, 2d_grid]
    """
    boards_dir = Path(boards_dir_path)
    boards = {}

    if boards_dir.exists():
        for idx, file_path in enumerate(sorted(boards_dir.glob("*.txt"))):
            with open(file_path, "r", encoding="utf-8") as f:
                grid = [
                    [int(token) for token in line.split()]
                    for line in f
                    if line.strip()
                ]

            # Store tuple of (name, grid)
            boards[idx] = [file_path.stem, grid]

    return boards

config_data = {
    "entities": class_to_dict(ENTITIES),
    "sim": class_to_dict(SIM),
    "pretty_print": class_to_dict(PRETTY_PRINT),
    "paths": class_to_dict(PATHS),
    "boards": load_indexed_boards(PATHS.NATURE_BOARDS_DIR),
}

cfg = OmegaConf.create(config_data)
with open("../config.yaml", "w") as f:
    OmegaConf.save(config=cfg, f=f)
print(OmegaConf.to_yaml(cfg))