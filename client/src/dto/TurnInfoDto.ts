import { EMPTY_STRING } from "../env";
import { CellDto } from "./PartialCellInfoDto";
import { PlayerGameInfoBundleDto, undefinedPlayerInfoBundleDto } from "./PlayerInfoBundleDto";

export interface TurnInfoDto {
    currentPlayerId: string;
    isPlayer1Turn: boolean;
    durationInS: number;
    totalTurnDurationInS: number;
    notifyTurnChange: boolean;
    playerGameInfoBundle: PlayerGameInfoBundleDto;
    updatedBoardArray: CellDto[][];
}

export const undefinedTurnInfo: TurnInfoDto = {
    currentPlayerId: EMPTY_STRING,
    isPlayer1Turn: false,
    durationInS: 0,
    totalTurnDurationInS: 0,
    notifyTurnChange: false,
    playerGameInfoBundle: undefinedPlayerInfoBundleDto,
    updatedBoardArray: []
};
