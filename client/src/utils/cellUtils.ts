import { CellInfoDto } from "../dto/CellInfoDto";
import { cellStyle, colors } from "../style/constants";

export function isOwned(cell: CellInfoDto) {
    return cell.owner !== 0;
}

export function getDefaultStyle(cell: CellInfoDto, isPlayer1: boolean) {
    const style: React.CSSProperties = {
        backgroundColor: getCellColor(cell, isPlayer1)
    }

    return style;
}

export function clearCellColor(rowIndex: number, colIndex: number) {
    const htmlCell = getHtmlCell(rowIndex, colIndex);
    if (!htmlCell)
        return;

    htmlCell.style.backgroundColor = colors.cell.idle;
    htmlCell.style.animation = "";
}

export function colorCellToPossibleMovement(rowIndex: number, colIndex: number) {
    const htmlCell = getHtmlCell(rowIndex, colIndex);
    if (!htmlCell)
        return;

    htmlCell.style.backgroundColor = colors.cell.ownCellMovementPossible;
    htmlCell.style.animation = "half-fade-in 1s infinite alternate-reverse";
}

export function colorHoveredCell(cell: CellInfoDto) {
    addClassName(cell.rowIndex, cell.columnIndex, cellStyle.hoveredClassName);
}

export function decolorHoveredCell(cell: CellInfoDto) {
    removeClassName(cell.rowIndex, cell.columnIndex, cellStyle.hoveredClassName);
}

function getCellColor(cell: CellInfoDto, isPlayer1: boolean) {
    if (!isOwned(cell))
        return colors.cell.idle;

    const ownPlayer = isPlayer1 ? 1 : 2;

    if (cell.owner === ownPlayer)
        return cell.isMaster ? colors.cell.ownMaster : colors.cell.own;

    return cell.isMaster ? colors.cell.opponentMaster : colors.cell.opponent;
}

function addClassName(rowIndex: number, colIndex: number, className: string) {
    const htmlCell = getHtmlCell(rowIndex, colIndex);
    if (!htmlCell)
        return;

    const currentClassName = htmlCell.className;
    htmlCell.className = `${currentClassName} ${className}`;
}

function removeClassName(rowIndex: number, colIndex: number, className: string) {
    const htmlCell = getHtmlCell(rowIndex, colIndex);
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