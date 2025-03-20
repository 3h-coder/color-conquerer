export interface PlayerResourcesDto {
    maxHP: number;
    currentHP: number;
    maxMP: number;
    currentMP: number;
}

export const undefinedPlayerResources: PlayerResourcesDto = {
    maxHP: 0,
    currentHP: 0,
    maxMP: 0,
    currentMP: 0
};