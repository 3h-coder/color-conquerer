import { PartialMatchInfoDto } from "./PartialMatchInfoDto";
import { PartialPlayerInfoDto } from "./PartialPlayerInfoDto";

export interface GameContextDto {
    matchInfo: PartialMatchInfoDto;
    playerInfo: PartialPlayerInfoDto;
}