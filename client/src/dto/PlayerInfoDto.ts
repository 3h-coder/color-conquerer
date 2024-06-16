import UserDto from "./UserDto";

export interface PlayerInfoDto {
    user: UserDto | null; // null if against AI
    playerId: string;
    isPlayer1: boolean;
}