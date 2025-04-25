import { PlayerDto } from "../player/PlayerDto";

// ⚠️ Must be strictly identical to the server side definition
export enum EndingReason {
    PLAYER_VICTORY = 1,
    DRAW = 2,
    PLAYER_LEFT = 3,
    PLAYER_INACTIVE = 4,
    PLAYER_CONCEDED = 5,
    NEVER_JOINED = 6

}

export interface MatchClosureDto {
    endingReason: number,
    winner: PlayerDto,
    loser: PlayerDto,
}