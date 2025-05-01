export interface PlayerResourcesDto {
    maxHP: number;
    currentHP: number;
    maxMP: number;
    currentMP: number;
    maxStamina: number;
    currentStamina: number;
}

export const undefinedPlayerResources: PlayerResourcesDto = {
    maxHP: 0,
    currentHP: 0,
    maxMP: 0,
    currentMP: 0,
    maxStamina: 0,
    currentStamina: 0,
};