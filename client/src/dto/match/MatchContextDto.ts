import { EMPTY_STRING } from "../../env";
import { CellDto } from "../misc/CellDto";
import { PlayerResourceBundleDto, undefinedPlayerResourceBundleDto } from "../player/PlayerInfoBundleDto";

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