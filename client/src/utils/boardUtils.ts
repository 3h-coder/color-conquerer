import { PartialCellInfoDto } from "../dto/PartialCellInfoDto";
import {
  clearCellColor,
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
