import { CellInfoDto } from "./CellInfoDto";
import { MatchActionDto } from "./MatchActionDto";

export interface ProcessedActionsDto {
    processedActions: MatchActionDto[];
    updatedBoardArray: CellInfoDto[][];
}