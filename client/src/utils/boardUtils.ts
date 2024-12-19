import { CellInfoDto } from "../dto/CellInfoDto";
import { CoordinatesDto } from "../dto/CoordinatesDto";
import { PossibleActionsDto } from "../dto/PossibleActionsDto";
import { ProcessedActionsDto } from "../dto/ProcessedActionsDto";
import { ActionType } from "../enums/actionType";
import {
  clearCellColor,
  colorCellToPossibleMovement,
  colorOwnedCell,
  isOwned,
} from "./cellUtils";

type CellDelegate = (cell: CellInfoDto) => boolean;

export function getDefaultSelectableCells(boardArray: CellInfoDto[][]) {
  // By default, a cell is selectable if it is owned, even if it's an enemy cell
  return boardArray.map((row) => row.map((cell) => isOwned(cell)));
}

export function clearBoardColoring(
  boardArray: CellInfoDto[][],
  excludingCondition?: CellDelegate
) {
  boardArray.forEach((row) => {
    row.forEach((cell) => {
      if (excludingCondition !== undefined && excludingCondition(cell)) return;

      clearCellColor(cell.rowIndex, cell.columnIndex);
    });
  });
}

export function colorBoard(boardArray: CellInfoDto[][], isPlayer1: boolean) {
  boardArray.forEach((row) => {
    row.forEach((cell) => {
      if (!isOwned(cell)) return;

      colorOwnedCell(cell, isPlayer1);
    });
  });
}

export function applyPossibleActionsToBoard(
  possibleActionsDto: PossibleActionsDto,
  setCellsSelectable: (
    coordinates: CoordinatesDto[],
    isSelectable: boolean
  ) => void
) {
  const selectableCellsCoordinates: CoordinatesDto[] = [];
  possibleActionsDto.possibleActions.forEach((action) => {
    // TODO extract into a method with a switch case later on
    if (action.type === ActionType.CELL_MOVE) {
      const { rowIndex, columnIndex } = { ...action.impactedCoords[0] };
      colorCellToPossibleMovement(rowIndex, columnIndex);
      selectableCellsCoordinates.push({ rowIndex, columnIndex });
    }
  });
  setCellsSelectable(selectableCellsCoordinates, true);
}

export function animateProcessedActionsOnBoard(
  processedActionsDto: ProcessedActionsDto,
  isPlayer1: boolean,
  setSelectableCells: (
    selectableArray: boolean[][]
  ) => void
) {
  const updatedBoardArray = processedActionsDto.updatedBoardArray;

  processedActionsDto.processedActions.forEach((action) => {
    // TODO extract into a method with a switch case later on
    if (action.type == ActionType.CELL_MOVE) {
      if (!action.originatingCellCoords)
        return;

      // const { rowIndex, columnIndex } = { ...action.originatingCellCoords }
      // const { rowIndex: newRowIndex, columnIndex: newColumnIndex } = { ...action.impactedCoords[0] }

      setSelectableCells(getDefaultSelectableCells(updatedBoardArray));
      clearBoardColoring(updatedBoardArray, cell => isOwned(cell));
    }
  })
}
