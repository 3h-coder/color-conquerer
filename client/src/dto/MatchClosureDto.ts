import { PartialPlayerInfoDto } from "./PlayerInfoDto";

export enum EndingReason {
    PLAYER_LEFT = "player left",
    PLAYER_WON = "player won",
    DRAW = "draw",
    NEVER_JOINED = "player never joined the match"
}

export interface MatchClosureDto {
    endingReason: string,
    winner: PartialPlayerInfoDto,
    loser: PartialPlayerInfoDto,
}