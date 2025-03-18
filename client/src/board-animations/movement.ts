import { CellDto } from "../dto/CellDto";
import { MatchActionDto } from "../dto/MatchActionDto";
import { CellState, CellStateUtils } from "../enums/cellState";
import { animateManaBubblePop } from "./common";

export function handleCellMovementAnimation(action: MatchActionDto, boardArray: CellDto[][]) {
    const targetCoords = action.impactedCoords;
    const targetCell = boardArray[targetCoords.rowIndex][targetCoords.columnIndex];

    if (CellStateUtils.contains(targetCell.state, CellState.MANA_BUBBLE))
        animateManaBubblePop(targetCoords.rowIndex, targetCoords.columnIndex);
}