import { PartialPlayerGameInfoDto, undefinedPlayerGameInfo } from "./PartialPlayerGameInfoDto";
import { PlayerGameInfoDto } from "./PlayerGameInfoDto";

// Used to populate the match's player info context
export interface PlayerGameInfoBundleDto {
    player1GameInfo: PlayerGameInfoDto;
    player2GameInfo: PartialPlayerGameInfoDto;
}

export const undefinedPlayerInfoBundleDto: PlayerGameInfoBundleDto = {
    player1GameInfo: undefinedPlayerGameInfo,
    player2GameInfo: undefinedPlayerGameInfo
}