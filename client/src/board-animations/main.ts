import { ActionCallbackDto } from "../dto/ActionCallbackDto";
import { CellDto } from "../dto/CellDto";
import { MatchActionDto } from "../dto/MatchActionDto";
import { PartialSpellDto } from "../dto/PartialSpellDto";
import { PlayerResourceBundleDto } from "../dto/PlayerInfoBundleDto";
import { ActionCallbackId } from "../enums/actionCallbackId";
import { ActionType } from "../enums/actionType";
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

export async function animateActionCallbacks(
    callback: ActionCallbackDto,
    currentPlayerisPlayer1: boolean,
    stateSetters: GameStateSetters
) {
    stateSetters.setPlayerResourceBundle(callback.updatedGameContext.playerResourceBundle);
    await animateCallback(callback, currentPlayerisPlayer1, stateSetters.setActionSpell);
    developmentLog("Updating game context after animation");
    stateSetters.setBoardArray(callback.updatedGameContext.gameBoard);
}

async function animateCallback(
    callback: ActionCallbackDto,
    currentPlayerisPlayer1: boolean,
    setActionSpell: (spellAction: PartialSpellDto | null) => void
) {
    switch (callback.id) {
        case ActionCallbackId.MINE_EXPLOSION:
            await animateMineExplosion(callback, currentPlayerisPlayer1, setActionSpell);
            break;

        default:
            break;
    }
}
