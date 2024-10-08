import { CellInfoDto } from "./CellInfoDto";
import { PartialPlayerInfoDto } from "./PlayerInfoDto";

// TODO : remove the player info dtos client side
export interface MatchInfoDto {
    id: string;
    roomId: string;
    boardArray: CellInfoDto[][];
    player1?: PartialPlayerInfoDto;
    player2?: PartialPlayerInfoDto;
    currentTurn: number;
}