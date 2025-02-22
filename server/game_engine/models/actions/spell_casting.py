from dto.coordinates_dto import CoordinatesDto
from dto.match_action_dto import ActionType, MatchActionDto
from game_engine.models.actions.action import Action
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.game_board import GameBoard
from game_engine.models.spells.spell import Spell


class SpellCasting(Action):
    """
    Represents the effective invocation of a spell.
    """

    def __init__(
        self,
        from_player1: bool,
        impacted_coords: bool,
        spell: Spell,
    ):
        super().__init__(from_player1, impacted_coords)
        self.spell = spell

    def __eq__(self, other):
        return (
            isinstance(other, SpellCasting)
            and other.spell.id == self.spell.id
            and other.impacted_coords == self.impacted_coords
        )

    def __hash__(self):
        return hash((self.spell.id, self.impacted_coords))

    def to_dto(self):
        return MatchActionDto(
            player1=self.from_player1,
            type=ActionType.PLAYER_SPELL,
            originatingCellCoords=None,
            impactedCoords=self.impacted_coords,
            # Note : the spell here must be partial to not
            # contain the count number as it will be sent to both clients
            spell=self.spell.to_partial_dto(),
        )

    @staticmethod
    def create(from_player1: bool, spell: Spell, row_index: int, column_index: int):
        return SpellCasting(
            from_player1=from_player1,
            impacted_coords=CoordinatesDto(row_index, column_index),
            spell=spell,
        )

    @staticmethod
    def calculate(
        spell: Spell,
        from_player1: bool,  # not used for now
        transient_game_board: GameBoard,
    ):
        """
        Returns a set of spell casting actions that can be performed on a cell.
        """
        possible_spell_targets: set[SpellCasting] = set()
        possible_targets = spell.get_possible_targets(transient_game_board)

        for target in possible_targets:
            possible_spell_targets.add(
                SpellCasting.create(
                    from_player1,
                    spell,
                    target.row_index,
                    target.column_index,
                )
            )

        return possible_spell_targets

    def apply(self, match_context):
        self.spell.invoke(
            coordinates=self.impacted_coords,
            board=match_context.game_board,
            invocator=CellOwner.PLAYER_1 if self.from_player1 else CellOwner.PLAYER_2,
        )
