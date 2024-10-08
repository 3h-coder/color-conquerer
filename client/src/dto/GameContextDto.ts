import { MatchInfoDto } from "./MatchInfoDto";
import { PartialPlayerInfoDto } from "./PlayerInfoDto";

export interface GameContextDto {
    matchInfo: MatchInfoDto;
    playerInfo: PartialPlayerInfoDto;
}