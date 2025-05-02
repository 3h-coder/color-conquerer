import { MatchActionDto } from "../actions/MatchActionDto";
import { CellDto } from "../cell/CellDto";
import { GameContextDto } from "../gameState/GameContextDto";

export interface ProcessedActionDto {
    processedAction: MatchActionDto;
    playerMode: number;
    updatedGameContext: GameContextDto;
    overridingTransientBoard: CellDto[][] | null;
}