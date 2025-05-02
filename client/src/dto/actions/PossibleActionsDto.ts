import { CellDto } from "../cell/CellDto";

export interface PossibleActionsDto {
    playerMode: number;
    transientBoardArray: CellDto[][];
    additionalData: unknown;
}