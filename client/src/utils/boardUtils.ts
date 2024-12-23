import { CoordinatesDto } from "../dto/CoordinatesDto";
import { PartialCellInfoDto } from "../dto/PartialCellInfoDto";
import { PossibleActionsDto } from "../dto/PossibleActionsDto";
import { ActionType } from "../enums/actionType";
import {
  clearCellColor,
  colorCellToPossibleMovement,
  isOwned,
} from "./cellUtils";

type CellDelegate = (cell: PartialCellInfoDto) => boolean;

/**
 * By default, a cell is selectable if it is owned, even if it's an enemy cell
 */
export function getDefaultSelectableCells(boardArray: PartialCellInfoDto[][]) {
  return boardArray.map((row) => row.map((cell) => isOwned(cell)));
}

export function clearBoardColoring(
  boardArray: PartialCellInfoDto[][],
  excludingCondition?: CellDelegate
) {
  boardArray.forEach((row) => {
    row.forEach((cell) => {
      if (excludingCondition !== undefined && excludingCondition(cell)) return;

      clearCellColor(cell.rowIndex, cell.columnIndex);
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
