import { CoordinatesDto } from "../../../../../dto/misc/CoordinatesDto";
import { CellAttacksSetup } from "./ActionsSetup";
import { GridCoordSetup } from "./CellCoordSetup";
import { FakeGameGridSetup } from "./FakeGameGridSetup";

export function getFullSetup1() {
    const player1MasterCoords: CoordinatesDto = { rowIndex: 5, columnIndex: 4 };
    const player2MasterCoords: CoordinatesDto = { rowIndex: 4, columnIndex: 5 };

    const coordSetup: GridCoordSetup = {
        player1MasterCoords: player1MasterCoords,
        player2MasterCoords: player2MasterCoords,
        player1MinionCellsCoords: [
            { rowIndex: 5, columnIndex: 5 },
            { rowIndex: 4, columnIndex: 6 },
            { rowIndex: 4, columnIndex: 3 },
            { rowIndex: 5, columnIndex: 3 },
            { rowIndex: 6, columnIndex: 3 }
        ],
        player2MinionCellsCoords: [
            { rowIndex: 4, columnIndex: 4 },
            { rowIndex: 5, columnIndex: 6 },
            { rowIndex: 6, columnIndex: 5 }
        ]
    };

    const attacksSetup: CellAttacksSetup = {
        cellAttacks: [
            { attackerCoords: player1MasterCoords, targetCoords: player2MasterCoords }
        ],
        deaths: []
    };


    const fullSetup: FakeGameGridSetup = {
        coordinatesSetup: coordSetup,
        cellAttacksSetup: attacksSetup
    };

    return fullSetup;
}