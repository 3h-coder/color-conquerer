import { PartialCellInfoDto } from "./PartialCellInfoDto";

export interface PartialMatchInfoDto {
    id: string;
    roomId: string;
    boardArray: PartialCellInfoDto[][];
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