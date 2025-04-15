from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class CellAttackMetadataDto(BaseDto):
    isRangedAttack: bool

    @staticmethod
    def get_default():
        return CellAttackMetadataDto(
            isRangedAttack=False,
        )
