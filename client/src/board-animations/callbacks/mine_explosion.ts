import { ActionCallbackDto } from "../../dto/ActionCallbackDto";
import { PartialSpellDto } from "../../dto/PartialSpellDto";
import { getHtmlCell } from "../../utils/cellUtils";
import { cleanup, delay } from "../../utils/domUtils";

export async function animateMineExplosion(callback: ActionCallbackDto, setActionSpell: (spellAction: PartialSpellDto | null) => void) {
    const styleClass = "cell-explosion";
    const expansionColorVariable = "--expansion-color";
    const cleanupDelayInMs = 380;

    const parentAction = callback.parentAction;
    const explosionCenter = parentAction.impactedCoords;

    const htmlCell = getHtmlCell(explosionCenter.rowIndex, explosionCenter.columnIndex);
    if (!htmlCell)
        return;

    setActionSpell(callback.spellCause);

    const explosion = document.createElement("div");
    explosion.classList.add(styleClass);
    explosion.style.setProperty(expansionColorVariable, "blue");

    await delay(1000);

    htmlCell.appendChild(explosion);
    shakeGameGrid();

    setTimeout(() => {
        setActionSpell(null);
    }, 2500);
    cleanup(explosion, cleanupDelayInMs);
}

function shakeGameGrid() {
    const shakeClass = "shake";
    const gameGrid = document.getElementById("grid-outer");
    if (!gameGrid)
        return;

    gameGrid.classList.add(shakeClass);
    setTimeout(() => gameGrid.classList.remove(shakeClass), 500);
}