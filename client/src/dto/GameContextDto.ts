import { CellDto } from "./CellDto";
import { PlayerResourceBundleDto, undefinedPlayerResourceBundleDto } from "./PlayerInfoBundleDto";

export interface GameContextDto {
    gameBoard: CellDto[][];
    playerResourceBundle: PlayerResourceBundleDto;
}

export const undefinedGameContextDto: GameContextDto = {
    gameBoard: [],
    playerResourceBundle: undefinedPlayerResourceBundleDto
};