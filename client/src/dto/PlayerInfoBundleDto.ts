import { PartialPlayerGameInfoDto } from "./PartialPlayerGameInfoDto";
import { PartialPlayerInfoDto } from "./PartialPlayerInfoDto";
import { PlayerGameInfoDto } from "./PlayerGameInfoDto";

// Used to populate the match's player info context
export interface PlayerInfoBundleDto {
    playerInfo: PartialPlayerInfoDto;
    playerGameInfo: PlayerGameInfoDto;
    opponentGameInfo: PartialPlayerGameInfoDto;
}