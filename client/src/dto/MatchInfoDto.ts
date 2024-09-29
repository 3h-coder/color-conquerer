import { CellInfoDto } from "./CellInfoDto";
import { PlayerInfoDto } from "./PlayerInfoDto";

// TODO : remove the player info dtos client side
export interface MatchInfoDto {
    id: string;
    roomId: string;
    boardArray: CellInfoDto[][];
    player1?: PlayerInfoDto;
    player2?: PlayerInfoDto;
    currentTurn: number;
}