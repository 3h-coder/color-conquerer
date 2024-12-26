import { PartialCellInfoDto } from "./PartialCellInfoDto";
import { PartialMatchActionDto } from "./PartialMatchActionDto";

export interface ProcessedActionDto {
    processedAction: PartialMatchActionDto;
    updatedBoardArray: PartialCellInfoDto[][];
    playerMode: number;
}