import { CellInfoDto } from "../../../dto/CellInfoDto";

export namespace BoardHelper {

    export function createBoardArray(size: number): CellInfoDto[][] {
        const boardArray: CellInfoDto[][] = new Array(size).fill(null).map((_, rowIndex) => 
            new Array(size).fill(null).map((_, columnIndex) => ({
                rowIndex,
                columnIndex
            }))
        );
        return boardArray;
    }

}
