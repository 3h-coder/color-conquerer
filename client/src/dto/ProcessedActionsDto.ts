import { MatchActionDto } from "./MatchActionDto";
import { PartialCellInfoDto } from "./PartialCellInfoDto";

export interface ProcessedActionsDto {
    processedActions: MatchActionDto[];
    updatedBoardArray: PartialCellInfoDto[][];
}