import { CoordinatesDto } from "../../../../../dto/misc/CoordinatesDto";

interface CellAttackSetup {
    attackerCoords: CoordinatesDto;
    targetCoords: CoordinatesDto;
}

export interface CellAttacksSetup {
    cellAttacks: CellAttackSetup[];
    deaths: CoordinatesDto[];
}