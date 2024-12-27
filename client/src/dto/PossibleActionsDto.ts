import { PartialCellInfoDto } from "./PartialCellInfoDto";
import { PartialMatchActionDto } from "./PartialMatchActionDto";

export interface PossibleActionsDto {
    possibleActions: PartialMatchActionDto[];
    playerMode: number;
    transientBoardArray: PartialCellInfoDto[][];
}