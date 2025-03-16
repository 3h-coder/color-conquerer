import { MatchActionDto } from "../dto/MatchActionDto";
import { getHtmlCell } from "../utils/cellUtils";
import { triggerAuraEffect } from "./common";

export function handleCellClashAnimation(action: MatchActionDto) {
    const attackerCoords = action.originatingCellCoords;
    if (!attackerCoords)
        return;

    const targetCoords = action.impactedCoords.pop();
    if (!targetCoords)
        return;

    animateCellClash(
        attackerCoords.rowIndex,
        attackerCoords.columnIndex,
        targetCoords.rowIndex,
        targetCoords.columnIndex
    );
}

function animateCellClash(
    rowIndex: number,
    colIndex: number,
    otherRowIndex: number,
    otherColIndex: number
) {
    const htmlCell = getHtmlCell(rowIndex, colIndex);
    const otherHtmlCell = getHtmlCell(otherRowIndex, otherColIndex);

    if (!htmlCell || !otherHtmlCell)
        return;

    triggerAuraEffect(htmlCell, () => getComputedStyle(htmlCell).backgroundColor);
    triggerAuraEffect(otherHtmlCell, () => getComputedStyle(otherHtmlCell).backgroundColor);
}