export interface PlayerResourcesDto {
    maxHP: number;
    currentHP: number;
    maxMP: number;
    currentMP: number;
    currentStamina: number;
    maxStamina: number;
}

export const undefinedPlayerResources: PlayerResourcesDto = {
    maxHP: 0,
    currentHP: 0,
    maxMP: 0,
    currentMP: 0,
    currentStamina: 0,
    maxStamina: 0,
};