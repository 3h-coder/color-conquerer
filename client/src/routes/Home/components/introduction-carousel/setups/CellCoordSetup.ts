import { CoordinatesDto } from "../../../../../dto/misc/CoordinatesDto";
import { CellSetup } from "./CellSetup";

export interface GameBoardSetup {
    player1MasterCoords: CoordinatesDto;
    player2MasterCoords: CoordinatesDto;
    player1MinionCellsCoords: CellSetup[];
    player2MinionCellsCoords: CellSetup[];
}


