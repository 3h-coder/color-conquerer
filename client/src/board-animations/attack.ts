import { MatchActionDto } from "../dto/MatchActionDto";
import { getHtmlCell } from "../utils/cellUtils";
import { cleanup } from "../utils/domUtils";

export function handleCellClashAnimation(action: MatchActionDto) {
    const attackerCoords = action.originatingCellCoords;
    if (!attackerCoords) return;

    const targetCoords = action.impactedCoords;

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
    const styleClass = "cell-clash-or-spawn-indicator";
    const expansionColorVariable = "--expansion-color";
    const cleanupDelayInMs = 2000;

    const htmlCell = getHtmlCell(rowIndex, colIndex);
    const otherHtmlCell = getHtmlCell(otherRowIndex, otherColIndex);

    if (!htmlCell || !otherHtmlCell) return;

    const expansion1 = document.createElement("div");
    expansion1.classList.add(styleClass);
    expansion1.style.setProperty(expansionColorVariable, htmlCell.style.backgroundColor);

    const expansion2 = document.createElement("div");
    expansion2.classList.add(styleClass);
    expansion2.style.setProperty(expansionColorVariable, otherHtmlCell.style.backgroundColor);

    htmlCell.appendChild(expansion1);
    otherHtmlCell.appendChild(expansion2);

    cleanup(expansion1, cleanupDelayInMs);
    cleanup(expansion2, cleanupDelayInMs);
}