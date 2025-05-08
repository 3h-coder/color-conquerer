import { CoordinatesDto } from "../../../../../dto/misc/CoordinatesDto";
import { CellAttackSetup, CellMovementSetup, SpawnSetup } from "./ActionsSetup";
import { GridCoordSetup } from "./CellCoordSetup";
import { FakeGameGridSetup } from "./FakeGameGridSetup";

export function getFullSetup1() {
    const player1MasterCoords: CoordinatesDto = { rowIndex: 5, columnIndex: 4 };
    const player2MasterCoords: CoordinatesDto = { rowIndex: 4, columnIndex: 5 };

    const player1CellCoords1: CoordinatesDto = { rowIndex: 5, columnIndex: 5 };
    const player1CellCoords2: CoordinatesDto = { rowIndex: 4, columnIndex: 6 };
    const player1CellCoords3: CoordinatesDto = { rowIndex: 4, columnIndex: 3 };

    const player2CellCoords1: CoordinatesDto = { rowIndex: 5, columnIndex: 6 };
    const player2CellCoords2: CoordinatesDto = { rowIndex: 6, columnIndex: 5 };
    const player2CellCoords3: CoordinatesDto = { rowIndex: 4, columnIndex: 4 };


    const coordSetup: GridCoordSetup = {
        player1MasterCoords: player1MasterCoords,
        player2MasterCoords: player2MasterCoords,
        player1MinionCellsCoords: [
            player1CellCoords1,
            player1CellCoords2,
            player1CellCoords3,
            { rowIndex: 5, columnIndex: 3 },
            { rowIndex: 6, columnIndex: 3 }
        ],
        player2MinionCellsCoords: [
            player2CellCoords1,
            player2CellCoords2,
            player2CellCoords3,
        ]
    };

    const attackSetups: CellAttackSetup[] = [
        {
            attackerCoords: player1MasterCoords,
            targetCoords: player2MasterCoords,
            attackerDeath: false,
            targetDeath: false,
            metadata: {
                isRangedAttack: false,
                isRetaliated: true,
            }
        },
        {
            attackerCoords: player1CellCoords1,
            targetCoords: player2CellCoords1,
            attackerDeath: true,
            targetDeath: true,
            metadata: {
                isRangedAttack: false,
                isRetaliated: true,
            }
        },
        {
            attackerCoords: player1CellCoords1,
            targetCoords: player2CellCoords2,
            attackerDeath: true,
            targetDeath: true,
            metadata: {
                isRangedAttack: false,
                isRetaliated: true
            }
        },
        {
            attackerCoords: player1CellCoords3,
            targetCoords: player2CellCoords3,
            attackerDeath: true,
            targetDeath: true,
            metadata: {
                isRangedAttack: false,
                isRetaliated: true,
            }
        }
    ];

    const movementSetups: CellMovementSetup[] = [
        {
            originatingCoords: player1CellCoords2,
            targetCoords: player1CellCoords1
        },
        {
            originatingCoords: player1MasterCoords,
            targetCoords: { rowIndex: 5, columnIndex: 2 }
        }
    ];

    const spawnSetups: SpawnSetup[] = [
        {
            coordinates: player1CellCoords3
        },
        {
            coordinates: player2CellCoords3
        },
        {
            coordinates: player1MasterCoords
        }
    ];


    const fullSetup: FakeGameGridSetup = {
        coordinatesSetup: coordSetup,
        actionsSetup: {
            actionsSequence: [
                attackSetups[0],
                attackSetups[1],
                movementSetups[0],
                attackSetups[2],
                attackSetups[3],
                movementSetups[1],
                ...spawnSetups
            ]
        }
    };

    return fullSetup;
}