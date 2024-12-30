import { EMPTY_STRING } from "../env";
import { PartialCellInfoDto } from "./PartialCellInfoDto";
import { PlayerGameInfoBundleDto, undefinedPlayerInfoBundleDto } from "./PlayerInfoBundleDto";

export interface PartialMatchInfoDto {
    id: string;
    roomId: string;
    boardArray: PartialCellInfoDto[][];
    currentTurn: number;
    playerInfoBundle: PlayerGameInfoBundleDto;
}

export const undefinedMatch: PartialMatchInfoDto = {
    id: EMPTY_STRING,
    roomId: EMPTY_STRING,
    boardArray: [],
    currentTurn: 0,
    playerInfoBundle: undefinedPlayerInfoBundleDto
}