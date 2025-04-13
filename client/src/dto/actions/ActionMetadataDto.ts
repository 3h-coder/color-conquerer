import { CoordinatesDto } from "../misc/CoordinatesDto";
import { PositioningInfoDto } from "../spell/metadata/PositioningInfoDto";

export interface ActionMetadataDto {
    originatingCellCoords: CoordinatesDto;
    impactedCoords: CoordinatesDto;
    positioningInfo: PositioningInfoDto;
}