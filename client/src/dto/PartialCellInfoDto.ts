import { CellState, CellTransientState } from "../enums/cellStates";

export interface CellDto {
    owner: number;
    isMaster: boolean;
    rowIndex: number;
    columnIndex: number;
    state: CellState;
    transientState: CellTransientState;
}