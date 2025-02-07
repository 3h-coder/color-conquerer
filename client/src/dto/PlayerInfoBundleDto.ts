import { PlayerResourcesDto, undefinedPlayerResources } from "./PlayerResourcesDto";

// Used to populate the match's player info context
export interface PlayerResourceBundleDto {
    player1Resources: PlayerResourcesDto;
    player2Resources: PlayerResourcesDto;
}

export const undefinedPlayerResourceBundleDto: PlayerResourceBundleDto = {
    player1Resources: undefinedPlayerResources,
    player2Resources: undefinedPlayerResources
};