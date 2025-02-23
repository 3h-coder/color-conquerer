import { CellDto } from "./CellDto";
import { GameContextDto } from "./GameContextDto";
import { MatchActionDto } from "./MatchActionDto";

export interface ProcessedActionDto {
    processedAction: MatchActionDto;
    playerMode: number;
    updatedGameContext: GameContextDto;
    overridingTransientBoard: CellDto[][] | null;
}