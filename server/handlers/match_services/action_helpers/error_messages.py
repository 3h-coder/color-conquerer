from enum import StrEnum


class ErrorMessages(StrEnum):
    CANNOT_MOVE_TO_NOR_ATTACK = "Cannot move to nor attack this cell"
    SELECT_IDLE_CELL = "You must select an idle cell"
    NOT_ENOUGH_MANA = "Not enough mana"
    INVALID_ACTION = "Invalid action"  # The client should prevent this message from being shown, but just in case
