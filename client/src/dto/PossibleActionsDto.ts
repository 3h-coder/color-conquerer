import { PartialMatchActionDto } from "./PartialMatchActionDto";

export interface PossibleActionsDto {
    possibleActions: PartialMatchActionDto[];
    playerMode: number;
}