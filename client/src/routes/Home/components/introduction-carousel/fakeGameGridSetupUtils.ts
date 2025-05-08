import { CellDto } from "../../../../dto/cell/CellDto";
import { CellHiddenState } from "../../../../enums/cellHiddenState";
import { CellOwner } from "../../../../enums/cellOwner";
import { CellState } from "../../../../enums/cellState";
import { CellTransientState } from "../../../../enums/cellTransientState";
import { create2DArray } from "../../../../utils/arrayUtils";
import { GridCoordSetup } from "./Setups/CellCoordSetup";

export function getDefaultGameGrid(setup: GridCoordSetup) {
    const board_size = 11;

    const array = create2DArray<CellDto>(board_size);
    const filledArray = array.map((row, rowIndex) =>
        row.map((_, columnIndex) =>
            getDefaultCellDto(rowIndex, columnIndex)
        )
    );
    setupPlayerCells(filledArray, setup);
    return filledArray;
}

function setupPlayerCells(boardArray: CellDto[][], setup: GridCoordSetup) {
    // Player 1 cells
    // 5, 4
    const player1MasterCell = boardArray[setup.player1MasterCoords.rowIndex][setup.player1MasterCoords.columnIndex];
    player1MasterCell.isMaster = true;
    player1MasterCell.owner = CellOwner.PLAYER_1;

    //const player1CellCoordinates: number[][] = [[5, 5], [4, 6], [4, 3], [5, 3], [6, 3]];
    const player1CellCoordinates = setup.player1MinionCellsCoords;
    player1CellCoordinates.forEach(coords => {
        const playerMinionCell = boardArray[coords.rowIndex][coords.columnIndex];
        playerMinionCell.owner = CellOwner.PLAYER_1;
    });

    // Player 2 cells
    // 4, 5
    const player2MasterCell = boardArray[setup.player2MasterCoords.rowIndex][setup.player2MasterCoords.columnIndex];
    player2MasterCell.isMaster = true;
    player2MasterCell.owner = CellOwner.PLAYER_2;

    //const player2CellCoordinates: number[][] = [[4, 4], [5, 6], [6, 5]]; 
    const player2CellCoordinates = setup.player2MinionCellsCoords;
    player2CellCoordinates.forEach(coords => {
        const playerMinionCell = boardArray[coords.rowIndex][coords.columnIndex];
        playerMinionCell.owner = CellOwner.PLAYER_2;
    });
}

function getDefaultCellDto(rowIndex: number, columnIndex: number) {
    const cellDto: CellDto = {
        rowIndex: rowIndex,
        columnIndex: columnIndex,
        isMaster: false,
        hiddenState: CellHiddenState.NONE,
        owner: CellOwner.NONE,
        state: CellState.NONE,
        transientState: CellTransientState.NONE,
    };

    return cellDto;
}
