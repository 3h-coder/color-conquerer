import { CellDto } from "./PartialCellInfoDto";

export interface PossibleActionsDto {
    playerMode: number;
    transientBoardArray: CellDto[][];
}