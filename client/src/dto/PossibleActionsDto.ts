import { PartialCellInfoDto } from "./PartialCellInfoDto";

export interface PossibleActionsDto {
    playerMode: number;
    transientBoardArray: PartialCellInfoDto[][];
}