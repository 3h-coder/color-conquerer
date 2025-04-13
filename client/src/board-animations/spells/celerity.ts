import { MatchActionDto } from "../../dto/actions/MatchActionDto";
import { displayAppliedSpellEffect, getCellsInFormation } from "./common";

export function handleCelerityAnimation(spellAction: MatchActionDto) {
    const htmlCells = getCellsInFormation(spellAction);
    displayCelerityEffect(htmlCells);
}

function displayCelerityEffect(htmlCells: HTMLElement[]) {
    if (htmlCells.length === 0)
        return;

    htmlCells.forEach(cell => displayAppliedSpellEffect(cell));
}
