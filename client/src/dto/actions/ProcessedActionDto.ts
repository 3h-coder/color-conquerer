import { MatchActionDto } from "../actions/MatchActionDto";
import { GameContextDto } from "../gameState/GameContextDto";
import { CellDto } from "../misc/CellDto";

export interface ProcessedActionDto {
    processedAction: MatchActionDto;
    playerMode: number;
    updatedGameContext: GameContextDto;
    overridingTransientBoard: CellDto[][] | null;
}