import { PartialCellInfoDto } from "./PartialCellInfoDto";
import { PartialMatchActionDto } from "./PartialMatchActionDto";
import { TurnInfoDto } from "./TurnInfoDto";

export interface ProcessedActionDto {
    processedAction: PartialMatchActionDto;
    playerMode: number;
    updatedTurnInfo: TurnInfoDto;
    overridingTransientBoard: PartialCellInfoDto[][] | null;
}