from config import Config
from entities.entity import EmptySpace
from entities.entity_type_enum import EntityType
from entities.location import Location
from entities.mobile_entity import MobileEntity


class Predator(MobileEntity):
    """
    Predator class. Inherits from MobileEntity
    """

    def __init__(self, lifespan: int, loc: Location, r: int, cfg: Config) -> None:
        """
        Initializes the predator

        Args:
            lifespan (int): Lifespan of the predator
            loc (Location): Location of the predator
            r (int): Sight radius for hunting
            cfg: OmegaConf object
        """
        super().__init__(EntityType.PREDATOR, lifespan, loc, r, cfg)

    def move(self, grid) -> int:
        """
        Move the predator. Implements the abstract method from MobileEntity

        Args:
            grid: Grid object
        """
        if not self.is_still_alive():
            grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
            return 0

        next_move = self.get_next_move(grid, predator=True)
        target_entity = grid.grid[next_move.coords]
        consumption = False

        if target_entity.type == EntityType.PLANT:
            target_entity.kill()

        if target_entity.type == EntityType.HERBIVORE:
            self.refuel_age()
            consumption = True
        else:
            self.increase_age()

        grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
        self.loc = next_move
        grid.update_grid(next_move, self)
        return 1 if consumption else 0
