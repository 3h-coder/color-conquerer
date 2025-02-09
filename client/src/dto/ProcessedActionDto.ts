import { CellDto } from "./CellDto";
import { MatchActionDto } from "./MatchActionDto";
import { TurnContextDto } from "./TurnContextDto";

export interface ProcessedActionDto {
    processedAction: MatchActionDto;
    playerMode: number;
    updatedTurnInfo: TurnContextDto;
    overridingTransientBoard: CellDto[][] | null;
}