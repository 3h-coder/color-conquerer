import { CellState } from "../enums/cellState";

export interface PartialCellInfoDto {
    owner: number;
    isMaster: boolean;
    rowIndex: number;
    columnIndex: number;
    state: CellState;
}