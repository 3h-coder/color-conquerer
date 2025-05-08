import { CoordinatesDto } from "../../../../../dto/misc/CoordinatesDto";

export interface GridCoordSetup {
    player1MasterCoords: CoordinatesDto;
    player2MasterCoords: CoordinatesDto;
    player1MinionCellsCoords: CoordinatesDto[];
    player2MinionCellsCoords: CoordinatesDto[];
}

