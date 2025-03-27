import { HTMLElements } from "../env";
import { getHtmlCell } from "../utils/cellUtils";
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