import { PlayerMode } from "../../enums/playerMode";
import { CellDto } from "../misc/CellDto";

export interface ActionErrorDto {
    error: string;
    playerMode: PlayerMode;
    gameBoard: CellDto[][];
}