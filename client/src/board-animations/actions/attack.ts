import {
    CellAttackMetadataDto,
    isCellAttackMetadataDto,
} from "../../dto/actions/CellAttackMetadataDto";
import { MatchActionDto } from "../../dto/actions/MatchActionDto";
import { getHtmlCell } from "../../utils/cellUtils";
import { triggerAuraEffect } from "../common";

export function handleCellClashAnimation(action: MatchActionDto) {
    const attackerCoords = action.metadata.originatingCellCoords;
    if (!attackerCoords) return;

    const targetCoords = action.metadata.impactedCoords;

    let isRangedAttack = false;
    if (isCellAttackMetadataDto(action.specificMetadata)) {
        isRangedAttack = (action.specificMetadata as CellAttackMetadataDto)
            .isRangedAttack;
    }
    animateCellClash(
        attackerCoords.rowIndex,
        attackerCoords.columnIndex,
        targetCoords.rowIndex,
        targetCoords.columnIndex,
        isRangedAttack
    );
}

function animateCellClash(
    attackerRowIndex: number,
    attackerColIndex: number,
    targetRowIndex: number,
    targetColIndex: number,
    isRangedAttack: boolean
) {
    const attackerCell = getHtmlCell(attackerRowIndex, attackerColIndex);
    const targetCell = getHtmlCell(targetRowIndex, targetColIndex);

    if (!attackerCell || !targetCell) return;

    if (!isRangedAttack) {
        triggerAuraEffect(
            attackerCell,
            () => getComputedStyle(attackerCell).backgroundColor
        );
        triggerAuraEffect(
            targetCell,
            () => getComputedStyle(targetCell).backgroundColor
        );
    } else {

    }
}
