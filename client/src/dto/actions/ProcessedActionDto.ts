import { MatchActionDto } from "../actions/MatchActionDto";
import { CellDto } from "./CellDto";
import { GameContextDto } from "./GameContextDto";

export interface ProcessedActionDto {
    processedAction: MatchActionDto;
    playerMode: number;
    updatedGameContext: GameContextDto;
    overridingTransientBoard: CellDto[][] | null;
}