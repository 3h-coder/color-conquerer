import { CellDto } from "../dto/CellDto";
import { CellState, CellTransientState } from "../enums/cellStates";
import { EMPTY_STRING } from "../env";
import { cellStyle, colors } from "../style/constants";

export function isOwned(cell: CellDto) {
  return cell.owner !== 0;
}

export function getCellStyle(cell: CellDto, isPlayer1: boolean) {
  const style: React.CSSProperties = {};

  if (canBeTargetted(cell)) {
    style.backgroundColor = colors.cell.ownCellActionPossible;
  } else if (cell.state === CellState.FRESHLY_SPAWNED) {
    style.backgroundColor = getFreshlySpawnedCellColor(cell, isPlayer1);
  } else {
    style.backgroundColor = getCellColor(cell, isPlayer1);
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

export function colorHoveredCell(cell: CellDto) {
  addClassName(cell.rowIndex, cell.columnIndex, cellStyle.hoveredClassName);
}

export function decolorHoveredCell(cell: CellDto) {
  removeClassName(cell.rowIndex, cell.columnIndex, cellStyle.hoveredClassName);
}

function getCellColor(cell: CellDto, isPlayer1: boolean) {
  if (!isOwned(cell)) return colors.cell.idle;

  const ownPlayer = isPlayer1 ? 1 : 2;

  if (cell.owner === ownPlayer)
    return cell.isMaster ? colors.cell.ownMaster : colors.cell.own;

  return cell.isMaster ? colors.cell.opponentMaster : colors.cell.opponent;
}

export function getOwnedCellColor(isMaster: boolean, ownCell: boolean) {
  if (ownCell)
    return isMaster ? colors.cell.ownMaster : colors.cell.own;

  return isMaster ? colors.cell.opponentMaster : colors.cell.opponent;
}

function getFreshlySpawnedCellColor(
  cell: CellDto,
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

export function getHtmlCell(rowIndex: number, columnIndex: number) {
  return document.getElementById(getCellId(rowIndex, columnIndex));
}

export function isSelectable(cell: CellDto) {
  return cell.owner !== 0 || cell.transientState !== CellTransientState.NONE;
}

/**
 * Returns true if the cell can be targetted by a spell, a spawn or a move.
 */
export function canBeTargetted(cell: CellDto) {
  return (
    cell.transientState === CellTransientState.CAN_BE_MOVED_INTO ||
    cell.transientState === CellTransientState.CAN_BE_SPAWNED_INTO ||
    cell.transientState === CellTransientState.CAN_BE_SPELL_TARGETTED
  );
}

export function getCellId(rowIndex: number, colIndex: number) {
  return `c-${rowIndex}-${colIndex}`;
}
