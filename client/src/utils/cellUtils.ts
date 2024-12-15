import { CellInfoDto } from "../dto/CellInfoDto";
import { cellStyle, colors } from "../style/constants";

export function isOwned(cell: CellInfoDto) {
    return cell.owner !== 0;
}

export function clearCellColor(rowIndex: number, colIndex: number) {
    const htmlCell = getHtmlCell(rowIndex, colIndex);
    if (!htmlCell)
        return;

    htmlCell.style.backgroundColor = colors.idleCell;
}

export function colorOwnedCell(cell: CellInfoDto, isPlayer1: boolean) {
    const htmlCell = getHtmlCell(cell.rowIndex, cell.columnIndex);
    if (!htmlCell)
        return;

    htmlCell.style.backgroundColor = getOwnedCellColor(cell, isPlayer1);

}

export function colorCellToPossibleMovement(rowIndex: number, colIndex: number) {
    const htmlCell = getHtmlCell(rowIndex, colIndex);
    if (!htmlCell)
        return;

    htmlCell.style.backgroundColor = colors.ownCellMovementPossible;
}

export function colorHoveredCell(cell: CellInfoDto) {
    addClassName(cell, cellStyle.hoveredClassName);
}

export function decolorHoveredCell(cell: CellInfoDto) {
    removeClassName(cell, cellStyle.hoveredClassName);
}

function getOwnedCellColor(cell: CellInfoDto, isPlayer1: boolean) {
    const ownPlayer = isPlayer1 ? 1 : 2;

    if (cell.owner === ownPlayer)
        return cell.isMaster ? colors.ownMasterCell : colors.ownCell;

    return cell.isMaster ? colors.opponentMasterCell : colors.opponentCell;
}

function addClassName(cell: CellInfoDto, className : string) {
    const htmlCell = getHtmlCell(cell.rowIndex, cell.columnIndex);
    if (!htmlCell)
        return;

    const currentClassName = htmlCell.className;
    htmlCell.className = `${currentClassName} ${className}`;
}

function removeClassName(cell: CellInfoDto, className : string) {
    const htmlCell = getHtmlCell(cell.rowIndex, cell.columnIndex);
    if (!htmlCell)
        return;

    const currentClassName = htmlCell.className;
    htmlCell.className = currentClassName.replace(className, "").trim();
}

function getHtmlCell(rowIndex: number, columnIndex: number) {
    return document.getElementById(
        getCellId(rowIndex, columnIndex)
    );
}

export function getCellId(rowIndex: number, colIndex: number) {
    return `c-${rowIndex}-${colIndex}`;
}