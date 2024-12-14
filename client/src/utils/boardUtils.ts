import { CellInfoDto } from "../dto/CellInfoDto";
import { PossibleActionsDto } from "../dto/PossibleActionsDto";
import { ActionType } from "../enums/actionType";
import { colors } from "../style/constants";

export function colorBoard(boardArray: CellInfoDto[][], isPlayer1: boolean) {
    boardArray.forEach((row) => {
        row.forEach((cell) => {
            if (cell.owner === 0) return;

            const htmlCell = getHtmlCell(cell.rowIndex, cell.columnIndex);
            if (!htmlCell)
                return;
            htmlCell.style.backgroundColor = getCellColor(cell, isPlayer1);
        });
    });
}

function getCellColor(cell: CellInfoDto, isPlayer1: boolean) {
    const ownPlayer = isPlayer1 ? 1 : 2;

    if (cell.owner === ownPlayer)
        return cell.isMaster ? colors.ownMasterCell : colors.ownCell;

    return cell.isMaster ? colors.opponentMasterCell : colors.opponentCell;
}

export function colorBoardFromPossibleActions(possibleActionsDto: PossibleActionsDto) {
    possibleActionsDto.possibleActions.forEach((action) => {
        if (action.type === ActionType.CELL_MOVE) {
            const { rowIndex, columnIndex } = { ...action.impactedCoords[0] };
            colorCellToPossibleMovement(rowIndex, columnIndex);
        }
    });
}

function colorCellToPossibleMovement(rowIndex: number, columnIndex: number) {
    const htmlCell = getHtmlCell(rowIndex, columnIndex);
    if (!htmlCell)
        return;

    htmlCell.style.backgroundColor = colors.ownCellMovementPossible;
}

export function getHtmlCell(rowIndex: number, columnIndex: number) {
    return document.getElementById(
        getCellId(rowIndex, columnIndex)
    );
}

export function getCellId(rowIndex: number, colIndex: number) {
    return `c-${rowIndex}-${colIndex}`;
}