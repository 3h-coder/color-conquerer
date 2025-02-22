import { CellDto } from "../dto/CellDto";
import { MatchActionDto } from "../dto/MatchActionDto";
import { CellState } from "../enums/cellState";
import { getHtmlCell, getOwnedCellColor } from "../utils/cellUtils";
import { cleanup } from "../utils/domUtils";
import { animateManaBubblePop } from "./common";

export function handleCellSpawnAnimation(action: MatchActionDto, isPlayer1: boolean, boardArray: CellDto[][]) {
    const newCellCoordinates = action.impactedCoords;
    const targetCell = boardArray[newCellCoordinates.rowIndex][newCellCoordinates.columnIndex];
    const cellOfMine = isPlayer1 === action.player1;

    animateCellSpawn(newCellCoordinates.rowIndex, newCellCoordinates.columnIndex, cellOfMine);

    if (targetCell.state === CellState.MANA_BUBBLE)
        animateManaBubblePop(newCellCoordinates.rowIndex, newCellCoordinates.columnIndex);
}

function animateCellSpawn(rowIndex: number, colIndex: number, ownCell: boolean) {
    const styleClass = "cell-clash-or-spawn-indicator";
    const expansionColorVariable = "--expansion-color";
    const cleanupDelayInMs = 2000;

    const htmlCell = getHtmlCell(rowIndex, colIndex);

    if (!htmlCell)
        return;

    const expansion = document.createElement("div");
    expansion.classList.add(styleClass);
    expansion.style.setProperty(expansionColorVariable, getOwnedCellColor(false, ownCell));

    htmlCell.appendChild(expansion);

    cleanup(expansion, cleanupDelayInMs);
}