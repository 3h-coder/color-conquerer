import { MatchActionDto } from "../../dto/actions/MatchActionDto";
import { getHtmlCell } from "../../utils/cellUtils";
import { displayAppliedSpellEffect } from "./common";

export function handleArcheryVowAnimation(spellAction: MatchActionDto) {
    const impactedCoords = spellAction.metadata.impactedCoords;
    const htmlCell = getHtmlCell(impactedCoords.rowIndex, impactedCoords.columnIndex);
    if (!htmlCell)
        return;

    displayAppliedSpellEffect(htmlCell);
}