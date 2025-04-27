import { CoordinatesDto } from "../../misc/CoordinatesDto";

export interface SpawnInfoDto {
    coordinates: CoordinatesDto[];
}

export function isSpawnInfoDto(obj: unknown) {
    return (
        typeof obj === "object" &&
        obj !== null &&
        "coordinates" in obj &&
        Array.isArray((obj as SpawnInfoDto).coordinates)
    );
}
