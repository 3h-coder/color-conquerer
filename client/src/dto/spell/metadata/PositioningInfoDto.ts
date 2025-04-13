import { CoordinatesDto } from "../../misc/CoordinatesDto";

export interface PositioningInfoDto {
    formationPerCoordinates: Record<string, number>;
    cellFormations: CoordinatesDto[][];
}

export function isPositioningInfoDto(data: unknown) {
    return data !== null &&
        typeof data === "object" &&
        "formationPerCoordinates" in data &&
        "cellFormations" in data &&
        Array.isArray((data as PositioningInfoDto).cellFormations) &&
        (data as PositioningInfoDto).cellFormations.every(Array.isArray);
}