import { PartialMatchActionDto } from "../dto/PartialMatchActionDto";
import { ActionType } from "../enums/actionType";
import { getHtmlCell } from "./cellUtils";

export function animateProcessedAction(action: PartialMatchActionDto) {
  if (action.type === ActionType.CELL_ATTACK) {
    const attacker_coords = action.originatingCellCoords!;
    const target_coords = action.impactedCoords[0];
    animateCellClash(
      attacker_coords.rowIndex,
      attacker_coords.columnIndex,
      target_coords.rowIndex,
      target_coords.columnIndex
    );
  }
}

export function animateCellClash(rowIndex: number, colIndex: number, otherRowIndex: number, otherColIndex: number) {
  const explosionClass = "cell-clash-indicator";
  const explosionColorVariable = "--explosion-color";
  
  const htmlCell = getHtmlCell(rowIndex, colIndex);
  const otherHtmlCell = getHtmlCell(otherRowIndex, otherColIndex);

  if (!htmlCell || !otherHtmlCell)
    return;

  const explosion1 = document.createElement('div');
  explosion1.classList.add(explosionClass);
  explosion1.style.setProperty(explosionColorVariable, htmlCell.style.backgroundColor);

  const explosion2 = document.createElement('div');
  explosion2.classList.add(explosionClass);
  explosion2.style.setProperty(explosionColorVariable, otherHtmlCell.style.backgroundColor);

  htmlCell.appendChild(explosion1);
  otherHtmlCell.appendChild(explosion2);

  function cleanup(element: HTMLElement) {
    setTimeout(() => element.remove(), 2000);
  };

  cleanup(explosion1);
  cleanup(explosion2);
}