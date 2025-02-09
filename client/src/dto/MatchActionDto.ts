import { ActionType } from "../enums/actionType";
import { CoordinatesDto } from "./CoordinatesDto";

export interface MatchActionDto {
    player1: boolean;
    type: ActionType;
    originatingCellCoords?: CoordinatesDto;
    impactedCoords: CoordinatesDto;
    spellId: number;
}