export interface PartialPlayerInfoDto {
    playerId: string;
    isPlayer1: boolean;
}

export const undefinedPlayer: PartialPlayerInfoDto = {
    playerId: "undefined",
    isPlayer1: false
}