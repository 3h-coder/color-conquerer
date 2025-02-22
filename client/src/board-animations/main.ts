import { CellDto } from "../dto/CellDto";
import { MatchActionDto } from "../dto/MatchActionDto";
import { PartialSpellDto } from "../dto/PartialSpellDto";
import { ActionType } from "../enums/actionType";
import { handleCellClashAnimation } from "./attack";
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
