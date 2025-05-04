import { CellDto } from "../cell/CellDto";
import { PlayerResourceBundleDto, undefinedPlayerResourceBundleDto } from "../player/PlayerInfoBundleDto";
import { SpellsDto } from "../spell/SpellsDto";

export interface GameContextDto {
    gameBoard: CellDto[][];
    playerResourceBundle: PlayerResourceBundleDto;
    spellsDto: SpellsDto;
}

export const undefinedGameContextDto: GameContextDto = {
    gameBoard: [],
    playerResourceBundle: undefinedPlayerResourceBundleDto,
    spellsDto: { spells: [] }
};