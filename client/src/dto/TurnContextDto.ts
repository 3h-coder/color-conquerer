import { EMPTY_STRING } from "../env";
import { CellDto } from "./CellDto";
import { PlayerResourceBundleDto, undefinedPlayerResourceBundleDto } from "./PlayerInfoBundleDto";

export interface TurnContextDto {
    currentPlayerId: string;
    isPlayer1Turn: boolean;
    remainingTimeInS: number;
    durationInS: number;
    notifyTurnChange: boolean;
    updatedBoardArray: CellDto[][];
    playerResourceBundle: PlayerResourceBundleDto;
}

export const undefinedTurnInfo: TurnContextDto = {
    currentPlayerId: EMPTY_STRING,
    isPlayer1Turn: false,
    remainingTimeInS: 0,
    durationInS: 0,
    notifyTurnChange: false,
    updatedBoardArray: [],
    playerResourceBundle: undefinedPlayerResourceBundleDto,
};
