import UserDto from "./UserDto";

export interface QueueRegisterDto {
    user: UserDto;
    playerId: string;
}