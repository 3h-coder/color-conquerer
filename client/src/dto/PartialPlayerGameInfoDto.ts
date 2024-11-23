export interface PartialPlayerGameInfoDto {
    maxHP: number;
    currentHP: number;
    maxMP: number;
    currentMP: number;
}

export const undefinedPlayerGameInfo: PartialPlayerGameInfoDto = {
    maxHP: 0,
    currentHP: 0,
    maxMP: 0,
    currentMP: 0
}