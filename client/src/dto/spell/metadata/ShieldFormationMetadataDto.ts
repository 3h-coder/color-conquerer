import { CoordinatesDto } from "../../misc/CoordinatesDto";

export interface ShieldFormationMetadataDto {
    squarePerCoordinates: Record<string, number>;
    squares: CoordinatesDto[][];
}

export function isShieldFormationMetadata(data: unknown) {
    return (
        data !== null &&
        typeof data === 'object' &&
        'squarePerCoordinates' in data &&
        'squares' in data &&
        Array.isArray(data.squares)
    );
} 