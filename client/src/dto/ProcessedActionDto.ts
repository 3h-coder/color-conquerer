import { CellDto } from "./CellDto";
import { PartialMatchActionDto } from "./PartialMatchActionDto";
import { TurnInfoDto } from "./TurnInfoDto";

export interface ProcessedActionDto {
    processedAction: PartialMatchActionDto;
    playerMode: number;
    updatedTurnInfo: TurnInfoDto;
    overridingTransientBoard: CellDto[][] | null;
}