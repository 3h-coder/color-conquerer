import { ActionCallbackDto } from "../../dto/ActionCallbackDto";
import { PartialSpellDto } from "../../dto/PartialSpellDto";
import { getHtmlCell } from "../../utils/cellUtils";
import { cleanup } from "../../utils/domUtils";

export function animateMineExplosion(callback: ActionCallbackDto, setActionSpell: (spellAction: PartialSpellDto | null) => void) {
    const styleClass = "cell-explosion";
    const expansionColorVariable = "--expansion-color";
    const cleanupDelayInMs = 3000;

    const parentAction = callback.parentAction;
    const explosionCenter = parentAction.impactedCoords;

    const htmlCell = getHtmlCell(explosionCenter.rowIndex, explosionCenter.columnIndex);
    if (!htmlCell)
        return;

    const explosion = document.createElement("div");
    explosion.classList.add(styleClass);
    explosion.style.setProperty(expansionColorVariable, "blue");
    htmlCell.appendChild(explosion);

    setActionSpell(callback.spellCause);
    cleanup(explosion, cleanupDelayInMs);
}