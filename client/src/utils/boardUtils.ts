import { CellInfoDto } from "../dto/CellInfoDto";
import { PossibleActionsDto } from "../dto/PossibleActionsDto";
import { ActionType } from "../enums/actionType";
import { clearCellColor, colorCellToPossibleMovement, colorOwnedCell, isOwned } from "./cellUtils";

type CellDelegate = (cell: CellInfoDto) => boolean;

export function clearBoardColoring(boardArray: CellInfoDto[][], excludingCondition?: CellDelegate) {
    boardArray.forEach((row) => {
        row.forEach((cell) => {
            if (excludingCondition !== undefined && excludingCondition(cell))
                return;

            clearCellColor(cell.rowIndex, cell.columnIndex);
        })
    })
}

export function colorBoard(boardArray: CellInfoDto[][], isPlayer1: boolean) {
    boardArray.forEach((row) => {
        row.forEach((cell) => {
            if (!isOwned(cell)) return;

            colorOwnedCell(cell, isPlayer1);
        });
    });
}

export function colorBoardFromPossibleActions(possibleActionsDto: PossibleActionsDto) {
    possibleActionsDto.possibleActions.forEach((action) => {
        if (action.type === ActionType.CELL_MOVE) {
            const { rowIndex, columnIndex } = { ...action.impactedCoords[0] };
            colorCellToPossibleMovement(rowIndex, columnIndex);
        }
    });
}