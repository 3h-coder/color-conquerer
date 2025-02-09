import { CellDto } from "../dto/CellDto";
import { MatchActionDto } from "../dto/MatchActionDto";
import { ActionType } from "../enums/actionType";
import { CellState } from "../enums/cellStates";
import { getHtmlCell, getOwnedCellColor } from "./cellUtils";

export function animateProcessedAction(action: MatchActionDto, isPlayer1: boolean, boardArray: CellDto[][]) {
  switch (action.type) {
    case ActionType.CELL_MOVE: {
      const targetCoords = action.impactedCoords;
      const targetCell = boardArray[targetCoords.rowIndex][targetCoords.columnIndex];
      if (targetCell.state === CellState.MANA_BUBBLE)
        animateManaBubblePop(targetCoords.rowIndex, targetCoords.columnIndex);
      break;
    }

    case ActionType.CELL_ATTACK: {
      const attackerCoords = action.originatingCellCoords;
      if (!attackerCoords) return;

      const targetCoords = action.impactedCoords;

      animateCellClash(
        attackerCoords.rowIndex,
        attackerCoords.columnIndex,
        targetCoords.rowIndex,
        targetCoords.columnIndex
      );
      break;
    }

    case ActionType.CELL_SPAWN: {
      const newCellCoordinates = action.impactedCoords;
      const targetCell = boardArray[newCellCoordinates.rowIndex][newCellCoordinates.columnIndex];
      const cellOfMine = isPlayer1 === action.player1;
      animateCellSpawn(newCellCoordinates.rowIndex, newCellCoordinates.columnIndex, cellOfMine);
      if (targetCell.state === CellState.MANA_BUBBLE)
        animateManaBubblePop(newCellCoordinates.rowIndex, newCellCoordinates.columnIndex);
      break;
    }

    default:
      break;
  }
}


function animateCellClash(
  rowIndex: number,
  colIndex: number,
  otherRowIndex: number,
  otherColIndex: number
) {
  const styleClass = "cell-clash-or-spawn-indicator";
  const expansionColorVariable = "--expansion-color";
  const cleanupDelayInMs = 2000;

  const htmlCell = getHtmlCell(rowIndex, colIndex);
  const otherHtmlCell = getHtmlCell(otherRowIndex, otherColIndex);

  if (!htmlCell || !otherHtmlCell) return;

  const expansion1 = document.createElement("div");
  expansion1.classList.add(styleClass);
  expansion1.style.setProperty(expansionColorVariable, htmlCell.style.backgroundColor);

  const expansion2 = document.createElement("div");
  expansion2.classList.add(styleClass);
  expansion2.style.setProperty(expansionColorVariable, otherHtmlCell.style.backgroundColor);

  htmlCell.appendChild(expansion1);
  otherHtmlCell.appendChild(expansion2);

  cleanup(expansion1, cleanupDelayInMs);
  cleanup(expansion2, cleanupDelayInMs);
}

function animateCellSpawn(rowIndex: number, colIndex: number, ownCell: boolean) {
  const styleClass = "cell-clash-or-spawn-indicator";
  const expansionColorVariable = "--expansion-color";
  const cleanupDelayInMs = 2000;

  const htmlCell = getHtmlCell(rowIndex, colIndex);

  if (!htmlCell)
    return;

  const expansion = document.createElement("div");
  expansion.classList.add(styleClass);
  expansion.style.setProperty(expansionColorVariable, getOwnedCellColor(false, ownCell));

  htmlCell.appendChild(expansion);

  cleanup(expansion, cleanupDelayInMs);
}

function animateManaBubblePop(rowIndex: number, colIndex: number) {
  const styleClasses = ["mana-bubble-pop", "absolute-positioning-centered"];
  const cleanupDelayInMs = 650;

  const htmlCell = getHtmlCell(rowIndex, colIndex);

  if (!htmlCell)
    return;

  const bubble = document.createElement("div");
  bubble.classList.add(...styleClasses);

  htmlCell.appendChild(bubble);
  cleanup(bubble, cleanupDelayInMs);
}

/**
 * Removes the specified DOM element from the page
 * after the specified delay using the setTimeout API.
 */
function cleanup(element: HTMLElement, delayInMs: number) {
  setTimeout(() => element.remove(), delayInMs);
}
