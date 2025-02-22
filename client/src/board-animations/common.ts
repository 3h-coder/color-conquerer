import { getHtmlCell } from "../utils/cellUtils";
import { cleanup } from "../utils/domUtils";

export function animateManaBubblePop(rowIndex: number, colIndex: number) {
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