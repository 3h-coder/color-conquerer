from dto.actions.match_action_dto import ActionType, MatchActionDto
from game_engine.models.actions.action import Action
from game_engine.models.actions.hooks.stamina_restoration_hook import (
    StaminaRestorationHook,
)
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.game_board import GameBoard
from game_engine.models.match.match_context import MatchContext
from game_engine.models.spells.abstract.spell import Spell


class SpellCasting(Action):
    """
    Represents the effective invocation of a spell.
    """

    HOOKS = {StaminaRestorationHook()}

    def __init__(
        self,
        from_player1: bool,
        impacted_coords: bool,
        spell: Spell,
    ):
        super().__init__(from_player1, impacted_coords)
        self.spell = spell
        self.mana_cost = spell.MANA_COST

    def __eq__(self, other):
        return (
            isinstance(other, SpellCasting)
            and other.spell.ID == self.spell.ID
            and other.metadata == self.metadata
        )

    def __hash__(self):
        return hash((self.spell.ID, self.metadata))

    def to_dto(self):
        return MatchActionDto(
            player1=self.from_player1,
            type=ActionType.PLAYER_SPELL,
            # Note : the spell here must be partial to not
            # contain the count number as it will be sent to both clients
            spell=self.spell.to_partial_dto(),
            metadata=self.metadata.to_dto(),
            specificMetadata=self.spell.get_specific_metadata_dto(),
        )

    @staticmethod
    def create(from_player1: bool, spell: Spell, row_index: int, column_index: int):
        return SpellCasting(
            from_player1=from_player1,
            impacted_coords=Coordinates(row_index, column_index),
            spell=spell,
        )

    @staticmethod
    def calculate(
        spell: Spell,
        from_player1: bool,
        transient_game_board: GameBoard,
    ):
        """
        Returns a set of spell casting actions that can be performed on a cell.
        """
        possible_spell_targets: set[SpellCasting] = set()
        possible_targets = spell.get_possible_targets(
            transient_game_board, from_player1
        )

        for target_coordinates in possible_targets:
            possible_spell_targets.add(
                SpellCasting.create(
                    from_player1,
                    spell,
                    target_coordinates.row_index,
                    target_coordinates.column_index,
                )
            )

        return possible_spell_targets

    def apply(self, match_context: MatchContext):
        self.spell.invoke(
            coordinates=self.metadata.impacted_coords,
            match_context=match_context,
            invocator=CellOwner.PLAYER_1 if self.from_player1 else CellOwner.PLAYER_2,
        )
        self._callbacks_to_trigger = (
            self.spell._callbacks_to_trigger_for_parent_spell_casting
        )
        self._decrease_spell_count(match_context)

    def _decrease_spell_count(self, match_context: MatchContext):
        current_player = match_context.get_current_player()
        current_player.resources.spells[self.spell.ID] = max(
            0, current_player.resources.spells[self.spell.ID] - 1
        )
