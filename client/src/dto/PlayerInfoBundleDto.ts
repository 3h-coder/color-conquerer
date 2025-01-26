import { PartialPlayerGameInfoDto, undefinedPlayerGameInfo } from "./PartialPlayerGameInfoDto";

// Used to populate the match's player info context
export interface PlayerGameInfoBundleDto {
    player1GameInfo: PartialPlayerGameInfoDto;
    player2GameInfo: PartialPlayerGameInfoDto;
}

export const undefinedPlayerInfoBundleDto: PlayerGameInfoBundleDto = {
    player1GameInfo: undefinedPlayerGameInfo,
    player2GameInfo: undefinedPlayerGameInfo
};