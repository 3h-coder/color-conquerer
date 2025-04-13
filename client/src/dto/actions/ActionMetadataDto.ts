import { CoordinatesDto } from "../misc/CoordinatesDto";
import { PositioningInfoDto } from "../spell/metadata/PositioningInfoDto";

export interface ActionMetadataDto {
    // Spell castings have no originating coordinates
    originatingCellCoords: CoordinatesDto;
    impactedCoords: CoordinatesDto;
    positioningInfo: PositioningInfoDto;
}