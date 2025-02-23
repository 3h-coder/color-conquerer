import { ActionCallbackDto } from "../dto/ActionCallbackDto";
import { ActionCallbacksDto } from "../dto/ActionCallbacksDto";
import { CellDto } from "../dto/CellDto";
import { MatchActionDto } from "../dto/MatchActionDto";
import { PartialSpellDto } from "../dto/PartialSpellDto";
import { ActionCallbackId } from "../enums/actionCallbackId";
import { ActionType } from "../enums/actionType";
import { handleCellClashAnimation } from "./attack";
import { animateMineExplosion } from "./callbacks/mine_explosion";
import { handleCellMovementAnimation } from "./movement";
import { handleCellSpawnAnimation } from "./spawn";
import { handleSpellCastingAnimation } from "./spell";

export function animateProcessedAction(
    action: MatchActionDto,
    isPlayer1: boolean,
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
            handleSpellCastingAnimation(action, setActionSpell);
            break;

        default:
            break;
    }
}

export function animateActionCallbacks(
    actionCallbacks: ActionCallbacksDto,
    setBoardArray: (boardArray: CellDto[][]) => void,
    setActionSpell: (spellAction: PartialSpellDto | null) => void
) {
    actionCallbacks.callbacks.forEach((callback) => {
        animateCallback(callback, setActionSpell);
        setBoardArray(callback.updatedGameBoard);
    });
}

function animateCallback(
    callback: ActionCallbackDto,
    setActionSpell: (spellAction: PartialSpellDto | null) => void
) {
    switch (callback.id) {
        case ActionCallbackId.MINE_EXPLOSION:
            animateMineExplosion(callback, setActionSpell);
            break;

        default:
            break;
    }
}
