import { ActionCallbackDto } from "../../dto/ActionCallbackDto";
import { getHtmlCell } from "../../utils/cellUtils";

export function animateMineExplosion(callback: ActionCallbackDto) {
    const explosionCenter = callback.parentAction.impactedCoords;
    const htmlCell = getHtmlCell(explosionCenter.rowIndex, explosionCenter.columnIndex);
}