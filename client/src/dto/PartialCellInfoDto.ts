import { CellState, CellTransientState } from "../enums/cellStates";

export interface PartialCellInfoDto {
    owner: number;
    isMaster: boolean;
    rowIndex: number;
    columnIndex: number;
    state: CellState;
    transientState: CellTransientState;
}