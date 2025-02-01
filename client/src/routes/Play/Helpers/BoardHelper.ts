import { CellDto } from "../../../dto/PartialCellInfoDto";

export function createBoardArray(size: number): CellDto[][] {
    const boardArray: CellDto[][] = new Array(size).fill(null).map((_, rowIndex) =>
        new Array(size).fill(null).map((_, columnIndex) => ({
            rowIndex,
            columnIndex
        }))
    );
    return boardArray;
}



