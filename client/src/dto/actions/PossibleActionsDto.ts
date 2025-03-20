import { CellDto } from "./CellDto";

export interface PossibleActionsDto {
    playerMode: number;
    transientBoardArray: CellDto[][];
}