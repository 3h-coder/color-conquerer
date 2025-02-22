import { CellDto } from "../dto/CellDto";
import { MatchActionDto } from "../dto/MatchActionDto";
import { ActionType } from "../enums/actionType";
import { handleCellClashAnimation } from "./attack";
import { handleCellMovementAnimation } from "./movement";
import { handleCellSpawnAnimation } from "./spawn";

export function animateProcessedAction(action: MatchActionDto, isPlayer1: boolean, boardArray: CellDto[][]) {
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

        default:
            break;
    }
}