import { CellInfoDto } from "./CellInfoDto";
import { PlayerInfoDto } from "./PlayerInfoDto";

export interface MatchInfoDto {
    boardArray: CellInfoDto[][];
    player1?: PlayerInfoDto;
    player2?: PlayerInfoDto;
    currentTurn: number;
    started: boolean;
}