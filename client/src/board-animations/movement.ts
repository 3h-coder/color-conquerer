import { MatchActionDto } from "../dto/actions/MatchActionDto";
import { CellDto } from "../dto/misc/CellDto";
import { CellState, CellStateUtils } from "../enums/cellState";
import { getHtmlCell } from "../utils/cellUtils";
import { animateManaBubblePop } from "./common";

export function handleCellMovementAnimation(action: MatchActionDto, boardArray: CellDto[][]) {
    const sourceCoords = action.originatingCellCoords;
    if (!sourceCoords) return;

    const targetCoords = action.impactedCoords;
    const targetCell = boardArray[targetCoords.rowIndex][targetCoords.columnIndex];

    // Create moving cell clone
    const sourceElement = getHtmlCell(sourceCoords.rowIndex, sourceCoords.columnIndex);
    const targetElement = getHtmlCell(targetCoords.rowIndex, targetCoords.columnIndex);

    if (!sourceElement || !targetElement) return;

    const clone = sourceElement.cloneNode(true) as HTMLElement;
    const sourceBounds = sourceElement.getBoundingClientRect();
    const targetBounds = targetElement.getBoundingClientRect();

    // Calculate the difference in position
    const deltaX = targetBounds.left - sourceBounds.left;
    const deltaY = targetBounds.top - sourceBounds.top;

    // Style and position the clone
    clone.style.setProperty('--target-x', `${deltaX}px`);
    clone.style.setProperty('--target-y', `${deltaY}px`);
    clone.style.position = 'absolute';
    clone.style.left = `${sourceBounds.left}px`;
    clone.style.top = `${sourceBounds.top}px`;
    clone.style.width = `${sourceBounds.width}px`;
    clone.style.height = `${sourceBounds.height}px`;
    clone.classList.add('moving-cell');

    // Add clone to body
    document.body.appendChild(clone);

    // Remove clone after animation
    setTimeout(() => {
        clone.remove();
        if (CellStateUtils.contains(targetCell.state, CellState.MANA_BUBBLE)) {
            animateManaBubblePop(targetCoords.rowIndex, targetCoords.columnIndex);
        }
    }, 400);
}