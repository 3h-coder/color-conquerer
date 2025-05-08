import { CellAttacksSetup } from "./ActionsSetup";
import { GridCoordSetup as CellCoordSetup } from "./CellCoordSetup";

export interface FakeGameGridSetup {
    coordinatesSetup: CellCoordSetup;
    cellAttacksSetup: CellAttacksSetup;
}