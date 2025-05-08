import { ActionsSetup } from "./ActionsSetup";
import { GridCoordSetup as CellCoordSetup } from "./CellCoordSetup";

export interface FakeGameGridSetup {
    coordinatesSetup: CellCoordSetup;
    actionsSetup: ActionsSetup;
}