from dataclasses import dataclass

from dto.actions.cell_attack_metadata_dto import CellAttackMetadataDto


@dataclass
class CellAttackMetadata:
    is_ranged_attack: bool

    def to_dto(self):
        return CellAttackMetadataDto(
            isRangedAttack=self.is_ranged_attack,
        )
