import { ActionCallbackDto } from "../dto/actions/ActionCallbackDto";
import { MatchActionDto } from "../dto/actions/MatchActionDto";
import { PossibleActionsDto } from "../dto/actions/PossibleActionsDto";
import { CellDto } from "../dto/misc/CellDto";
import { PlayerResourceBundleDto } from "../dto/player/PlayerInfoBundleDto";
import {
    isShieldFormationMetadata,
    ShieldFormationMetadataDto,
} from "../dto/spell/metadata/ShieldFormationMetadataDto";
import { PartialSpellDto } from "../dto/spell/PartialSpellDto";
import { ActionCallbackId } from "../enums/actionCallbackId";
import { ActionType } from "../enums/actionType";
import { EMPTY_STRING } from "../env";
import { cellAttributes, cellStyle, colors } from "../style/constants";
import { AttachedCellBehavior, getHtmlCell } from "../utils/cellUtils";
import { developmentLog } from "../utils/loggingUtils";
import { handleCellClashAnimation } from "./attack";
import { animateMineExplosion } from "./callbacks/mineExplosion";
import { handleCellMovementAnimation } from "./movement";
import { handleCellSpawnAnimation } from "./spawn";
import { handleSpellCastingAnimation } from "./spell";

export interface GameStateSetters {
    setBoardArray: (boardArray: CellDto[][]) => void;
    setActionSpell: (spellAction: PartialSpellDto | null) => void;
    setPlayerResourceBundle: (bundle: PlayerResourceBundleDto) => void;
}

export function animateProcessedAction(
    action: MatchActionDto,
    isPlayer1: boolean,
    isMyTurn: boolean,
    boardArray: CellDto[][],
    setActionSpell: (spellAction: PartialSpellDto | null) => void
) {
    switch (action.type) {
        case ActionType.CELL_MOVE:
            handleCellMovementAnimation(action, boardArray);
            break;

        case ActionType.CELL_ATTACK:
            handleCellClashAnimation(action);
            break;

        case ActionType.CELL_SPAWN:
            handleCellSpawnAnimation(action, isPlayer1, boardArray);
            break;

        case ActionType.PLAYER_SPELL:
            handleSpellCastingAnimation(action, setActionSpell, isMyTurn);
            break;

        default:
            break;
    }
}

export async function animateActionCallbacks(
    callback: ActionCallbackDto,
    currentPlayerisPlayer1: boolean,
    stateSetters: GameStateSetters
) {
    developmentLog("Animating callback", callback);
    const { setPlayerResourceBundle, setActionSpell, setBoardArray } =
        stateSetters;

    setPlayerResourceBundle(callback.updatedGameContext.playerResourceBundle);

    await animateCallback(callback, currentPlayerisPlayer1, setActionSpell);

    developmentLog("Callback animation over, updating the board");
    setBoardArray(callback.updatedGameContext.gameBoard);
}

export function handlePossibleActionsAdditionalData(
    possibleActions: PossibleActionsDto,
    setAttachedCellBehaviors: React.Dispatch<React.SetStateAction<(AttachedCellBehavior | undefined)[][]>>
) {
    const additionalData = possibleActions.additionalData;

    if (isShieldFormationMetadata(additionalData)) {
        const shieldFormationMetadata = additionalData as ShieldFormationMetadataDto;
        const squarePerCoordinates = shieldFormationMetadata.squarePerCoordinates;
        const attachedCellBehaviors: Record<string, AttachedCellBehavior> = {};


        Object.entries(squarePerCoordinates).forEach(([key, value]) => {
            const [rowIndex, columnIndex] = key.split(',').map(Number);
            const htmlCell = getHtmlCell(rowIndex, columnIndex);
            if (!htmlCell)
                return;

            const squareId = value.toString();
            htmlCell.setAttribute(cellAttributes.squareId, squareId);

            const selectorQuery = `.${cellStyle.className}[${cellAttributes.squareId}="${squareId}"]`;
            const attachedCellBehavior: AttachedCellBehavior = {
                mouseEnter: () => {
                    document.querySelectorAll(selectorQuery)
                        .forEach(cell => {
                            const htmlCellElement = cell as HTMLElement;
                            // Store the original color as a data attribute before changing it
                            htmlCellElement.dataset.originalColor = htmlCellElement.style.getPropertyValue(cellStyle.variableNames.backgroundColor);
                            htmlCellElement.classList.add(cellStyle.classNames.possibleSpellTarget);
                            htmlCellElement.style.setProperty(cellStyle.variableNames.backgroundColor, colors.cell.spellTargettingPossible);
                        });
                },
                mouseLeave: () => {
                    document.querySelectorAll(selectorQuery)
                        .forEach(cell => {
                            const htmlCellElement = cell as HTMLElement;
                            htmlCellElement.classList.remove(cellStyle.classNames.possibleSpellTarget);
                            // Restore the original color from the data attribute
                            const originalBackgroundColor = htmlCellElement.dataset.originalColor || EMPTY_STRING;
                            htmlCellElement.style.setProperty(cellStyle.variableNames.backgroundColor, originalBackgroundColor);
                        });
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
}

async function animateCallback(
    callback: ActionCallbackDto,
    currentPlayerisPlayer1: boolean,
    setActionSpell: (spellAction: PartialSpellDto | null) => void
) {
    switch (callback.id) {
        case ActionCallbackId.MINE_EXPLOSION:
            await animateMineExplosion(
                callback,
                currentPlayerisPlayer1,
                setActionSpell
            );
            break;

        default:
            break;
    }
}
