import { PlayerDto } from "../player/PlayerDto";

export enum EndingReason {
    PLAYER_VICTORY = "player won",
    DRAW = "draw",
    PLAYER_LEFT = "player left",
    PLAYER_CONCEDED = "player conceded",
    NEVER_JOINED = "player never joined the match"

}

export interface MatchClosureDto {
    endingReason: string,
    winner: PlayerDto,
    loser: PlayerDto,
}