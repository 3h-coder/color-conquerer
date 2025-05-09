import { CellState } from "../../../../../enums/cellState";
import { CellAttackSetup, CellMovementSetup, SpawnSetup } from "./ActionsSetup";
import { GameBoardSetup } from "./CellCoordSetup";
import { CellSetup } from "./CellSetup";
import { FakeGameGridSetup } from "./FakeGameGridSetup";

function getFullSetup1() {
    const player1MasterCoords: CellSetup = { rowIndex: 5, columnIndex: 4 };
    const player2MasterCoords: CellSetup = { rowIndex: 4, columnIndex: 5 };

    const player1CellSetup1: CellSetup = { rowIndex: 5, columnIndex: 5 };
    const player1CellSetup2: CellSetup = { rowIndex: 4, columnIndex: 6 };
    const player1CellSetup3: CellSetup = { rowIndex: 4, columnIndex: 3 };

    const player2CellSetup1: CellSetup = { rowIndex: 5, columnIndex: 6 };
    const player2CellSetup2: CellSetup = { rowIndex: 6, columnIndex: 5 };
    const player2CellSetup3: CellSetup = { rowIndex: 4, columnIndex: 4 };


    const coordSetup: GameBoardSetup = {
        player1MasterCoords: player1MasterCoords,
        player2MasterCoords: player2MasterCoords,
        player1MinionCellsCoords: [
            player1CellSetup1,
            player1CellSetup2,
            player1CellSetup3,
            { rowIndex: 5, columnIndex: 3 },
            { rowIndex: 6, columnIndex: 3 }
        ],
        player2MinionCellsCoords: [
            player2CellSetup1,
            player2CellSetup2,
            player2CellSetup3,
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
            attackerCoords: player1CellSetup1,
            targetCoords: player2CellSetup1,
            attackerDeath: true,
            targetDeath: true,
            metadata: {
                isRangedAttack: false,
                isRetaliated: true,
            }
        },
        {
            attackerCoords: player1CellSetup1,
            targetCoords: player2CellSetup2,
            attackerDeath: true,
            targetDeath: true,
            metadata: {
                isRangedAttack: false,
                isRetaliated: true
            }
        },
        {
            attackerCoords: player1CellSetup3,
            targetCoords: player2CellSetup3,
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
            originatingCoords: player1CellSetup2,
            targetCoords: player1CellSetup1
        },
        {
            originatingCoords: player1MasterCoords,
            targetCoords: { rowIndex: 5, columnIndex: 2 }
        }
    ];

    const spawnSetups: SpawnSetup[] = [
        {
            coordinates: player1CellSetup3
        },
        {
            coordinates: player2CellSetup3
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

function getFullSetup2() {
    const player1MasterCoords: CellSetup = { rowIndex: 4, columnIndex: 7 };
    const player2MasterCoords: CellSetup = { rowIndex: 3, columnIndex: 5 };

    const player1CellSetup1: CellSetup = { rowIndex: 9, columnIndex: 9, state: CellState.ARCHER + CellState.ACCELERATED };
    const player1CellSetup2: CellSetup = { rowIndex: 10, columnIndex: 10, state: CellState.ARCHER + CellState.ACCELERATED };
    const player1CellSetup3: CellSetup = { rowIndex: 3, columnIndex: 6 };
    const player1CellSetup4: CellSetup = { rowIndex: 4, columnIndex: 6 };
    const player1CellSetup5: CellSetup = { rowIndex: 5, columnIndex: 6 };
    const player1CellSetup6: CellSetup = { rowIndex: 6, columnIndex: 7 };

    const player2CellSetup1: CellSetup = { rowIndex: 2, columnIndex: 6 };
    const player2CellSetup2: CellSetup = { rowIndex: 4, columnIndex: 5 };
    const player2CellSetup3: CellSetup = { rowIndex: 5, columnIndex: 5 };
    const player2CellSetup4: CellSetup = { rowIndex: 5, columnIndex: 7 };

    const coordSetup: GameBoardSetup = {
        player1MasterCoords: player1MasterCoords,
        player2MasterCoords: player2MasterCoords,
        player1MinionCellsCoords: [
            player1CellSetup1,
            player1CellSetup2,
            player1CellSetup3,
            player1CellSetup4,
            player1CellSetup5,

        ],
        player2MinionCellsCoords: [
            player2CellSetup1,
            player2CellSetup2,
            player2CellSetup3,
            player2CellSetup4,
            { rowIndex: 3, columnIndex: 7, state: CellState.SHIELDED },
            { rowIndex: 4, columnIndex: 8, state: CellState.SHIELDED },
        ]
    };

    const attackSetups: CellAttackSetup[] = [
        {
            attackerCoords: player1CellSetup1,
            targetCoords: player2CellSetup1,
            attackerDeath: false,
            targetDeath: true,
            metadata: {
                isRangedAttack: true,
                isRetaliated: false
            }
        },
        {
            attackerCoords: player1CellSetup1,
            targetCoords: player2CellSetup2,
            attackerDeath: false,
            targetDeath: true,
            metadata: {
                isRangedAttack: true,
                isRetaliated: false
            }
        },
        {
            attackerCoords: player1CellSetup2,
            targetCoords: player2CellSetup3,
            attackerDeath: false,
            targetDeath: true,
            metadata: {
                isRangedAttack: true,
                isRetaliated: false
            }
        },
        {
            attackerCoords: player1CellSetup2,
            targetCoords: player2CellSetup4,
            attackerDeath: false,
            targetDeath: true,
            metadata: {
                isRangedAttack: true,
                isRetaliated: false
            }
        },
        {
            attackerCoords: player1CellSetup3,
            targetCoords: player2MasterCoords,
            attackerDeath: true,
            targetDeath: false,
            metadata: {
                isRangedAttack: false,
                isRetaliated: true
            }
        },
        {
            attackerCoords: player1CellSetup4,
            targetCoords: player2MasterCoords,
            attackerDeath: true,
            targetDeath: false,
            metadata: {
                isRangedAttack: false,
                isRetaliated: true
            }
        },
        {
            attackerCoords: player1CellSetup3,
            targetCoords: player2MasterCoords,
            attackerDeath: true,
            targetDeath: false,
            metadata: {
                isRangedAttack: false,
                isRetaliated: true
            }
        }
    ];

    const movementSetups: CellMovementSetup[] = [
        {
            originatingCoords: player1CellSetup5,
            targetCoords: player1CellSetup3,
        },
        {
            originatingCoords: player1MasterCoords,
            targetCoords: player1CellSetup6
        }
    ];

    const spawnSetups: SpawnSetup[] = [
        {
            coordinates: player2CellSetup4
        },
        {
            coordinates: player1CellSetup5
        },
    ];

    const fullSetup: FakeGameGridSetup = {
        coordinatesSetup: coordSetup,
        actionsSetup: {
            actionsSequence: [
                attackSetups[0],
                attackSetups[1],
                attackSetups[2],
                attackSetups[3],
                attackSetups[4],
                attackSetups[5],
                movementSetups[0],
                attackSetups[6],
                movementSetups[1],
                ...spawnSetups

            ]
        }
    };

    return fullSetup;
}

export const allSetups = [
    getFullSetup1(),
    getFullSetup2()
];