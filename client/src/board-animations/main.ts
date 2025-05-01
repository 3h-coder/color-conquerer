import { ActionCallbackDto } from "../dto/actions/ActionCallbackDto";
import { MatchActionDto } from "../dto/actions/MatchActionDto";
import { CellDto } from "../dto/misc/CellDto";
import { PlayerResourceBundleDto } from "../dto/player/PlayerInfoBundleDto";
import { PartialSpellDto } from "../dto/spell/PartialSpellDto";
import { ActionCallbackId } from "../enums/actionCallbackId";
import { ActionType } from "../enums/actionType";
import { getHtmlCell } from "../utils/cellUtils";
import { developmentLog } from "../utils/loggingUtils";
import { handleCellClashAnimation } from "./actions/attack";
import { handleCellMovementAnimation } from "./actions/movement";
import { handleCellSpawnAnimation } from "./actions/spawn";
import { animateMineExplosion } from "./callbacks/mineExplosion";
import { animateCellDeath } from "./common";
import { handleSpellCastingAnimation } from "./spells/spell";

export interface GameStateSetters {
    setBoardArray: (boardArray: CellDto[][]) => void;
    setActionSpell: (spellAction: PartialSpellDto | null) => void;
    setPlayerResourceBundle: (bundle: PlayerResourceBundleDto) => void;
}

export async function animateProcessedAction(
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
            await handleCellClashAnimation(action, isPlayer1);
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

    action.metadata.deaths.forEach((coord) => {
        const htmlCell = getHtmlCell(coord.rowIndex, coord.columnIndex);
        if (htmlCell)
            animateCellDeath(htmlCell);
    });
}

export async function animateActionCallbacks(
    callback: ActionCallbackDto,
    currentPlayerisPlayer1: boolean,
    stateSetters: GameStateSetters
) {
    developmentLog("Animating callback", callback);
    const { setPlayerResourceBundle, setActionSpell, setBoardArray } = stateSetters;

    setPlayerResourceBundle(callback.updatedGameContext.playerResourceBundle);

    await animateCallback(callback, currentPlayerisPlayer1, setActionSpell);

    developmentLog("Callback animation over, updating the board");
    setBoardArray(callback.updatedGameContext.gameBoard);
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

    callback.deaths.forEach((coord) => {
        const htmlCell = getHtmlCell(coord.rowIndex, coord.columnIndex);
        if (htmlCell)
            animateCellDeath(htmlCell);
    });
}
