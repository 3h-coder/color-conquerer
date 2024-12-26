import { PartialCellInfoDto } from "./PartialCellInfoDto";
import { PartialMatchActionDto } from "./PartialMatchActionDto";
import { PlayerGameInfoBundleDto } from "./PlayerInfoBundleDto";

export interface ProcessedActionDto {
    processedAction: PartialMatchActionDto;
    updatedBoardArray: PartialCellInfoDto[][];
    playerMode: number;
    playerInfoBundle: PlayerGameInfoBundleDto;
}