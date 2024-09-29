import { MatchInfoDto } from "./MatchInfoDto";
import { PlayerInfoDto } from "./PlayerInfoDto";

export interface GameContextDto {
    matchInfo: MatchInfoDto;
    playerInfo: PlayerInfoDto;
}