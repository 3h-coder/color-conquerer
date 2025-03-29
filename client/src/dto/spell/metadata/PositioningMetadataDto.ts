import { CoordinatesDto } from "../../misc/CoordinatesDto";

export interface PositioningMetadataDto {
    formationPerCoordinates: Record<string, number>;
    cellFormations: CoordinatesDto[][];
}

export function isPositioningMetadataDto(data: unknown) {
    return data !== null &&
        typeof data === "object" &&
        "formationPerCoordinates" in data &&
        "cellFormations" in data &&
        Array.isArray((data as PositioningMetadataDto).cellFormations) &&
        (data as PositioningMetadataDto).cellFormations.every(Array.isArray);
}