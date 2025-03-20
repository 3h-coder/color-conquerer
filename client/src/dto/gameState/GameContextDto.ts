import { CellDto } from "../misc/CellDto";
import { PlayerResourceBundleDto, undefinedPlayerResourceBundleDto } from "../player/PlayerInfoBundleDto";

export interface GameContextDto {
    gameBoard: CellDto[][];
    playerResourceBundle: PlayerResourceBundleDto;
}

export const undefinedGameContextDto: GameContextDto = {
    gameBoard: [],
    playerResourceBundle: undefinedPlayerResourceBundleDto
};