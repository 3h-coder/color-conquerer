import { PossibleActionsDto } from "../dto/actions/PossibleActionsDto";
import { isShieldFormationMetadata, ShieldFormationMetadataDto } from "../dto/spell/metadata/ShieldFormationMetadataDto";
import { EMPTY_STRING } from "../env";
import { cellStyle, colors } from "../style/constants";
import { AttachedCellBehavior, getHtmlCell } from "./cellUtils";

export function handlePossibleActionsAdditionalData(
    possibleActions: PossibleActionsDto,
    setAttachedCellBehaviors: React.Dispatch<React.SetStateAction<(AttachedCellBehavior | undefined)[][]>>
) {
    const additionalData = possibleActions.additionalData;

    if (isShieldFormationMetadata(additionalData)) {
        handleSquareHints(additionalData as ShieldFormationMetadataDto, setAttachedCellBehaviors);
    }
}

/**
 * Handles the square hints for the shield formation spell.
 * Shows the square that will be affected by the spell when hovering over the cell.
 */
function handleSquareHints(
    shieldFormationMetadata: ShieldFormationMetadataDto,
    setAttachedCellBehaviors: React.Dispatch<React.SetStateAction<(AttachedCellBehavior | undefined)[][]>>
) {
    const squarePerCoordinates = shieldFormationMetadata.squarePerCoordinates;
    const squares = shieldFormationMetadata.squares;
    const attachedCellBehaviors: Record<string, AttachedCellBehavior> = {};


    Object.entries(squarePerCoordinates).forEach(([key, value]) => {
        const [rowIndex, columnIndex] = key.split(',').map(Number);
        const htmlCell = getHtmlCell(rowIndex, columnIndex);
        if (!htmlCell)
            return;

        const squareIndex = value;
        const square = squares[squareIndex];

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
            const [rowIndex, columnIndex] = key.split(',').map(Number);
            newState[rowIndex][columnIndex] = value;
        });

        return newState;
    });
}