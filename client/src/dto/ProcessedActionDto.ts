import { CellDto } from "./CellDto";
import { MatchActionDto } from "./MatchActionDto";
import { TurnContextDto } from "./TurnContextDto";

export interface ProcessedActionDto {
    processedAction: MatchActionDto;
    playerMode: number;
    updatedTurnContext: TurnContextDto;
    overridingTransientBoard: CellDto[][] | null;
}