import { CellDto } from "./CellDto";
import { PartialMatchActionDto } from "./PartialMatchActionDto";
import { TurnContextDto } from "./TurnContextDto";

export interface ProcessedActionDto {
    processedAction: PartialMatchActionDto;
    playerMode: number;
    updatedTurnInfo: TurnContextDto;
    overridingTransientBoard: CellDto[][] | null;
}