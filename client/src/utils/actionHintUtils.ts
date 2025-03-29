import { PossibleActionsDto } from "../dto/actions/PossibleActionsDto";
import { isPositioningMetadataDto, PositioningMetadataDto } from "../dto/spell/metadata/PositioningMetadataDto";
import { EMPTY_STRING } from "../env";
import { cellStyle, colors } from "../style/constants";
import { AttachedCellBehavior, getHtmlCell } from "./cellUtils";

export function handlePossibleActionsAdditionalData(
    possibleActions: PossibleActionsDto,
    setAttachedCellBehaviors: React.Dispatch<React.SetStateAction<(AttachedCellBehavior | undefined)[][]>>
) {
    const additionalData = possibleActions.additionalData;

    if (isPositioningMetadataDto(additionalData)) {
        handleSquareHints(additionalData as PositioningMetadataDto, setAttachedCellBehaviors);
    }
}

/**
 * Handles the formation hints for the shield formation spell.
 * Shows all the cells that will be affected by the spell when hovering over the cell.
 */
function handleSquareHints(
    shieldFormationMetadata: PositioningMetadataDto,
    setAttachedCellBehaviors: React.Dispatch<React.SetStateAction<(AttachedCellBehavior | undefined)[][]>>
) {
    const formationsPerCoordinates = shieldFormationMetadata.formationPerCoordinates;
    const cellForrmations = shieldFormationMetadata.cellFormations;
    const attachedCellBehaviors: Record<string, AttachedCellBehavior> = {};


    Object.entries(formationsPerCoordinates).forEach(([key, value]) => {
        const [rowIndex, columnIndex] = extractCoordsFromKey(key);
        const htmlCell = getHtmlCell(rowIndex, columnIndex);
        if (!htmlCell)
            return;

        const squareIndex = value;
        const square = cellForrmations[squareIndex];

        function cleanupStyles(coords: { rowIndex: number, columnIndex: number; }) {
            const htmlCellElement = getHtmlCell(coords.rowIndex, coords.columnIndex);
            if (!htmlCellElement)
                return;
            htmlCellElement.classList.remove(cellStyle.classNames.possibleSpellTarget);
            const originalBackgroundColor = htmlCellElement.dataset.originalColor || EMPTY_STRING;
            htmlCellElement.style.setProperty(cellStyle.variableNames.backgroundColor, originalBackgroundColor);
        }

        const attachedCellBehavior: AttachedCellBehavior = {
            isActive: false,
            mouseEnter: () => {
                attachedCellBehavior.isActive = true;
                square.forEach(coords => {
                    const htmlCellElement = getHtmlCell(coords.rowIndex, coords.columnIndex);
                    if (!htmlCellElement)
                        return;
                    htmlCellElement.dataset.originalColor = htmlCellElement.style.getPropertyValue(cellStyle.variableNames.backgroundColor);
                    htmlCellElement.classList.add(cellStyle.classNames.possibleSpellTarget);
                    htmlCellElement.style.setProperty(cellStyle.variableNames.backgroundColor, colors.cell.spellTargettingPossible);
                });
            },
            mouseLeave: () => {
                attachedCellBehavior.isActive = false;
                square.forEach(cleanupStyles);
            },
            cleanup: () => {
                attachedCellBehavior.isActive = false;
                square.forEach(cleanupStyles);
            }
        };
        attachedCellBehaviors[key] = attachedCellBehavior;
    });

    setAttachedCellBehaviors(prev => {
        const newState = prev;
        Object.entries(attachedCellBehaviors).forEach(([key, value]) => {
            const [rowIndex, columnIndex] = extractCoordsFromKey(key);
            newState[rowIndex][columnIndex] = value;
        });

        return newState;
    });
}

export function extractCoordsFromKey(key: string) {
    return key.split(',').map(Number);
}

export function convertCoordsToKey(rowIndex: number, columnIndex: number) {
    return `${rowIndex},${columnIndex}`;
}