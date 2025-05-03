import { EMPTY_STRING } from "../../env";
import { CellDto } from "../cell/CellDto";
import { PlayerResourceBundleDto, undefinedPlayerResourceBundleDto } from "../player/PlayerInfoBundleDto";

export interface MatchContextDto {
    id: string;
    roomId: string;
    boardArray: CellDto[][];
    currentTurn: number;
    playerResourcesBundle: PlayerResourceBundleDto;
}

export const undefinedMatch: MatchContextDto = {
    id: EMPTY_STRING,
    roomId: EMPTY_STRING,
    boardArray: [],
    currentTurn: 0,
    playerResourcesBundle: undefinedPlayerResourceBundleDto
};