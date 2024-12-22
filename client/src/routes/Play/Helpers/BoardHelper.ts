import { PartialCellInfoDto } from "../../../dto/PartialCellInfoDto";

export function createBoardArray(size: number): PartialCellInfoDto[][] {
    const boardArray: PartialCellInfoDto[][] = new Array(size).fill(null).map((_, rowIndex) =>
        new Array(size).fill(null).map((_, columnIndex) => ({
            rowIndex,
            columnIndex
        }))
    );
    return boardArray;
}



