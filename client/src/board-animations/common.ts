import { EMPTY_STRING, HTMLElements } from "../env";
import { activeTooltipTarget, cleanupActiveTooltip } from "../singletons/tooltip";
import { getHtmlCell, getOwnedCellColor } from "../utils/cellUtils";
import { cleanup } from "../utils/domUtils";

export function animateManaBubblePop(rowIndex: number, colIndex: number) {
  const styleClasses = ["mana-bubble-pop-effect", "absolute-positioning-centered"];
  const cleanupDelayInMs = 450;

  const htmlCell = getHtmlCell(rowIndex, colIndex);

  if (!htmlCell)
    return;

  const bubble = document.createElement(HTMLElements.div);
  bubble.classList.add(...styleClasses);

  htmlCell.appendChild(bubble);
  cleanup(bubble, cleanupDelayInMs);
}

export function triggerAuraEffect(htmlCell: HTMLElement, colorRetriavalFunction: () => string) {
  const styleClass = "clash-or-spawn-effect";
  const expansionColorVariable = "--expansion-color";
  const cleanupDelayInMs = 2000;

  const aura = document.createElement(HTMLElements.div);
  aura.classList.add(styleClass);
  aura.style.setProperty(expansionColorVariable, colorRetriavalFunction());

  htmlCell.appendChild(aura);

  cleanup(aura, cleanupDelayInMs);
}

export function animateCellSpawn(rowIndex: number, colIndex: number, ownCell: boolean) {
  const htmlCell = getHtmlCell(rowIndex, colIndex);
  if (!htmlCell)
    return;

  triggerAuraEffect(htmlCell, () => getOwnedCellColor(false, ownCell));
}

export function animateCellDeath(htmlCell: HTMLElement) {
  const cleanupDelayInMs = 500;

  if (activeTooltipTarget === htmlCell) {
    cleanupActiveTooltip();
  }

  htmlCell.style.transition = `background-color ${cleanupDelayInMs - 100}ms ease-in-out`;
  htmlCell.style.setProperty("--bg", "white");

  setTimeout(() => {
    htmlCell.style.transition = EMPTY_STRING;
  }, cleanupDelayInMs);
}