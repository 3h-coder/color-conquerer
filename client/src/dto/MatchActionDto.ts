import { ActionType } from "../enums/actionType";
import { CoordinatesDto } from "./CoordinatesDto";

export interface MatchActionDto {
    playerId: string;
    isDirect: boolean;
    type: ActionType;
    originatingCellCoords?: CoordinatesDto;
    impactedCoords: CoordinatesDto[];
}