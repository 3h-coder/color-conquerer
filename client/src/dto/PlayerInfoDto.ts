import { CellInfoDto } from "./CellInfoDto";
import UserDto from "./UserDto";

export interface PlayerInfoDto {
    user: UserDto | null; // null if against AI
    controlledCells: CellInfoDto[];
}