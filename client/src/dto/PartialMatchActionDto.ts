import { ActionType } from "../enums/actionType";
import { CoordinatesDto } from "./CoordinatesDto";

export interface PartialMatchActionDto {
    playerId: string;
    type: ActionType;
    originatingCellCoords?: CoordinatesDto;
    impactedCoords: CoordinatesDto[];
}