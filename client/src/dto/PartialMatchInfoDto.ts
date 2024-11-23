import { CellInfoDto } from "./CellInfoDto";

export interface PartialMatchInfoDto {
    id: string;
    roomId: string;
    boardArray: CellInfoDto[][];
    currentTurn: number;
    isPlayer1Turn: boolean;
    totalTurnDurationInS: number;
}

export const undefinedMatch: PartialMatchInfoDto = {
    id: "",
    roomId: "",
    boardArray: [],
    currentTurn: 0,
    isPlayer1Turn: false,
    totalTurnDurationInS: 0
}