import { EMPTY_STRING } from "../env";
import { CellDto } from "./CellDto";
import { PlayerResourceBundleDto, undefinedPlayerResourceBundleDto } from "./PlayerInfoBundleDto";

export interface MatchContextDto {
    id: string;
    roomId: string;
    boardArray: CellDto[][];
    currentTurn: number;
    playerInfoBundle: PlayerResourceBundleDto;
}

export const undefinedMatch: MatchContextDto = {
    id: EMPTY_STRING,
    roomId: EMPTY_STRING,
    boardArray: [],
    currentTurn: 0,
    playerInfoBundle: undefinedPlayerResourceBundleDto
};