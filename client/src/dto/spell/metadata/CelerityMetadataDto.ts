import { CoordinatesDto } from "../../misc/CoordinatesDto";

export interface CelerityMetadataDto {
    diagonalPerCoordinates: Record<string, number>;
    diagonals: CoordinatesDto[][];
}

export function isCelerityMetadataDto(data: unknown) {
    return data !== null &&
        typeof data === "object" &&
        "diagonalPerCoordinates" in data &&
        "diagonals" in data &&
        Array.isArray((data as CelerityMetadataDto).diagonals) &&
        (data as CelerityMetadataDto).diagonals.every(Array.isArray);
}