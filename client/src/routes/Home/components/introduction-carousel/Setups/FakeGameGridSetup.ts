import { ActionsSetup } from "./ActionsSetup";
import { GameBoardSetup as CellCoordSetup } from "./CellCoordSetup";

export interface FakeGameGridSetup {
    coordinatesSetup: CellCoordSetup;
    actionsSetup: ActionsSetup;
}