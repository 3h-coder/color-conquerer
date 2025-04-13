import { MatchActionDto } from "../../dto/actions/MatchActionDto";
import { CellDto } from "../../dto/misc/CellDto";
import { CellState, CellStateUtils } from "../../enums/cellState";
import { getHtmlCell, getOwnedCellColor } from "../../utils/cellUtils";
import { animateManaBubblePop, triggerAuraEffect } from "../common";


export function handleCellSpawnAnimation(action: MatchActionDto, isPlayer1: boolean, boardArray: CellDto[][]) {
    const newCellCoordinates = action.metadata.impactedCoords;
    const targetCell = boardArray[newCellCoordinates.rowIndex][newCellCoordinates.columnIndex];
    const cellOfMine = isPlayer1 === action.player1;

    animateCellSpawn(newCellCoordinates.rowIndex, newCellCoordinates.columnIndex, cellOfMine);

    if (CellStateUtils.contains(targetCell.state, CellState.MANA_BUBBLE))
        animateManaBubblePop(newCellCoordinates.rowIndex, newCellCoordinates.columnIndex);
}

function animateCellSpawn(rowIndex: number, colIndex: number, ownCell: boolean) {
    const htmlCell = getHtmlCell(rowIndex, colIndex);
    if (!htmlCell)
        return;

    triggerAuraEffect(htmlCell, () => getOwnedCellColor(false, ownCell));
}