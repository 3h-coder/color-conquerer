import { ActionType } from "../enums/actionType";
import { CoordinatesDto } from "./CoordinatesDto";

export interface PartialMatchActionDto {
    player1: boolean;
    type: ActionType;
    originatingCellCoords?: CoordinatesDto;
    impactedCoords: CoordinatesDto[];
}