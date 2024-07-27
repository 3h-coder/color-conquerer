export interface CellInfoDto {
    owner?: number // either 1, 2 or undefined
    rowIndex: number;
    columnIndex: number;
    state?: number
}