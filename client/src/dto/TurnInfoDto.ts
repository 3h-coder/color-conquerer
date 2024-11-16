export interface TurnInfoDto {
    currentPlayerId: string;
    isPlayer1Turn: boolean;
    durationInS: number;
    notifyTurnChange: boolean;
}