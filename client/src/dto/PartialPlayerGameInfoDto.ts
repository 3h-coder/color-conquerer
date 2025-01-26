import { SpellDto } from "./SpellDto";

export interface PartialPlayerGameInfoDto {
    player1: boolean;
    maxHP: number;
    currentHP: number;
    maxMP: number;
    currentMP: number;
    spells: SpellDto[];
}

export const undefinedPlayerGameInfo: PartialPlayerGameInfoDto = {
    player1: false,
    maxHP: 0,
    currentHP: 0,
    maxMP: 0,
    currentMP: 0,
    spells: []
};