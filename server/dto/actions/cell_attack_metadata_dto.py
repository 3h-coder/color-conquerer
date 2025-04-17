from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class CellAttackMetadataDto(BaseDto):
    isRangedAttack: bool
    isRetaliated: bool

    @staticmethod
    def get_default():
        return CellAttackMetadataDto(isRangedAttack=False, isRetaliated=False)
