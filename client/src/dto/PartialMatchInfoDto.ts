import { CellInfoDto } from "./CellInfoDto";

export interface PartialMatchInfoDto {
    id: string;
    roomId: string;
    boardArray: CellInfoDto[][];
    currentTurn: number;
}