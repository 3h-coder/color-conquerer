import { PlayerInfoDto } from "./PlayerInfoDto";

export enum EndingReason {
    PLAYER_LEFT = "player left",
    PLAYER_WON = "player won",
    DRAW = "draw",
}

export interface MatchClosureDto {
    endingReason: string,
    winner: PlayerInfoDto,
    loser: PlayerInfoDto,
}