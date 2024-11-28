import {
    PlayerGameInfoBundleDto,
    undefinedPlayerInfoBundleDto,
} from "./PlayerInfoBundleDto";

export interface TurnInfoDto {
    currentPlayerId: string;
    isPlayer1Turn: boolean;
    durationInS: number;
    playerInfoBundle: PlayerGameInfoBundleDto;
    notifyTurnChange: boolean;
}

export const undefinedTurnInfo: TurnInfoDto = {
    currentPlayerId: "",
    isPlayer1Turn: false,
    durationInS: 0,
    playerInfoBundle: undefinedPlayerInfoBundleDto,
    notifyTurnChange: false,
};
