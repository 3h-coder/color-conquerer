export interface PlayerDto {
    playerId: string;
    isPlayer1: boolean;
}

export const undefinedPlayer: PlayerDto = {
    playerId: "undefined",
    isPlayer1: false
};