import { animateCellClash } from "../../../../../board-animations/actions/attack";
import { animateCellMovement } from "../../../../../board-animations/actions/movement";
import { animateCellDeath, animateCellSpawn } from "../../../../../board-animations/common";
import { cellStyle, colors } from "../../../../../style/constants";
import { getHtmlCell } from "../../../../../utils/cellUtils";
import { delay } from "../../../../../utils/domUtils";
import { BoolRef } from "../../../../../utils/typeAliases";
import { ActionsSetup, CellAttackSetup, CellMovementSetup, isCellAttackSetup, isCellMovementSetup, isSpawnSetup, SpawnSetup } from "../setups/ActionsSetup";

export async function animationActionsSequence(
    actionsSetup: ActionsSetup,
    delayBetweenEachActionInMs: number,
    gridId: string,
    isCancelled: BoolRef) {
    for (const action of actionsSetup.actionsSequence) {
        if (isCancelled.value)
            return;

        if (isCellAttackSetup(action))
            await animateAttack(action, gridId);

        else if (isCellMovementSetup(action))
            animateMovement(action, gridId);

        else if (isSpawnSetup(action))
            animateSpawn(action, gridId);

        await delay(delayBetweenEachActionInMs);
    }
}

async function animateAttack(attack: CellAttackSetup, gridId: string) {
    const attackerCoords = attack.attackerCoords;
    const targetCoords = attack.targetCoords;
    await animateCellClash(attack.attackerCoords, attack.targetCoords, attack.metadata, true, gridId);

    const attackerCell = getHtmlCell(attackerCoords.rowIndex, attackerCoords.columnIndex, gridId);
    const targetCell = getHtmlCell(targetCoords.rowIndex, targetCoords.columnIndex, gridId);
    if (attackerCell !== null && attack.attackerDeath)
        animateCellDeath(attackerCell);
    if (targetCell !== null && attack.targetDeath)
        animateCellDeath(targetCell);
}

function animateMovement(movement: CellMovementSetup, gridId: string) {
    const originatingCoords = movement.originatingCoords;
    const targetCoords = movement.targetCoords;

    const cellToMove = getHtmlCell(originatingCoords.rowIndex, originatingCoords.columnIndex, gridId);
    const targetCell = getHtmlCell(targetCoords.rowIndex, targetCoords.columnIndex, gridId);
    if (!cellToMove || !targetCell)
        return;

    animateCellMovement(cellToMove, targetCell);

    const colorToApply = cellToMove.style.getPropertyValue(cellStyle.variableNames.backgroundColor);
    cellToMove.style.setProperty(cellStyle.variableNames.backgroundColor, "white");
    targetCell.style.setProperty(cellStyle.variableNames.backgroundColor, colorToApply);
}

function animateSpawn(spawn: SpawnSetup, gridId: string) {
    const { rowIndex, columnIndex } = spawn.coordinates;
    const cell = getHtmlCell(rowIndex, columnIndex, gridId);
    if (!cell)
        return;

    cell.style.setProperty(cellStyle.variableNames.backgroundColor, colors.cell.ownCellFreshlySpawned);
    animateCellSpawn(rowIndex, columnIndex, true, gridId);
}