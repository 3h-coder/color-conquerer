import { PlayerDto } from "../player/PlayerDto";

// ⚠️ Must be strictly identical to the server side definition
export enum EndingReason {
    PLAYER_VICTORY = "player victory",
    DRAW = "draw",
    PLAYER_CONCEDED = "player conceded",
    PLAYER_LEFT = "player left",
    PLAYER_INACTIVE = "player inactive",
    NEVER_JOINED = "never joined",
    FATIGUE = "fatigue",
}

export interface MatchClosureDto {
    endingReason: string,
    winner: PlayerDto,
    loser: PlayerDto,
}