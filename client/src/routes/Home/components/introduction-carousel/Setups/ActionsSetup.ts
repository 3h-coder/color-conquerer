import { CellAttackMetadataDto } from "../../../../../dto/actions/CellAttackMetadataDto";
import { CoordinatesDto } from "../../../../../dto/misc/CoordinatesDto";

export interface ActionsSetup {
    actionsSequence: (CellAttackSetup | CellMovementSetup | SpawnSetup)[];
}

export interface CellAttackSetup {
    attackerCoords: CoordinatesDto;
    targetCoords: CoordinatesDto;
    attackerDeath: boolean;
    targetDeath: boolean;
    metadata: CellAttackMetadataDto;
}

export interface CellMovementSetup {
    originatingCoords: CoordinatesDto;
    targetCoords: CoordinatesDto;
}

export interface SpawnSetup {
    coordinates: CoordinatesDto;
}

export function isCellAttackSetup(action: unknown) {
    return (
        typeof action === "object" && action !== null &&
        "attackerCoords" in action &&
        "targetCoords" in action &&
        "attackerDeath" in action &&
        "targetDeath" in action &&
        "metadata" in action
    );
}

export function isCellMovementSetup(action: unknown) {
    return (
        typeof action === "object" && action !== null &&
        "originatingCoords" in action &&
        "targetCoords" in action
    );
}

export function isSpawnSetup(action: unknown) {
    return (
        typeof action === "object" && action !== null &&
        "coordinates" in action
    );
}