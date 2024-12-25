import { PartialCellInfoDto } from "./PartialCellInfoDto";
import { PartialMatchActionDto } from "./PartialMatchActionDto";

export interface ProcessedActionsDto {
    processedActions: PartialMatchActionDto[];
    updatedBoardArray: PartialCellInfoDto[][];
    playerMode: number;
}