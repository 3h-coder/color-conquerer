import { CellDto } from "../misc/CellDto";

export interface PossibleActionsDto {
    playerMode: number;
    transientBoardArray: CellDto[][];
    additionalData: unknown;
}