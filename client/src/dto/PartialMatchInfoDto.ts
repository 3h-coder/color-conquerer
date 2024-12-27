import { PartialCellInfoDto } from "./PartialCellInfoDto";
import { PlayerGameInfoBundleDto, undefinedPlayerInfoBundleDto } from "./PlayerInfoBundleDto";

export interface PartialMatchInfoDto {
    id: string;
    roomId: string;
    boardArray: PartialCellInfoDto[][];
    currentTurn: number;
    playerInfoBundle: PlayerGameInfoBundleDto;
}

export const undefinedMatch: PartialMatchInfoDto = {
    id: "",
    roomId: "",
    boardArray: [],
    currentTurn: 0,
    playerInfoBundle: undefinedPlayerInfoBundleDto
}