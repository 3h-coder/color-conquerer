import { PartialCellInfoDto } from "../dto/PartialCellInfoDto";
import { CellState } from "../enums/cellState";
import { EMPTY_STRING } from "../env";
import { cellStyle, colors } from "../style/constants";

export function isOwned(cell: PartialCellInfoDto) {
  return cell.owner !== 0;
}

export function getCellStyle(cell: PartialCellInfoDto, isPlayer1: boolean) {
  const style: React.CSSProperties = {};

  switch (cell.state) {
    case CellState.FRESHLY_SPAWNED:
      style.backgroundColor = getFreshlySpawnedCellColor(cell, isPlayer1);
      style.animation = undefined;
      break;

    case CellState.CAN_BE_MOVED_INTO:
    case CellState.CAN_BE_SPAWNED_INTO:
      style.backgroundColor = colors.cell.ownCellActionPossible;
      style.animation = "half-fade-in 1s infinite alternate-reverse";
      break;

    default:
      style.backgroundColor = getCellColor(cell, isPlayer1);
      style.animation = undefined;
      break;
  }

  return style;
}

export function clearCellColor(rowIndex: number, colIndex: number) {
  const htmlCell = getHtmlCell(rowIndex, colIndex);
  if (!htmlCell) return;

  clearHTMLCellStyle(htmlCell);
}

function clearHTMLCellStyle(htmlCell: HTMLElement) {
  htmlCell.style.backgroundColor = colors.cell.idle;
  htmlCell.style.animation = EMPTY_STRING;
  htmlCell.classList.remove(cellStyle.hoveredClassName);
}

export function colorHoveredCell(cell: PartialCellInfoDto) {
  addClassName(cell.rowIndex, cell.columnIndex, cellStyle.hoveredClassName);
}

export function decolorHoveredCell(cell: PartialCellInfoDto) {
  removeClassName(cell.rowIndex, cell.columnIndex, cellStyle.hoveredClassName);
}

function getCellColor(cell: PartialCellInfoDto, isPlayer1: boolean) {
  if (!isOwned(cell)) return colors.cell.idle;

  const ownPlayer = isPlayer1 ? 1 : 2;

  if (cell.owner === ownPlayer)
    return cell.isMaster ? colors.cell.ownMaster : colors.cell.own;

  return cell.isMaster ? colors.cell.opponentMaster : colors.cell.opponent;
}

function getFreshlySpawnedCellColor(
  cell: PartialCellInfoDto,
  isPlayer1: boolean
) {
  const ownPlayer = isPlayer1 ? 1 : 2;

  return cell.owner === ownPlayer
    ? colors.cell.ownCellFreshlySpawned
    : colors.cell.opponentCellFreshlySpawned;
}

function addClassName(rowIndex: number, colIndex: number, className: string) {
  const htmlCell = getHtmlCell(rowIndex, colIndex);
  if (!htmlCell) return;

  htmlCell.classList.add(className);
}

function removeClassName(
  rowIndex: number,
  colIndex: number,
  className: string
) {
  const htmlCell = getHtmlCell(rowIndex, colIndex);
  if (!htmlCell) return;

  htmlCell.classList.remove(className);
}

function getHtmlCell(rowIndex: number, columnIndex: number) {
  return document.getElementById(getCellId(rowIndex, columnIndex));
}

export function isSelectable(cell: PartialCellInfoDto) {
  return cell.owner !== 0 || cell.state !== CellState.NONE;
}

export function getCellId(rowIndex: number, colIndex: number) {
  return `c-${rowIndex}-${colIndex}`;
}
