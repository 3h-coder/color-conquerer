import { CellInfoDto } from "./CellInfoDto";

export interface PartialMatchInfoDto {
    id: string;
    roomId: string;
    boardArray: CellInfoDto[][];
    currentTurn: number;
    isPlayer1Turn: boolean;
    totalTurnDurationInS: number;
}