import { CellHiddenState } from "../../enums/cellHiddenState";
import { CellOwner } from "../../enums/cellOwner";
import { CellState } from "../../enums/cellState";
import { CellTransientState } from "../../enums/cellTransientState";

export interface CellDto {
    owner: CellOwner;
    isMaster: boolean;
    rowIndex: number;
    columnIndex: number;
    state: CellState;
    hiddenState: CellHiddenState;
    transientState: CellTransientState;
}