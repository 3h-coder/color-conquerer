import { CoordinatesDto } from "../misc/CoordinatesDto";

export interface ActionMetadataDto {
    // Spell castings have no originating coordinates
    originatingCellCoords: CoordinatesDto;
    impactedCoords: CoordinatesDto;
    deaths: CoordinatesDto[];
}