import { EMPTY_STRING } from "../env";
import { CellDto } from "./CellDto";
import { PlayerGameInfoBundleDto, undefinedPlayerInfoBundleDto } from "./PlayerInfoBundleDto";

export interface PartialMatchInfoDto {
    id: string;
    roomId: string;
    boardArray: CellDto[][];
    currentTurn: number;
    playerInfoBundle: PlayerGameInfoBundleDto;
}

export const undefinedMatch: PartialMatchInfoDto = {
    id: EMPTY_STRING,
    roomId: EMPTY_STRING,
    boardArray: [],
    currentTurn: 0,
    playerInfoBundle: undefinedPlayerInfoBundleDto
};