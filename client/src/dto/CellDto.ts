import { CellHiddenState, CellState, CellTransientState } from "../enums/cellState";

export interface CellDto {
    owner: number;
    isMaster: boolean;
    rowIndex: number;
    columnIndex: number;
    state: CellState;
    hiddenState: CellHiddenState;
    transientState: CellTransientState;
}