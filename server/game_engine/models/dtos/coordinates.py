from dataclasses import dataclass

from constants.game_constants import PLAYER_1_ROWS, PLAYER_2_ROWS
from dto.misc.coordinates_dto import CoordinatesDto


@dataclass(frozen=True)
class Coordinates:
    row_index: int
    column_index: int

    def to_dto(self):
        return CoordinatesDto(self.row_index, self.column_index)

    def as_tuple(self):
        return (self.row_index, self.column_index)

    def is_neighbour(self, other: "Coordinates") -> bool:
        """
        Check if the two coordinates are neighbours.
        """
        return (
            abs(self.row_index - other.row_index) <= 1
            and abs(self.column_index - other.column_index) <= 1
        )

    def is_on_player_side(self, of_player1: bool):
        """
        Checks if the coordinates are located on the given player's side.
        """
        player1_min_row, player1_max_row = PLAYER_1_ROWS
        player2_min_row, player2_max_row = PLAYER_2_ROWS

        if of_player1:
            return (
                self.row_index >= player1_min_row and self.row_index <= player1_max_row
            )
        else:
            return (
                self.row_index >= player2_min_row and self.row_index <= player2_max_row
            )
