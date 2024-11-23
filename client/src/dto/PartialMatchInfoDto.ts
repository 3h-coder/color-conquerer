import { CellInfoDto } from "./CellInfoDto";
import { PartialPlayerGameInfoDto } from "./PlayerGameInfoDto";

export interface PartialMatchInfoDto {
    id: string;
    roomId: string;
    boardArray: CellInfoDto[][];
    currentTurn: number;
    isPlayer1Turn: boolean;
    totalTurnDurationInS: number;
    opponentGameInfo: PartialPlayerGameInfoDto;
}