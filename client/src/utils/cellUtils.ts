import { CellDto } from "../dto/misc/CellDto";
import { CellState, CellStateUtils } from "../enums/cellState";
import { CellTransientState } from "../enums/cellTransientState";
import { EMPTY_STRING } from "../env";
import { cellStyle, colors } from "../style/constants";

export interface AttachedCellBehavior {
  // Temporary behaviors will automatically be upon turn swapping
  isPermanent: boolean;
  mouseEnter?: () => void;
  mouseLeave?: () => void;
}

export function isOwned(cell: CellDto) {
  return cell.owner !== 0;
}

export function getCellBackgroundColor(cell: CellDto, isPlayer1: boolean) {
  const backgroundColorVariable = cellStyle.variableNames.backgroundColor;
  const style: React.CSSProperties = {};

  if (canBeSpawnedOrMovedInto(cell)) {
    /* eslint-disable @typescript-eslint/no-explicit-any */
    (style as any)[backgroundColorVariable] = colors.cell.movementOrSpawnPossible;
  } else if (isNotOwnedAndCanBeSpellTargetted(cell)) {
    (style as any)[backgroundColorVariable] = colors.cell.spellTargettingPossible;
  } else if (CellStateUtils.contains(cell.state, CellState.FRESHLY_SPAWNED)) {
    (style as any)[backgroundColorVariable] = getFreshlySpawnedCellColor(cell, isPlayer1);
  } else {
    (style as any)[backgroundColorVariable] = getCellColor(cell, isPlayer1);
    /* eslint-enable @typescript-eslint/no-explicit-any */
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
  htmlCell.classList.remove(cellStyle.classNames.hovered);
}

export function colorHoveredCell(cell: CellDto) {
  addClassName(cell.rowIndex, cell.columnIndex, cellStyle.classNames.hovered);
}

export function decolorHoveredCell(cell: CellDto) {
  removeClassName(cell.rowIndex, cell.columnIndex, cellStyle.classNames.hovered);
}

export function getOwnedCellColor(isMaster: boolean, ownCell: boolean) {
  if (ownCell)
    return isMaster ? colors.cell.ownMaster : colors.cell.own;

  return isMaster ? colors.cell.opponentMaster : colors.cell.opponent;
}

export function getHtmlCell(rowIndex: number, columnIndex: number) {
  return document.getElementById(getCellId(rowIndex, columnIndex));
}

export function isSelectable(cell: CellDto) {
  return cell.owner !== 0 || cell.transientState !== CellTransientState.NONE;
}

export function canBeSpawnedOrMovedInto(cell: CellDto) {
  return (
    cell.transientState === CellTransientState.CAN_BE_MOVED_INTO ||
    cell.transientState === CellTransientState.CAN_BE_SPAWNED_INTO
  );
}

export function isNotOwnedAndCanBeSpellTargetted(cell: CellDto) {
  return (
    cell.owner === 0 && cell.transientState === CellTransientState.CAN_BE_SPELL_TARGETTED
  );
}

export function isOwnedAndCanBeSpellTargetted(cell: CellDto) {
  return (
    cell.owner !== 0 && cell.transientState === CellTransientState.CAN_BE_SPELL_TARGETTED
  );
}

export function getCellId(rowIndex: number, colIndex: number) {
  return `c-${rowIndex}-${colIndex}`;
}

function getCellColor(cell: CellDto, isPlayer1: boolean) {
  if (!isOwned(cell)) return colors.cell.idle;

  const ownPlayer = isPlayer1 ? 1 : 2;

  if (cell.owner === ownPlayer)
    return cell.isMaster ? colors.cell.ownMaster : colors.cell.own;

  return cell.isMaster ? colors.cell.opponentMaster : colors.cell.opponent;
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
