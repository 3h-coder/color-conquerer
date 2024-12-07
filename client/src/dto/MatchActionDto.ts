import { ActionType } from "../enums/actionType"

export interface MatchActionDto {
    fromPlayer1: boolean;
    isDirect: boolean;
    type: ActionType;
    impactedCoords: number[];
}