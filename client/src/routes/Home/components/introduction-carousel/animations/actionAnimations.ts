import { animateCellClash } from "../../../../../board-animations/actions/attack";
import { animateCellMovement } from "../../../../../board-animations/actions/movement";
import { animateCellDeath, animateCellSpawn } from "../../../../../board-animations/common";
import { colors } from "../../../../../style/constants";
import { getHtmlCell } from "../../../../../utils/cellUtils";
import { delay } from "../../../../../utils/domUtils";
import { ActionsSetup, CellAttackSetup, CellMovementSetup, isCellAttackSetup, isCellMovementSetup, isSpawnSetup, SpawnSetup } from "../Setups/ActionsSetup";

export async function animationActionsSequence(actionsSetup: ActionsSetup, delayBetweenEachActionInMs: number) {
    for (const action of actionsSetup.actionsSequence) {
        if (isCellAttackSetup(action))
            await animateAttack(action);

        else if (isCellMovementSetup(action))
            animateMovement(action);

        else if (isSpawnSetup(action))
            animateSpawn(action);

        await delay(delayBetweenEachActionInMs);
    }
}

async function animateAttack(attack: CellAttackSetup) {
    const attackerCoords = attack.attackerCoords;
    const targetCoords = attack.targetCoords;
    await animateCellClash(attack.attackerCoords, attack.targetCoords, attack.metadata, false);

    const attackerCell = getHtmlCell(attackerCoords.rowIndex, attackerCoords.columnIndex);
    const targetCell = getHtmlCell(targetCoords.rowIndex, targetCoords.columnIndex);
    if (attackerCell !== null && attack.attackerDeath)
        animateCellDeath(attackerCell);
    if (targetCell !== null && attack.targetDeath)
        animateCellDeath(targetCell);
}

function animateMovement(movement: CellMovementSetup) {
    const originatingCoords = movement.originatingCoords;
    const targetCoords = movement.targetCoords;

    const cellToMove = getHtmlCell(originatingCoords.rowIndex, originatingCoords.columnIndex);
    const targetCell = getHtmlCell(targetCoords.rowIndex, targetCoords.columnIndex);
    if (!cellToMove || !targetCell)
        return;

    animateCellMovement(cellToMove, targetCell);

    const colorToApply = cellToMove.style.getPropertyValue("--bg");
    cellToMove.style.setProperty("--bg", "white");
    targetCell.style.setProperty("--bg", colorToApply);
}

function animateSpawn(spawn: SpawnSetup) {
    const { rowIndex, columnIndex } = spawn.coordinates;
    const cell = getHtmlCell(rowIndex, columnIndex);
    if (!cell)
        return;

    cell.style.setProperty("--bg", colors.cell.ownCellFreshlySpawned);
    animateCellSpawn(rowIndex, columnIndex, true);
}