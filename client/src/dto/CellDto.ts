import { CellHiddenState } from "../enums/cellHiddenState";
import { CellState } from "../enums/cellState";
import { CellTransientState } from "../enums/cellTransientState";

export interface CellDto {
    owner: number;
    isMaster: boolean;
    rowIndex: number;
    columnIndex: number;
    state: CellState;
    hiddenState: CellHiddenState;
    transientState: CellTransientState;
}