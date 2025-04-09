import { MatchActionDto } from "../../dto/actions/MatchActionDto";
import { cleanup } from "../../utils/domUtils";
import { getCellsInFormation } from "./common";

export function handleCelerityAnimation(spellAction: MatchActionDto) {
    const htmlCells = getCellsInFormation(spellAction);
    displayCelerityEffect(htmlCells);
}

function displayCelerityEffect(htmlCells: HTMLElement[]) {
    if (htmlCells.length === 0)
        return;

    const styleClass = "spell-applied-effect";
    const cleanupDelayInMs = 1700;

    htmlCells.forEach(cell => {
        const auraContainer = document.createElement("div");
        auraContainer.classList.add(styleClass);

        cell.appendChild(auraContainer);

        cleanup(auraContainer, cleanupDelayInMs);
    });
}
