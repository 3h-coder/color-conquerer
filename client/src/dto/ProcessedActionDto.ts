import { PartialMatchActionDto } from "./PartialMatchActionDto";
import { PartialMatchInfoDto } from "./PartialMatchInfoDto";

export interface ProcessedActionDto {
    processedAction: PartialMatchActionDto;
    playerMode: number;
    updatedMatchInfo: PartialMatchInfoDto;
}