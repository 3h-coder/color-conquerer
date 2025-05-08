import {
    CellAttackMetadataDto,
    isCellAttackMetadataDto,
} from "../../dto/actions/CellAttackMetadataDto";
import { MatchActionDto } from "../../dto/actions/MatchActionDto";
import { CoordinatesDto } from "../../dto/misc/CoordinatesDto";
import { EMPTY_STRING, HTMLElements } from "../../env";
import { getHtmlCell } from "../../utils/cellUtils";
import { cleanup, delay, getElementCenterPoint } from "../../utils/domUtils";
import { triggerAuraEffect } from "../common";

export async function handleCellClashAnimation(action: MatchActionDto, isPlayer1: boolean) {
    const attackerCoords = action.metadata.originatingCellCoords;
    if (!attackerCoords) return;

    const targetCoords = action.metadata.impactedCoords;
    let cellAttackMetadata: CellAttackMetadataDto | null = null;
    if (isCellAttackMetadataDto(action.specificMetadata)) {
        cellAttackMetadata = action.specificMetadata;
    }

    await animateCellClash(
        attackerCoords,
        targetCoords,
        cellAttackMetadata,
        isPlayer1
    );
}

export async function animateCellClash(
    attackerCoords: CoordinatesDto, targetCoords: CoordinatesDto, cellAttackMetadata: CellAttackMetadataDto | null, isPlayer1: boolean) {
    if (!cellAttackMetadata) return;

    const { rowIndex: attackerRowIndex, columnIndex: attackerColIndex } = attackerCoords;
    const { rowIndex: targetRowIndex, columnIndex: targetColIndex } = targetCoords;
    const attackerCell = getHtmlCell(attackerRowIndex, attackerColIndex);
    const targetCell = getHtmlCell(targetRowIndex, targetColIndex);

    if (!attackerCell || !targetCell) return;

    if (!cellAttackMetadata.isRangedAttack) {
        await animateMeleeAttack(attackerCell, targetCell, isPlayer1);
    } else {
        await displayProjectileEffect(attackerCell, targetCell);
        if (cellAttackMetadata.isRetaliated) {
            await delay(300);
            await displayProjectileEffect(targetCell, attackerCell);
        }
    }
}

function animateMeleeAttack(attackerCell: HTMLElement, targetCell: HTMLElement, isPlayer1: boolean): Promise<void> {
    return new Promise((resolve) => {
        const attackerCenter = getElementCenterPoint(attackerCell);
        const targetCenter = getElementCenterPoint(targetCell);
        const coefficient = isPlayer1 ? 1 : -1;

        // Calculate direction vector and normalize it
        const directionX = targetCenter.x - attackerCenter.x;
        const directionY = targetCenter.y - attackerCenter.y;
        const magnitude = Math.sqrt(directionX * directionX + directionY * directionY);
        const normalizedX = directionX / magnitude;
        const normalizedY = directionY / magnitude;
        // Make sure the attacker cell is on top of the target cell during the animation
        attackerCell.style.setProperty("z-index", "10");

        // Create the animation
        const animation = attackerCell.animate(
            [
                // Starting position
                { transform: 'translate(0, 0)', offset: 0 },
                // Wind up (move back slightly)
                { transform: `translate(${coefficient * normalizedX * 10}px, ${coefficient * normalizedY * 10}px)`, offset: 0.2 },
                // Hold position briefly
                { transform: `translate(${coefficient * normalizedX * 10}px, ${coefficient * normalizedY * 10}px)`, offset: 0.3 },
                // Attack (move towards target)
                { transform: `translate(${-coefficient * normalizedX * 20}px, ${-coefficient * normalizedY * 20}px)`, offset: 0.7 },
                // Return to original position
                { transform: 'translate(0, 0)', offset: 1 }
            ],
            {
                duration: 500,
                easing: 'ease-in-out',
            }
        );

        animation.onfinish = () => {
            triggerCellAura(attackerCell);
            triggerCellAura(targetCell);
            attackerCell.style.setProperty("z-index", EMPTY_STRING);
            resolve();
        };
    });
}

function triggerCellAura(htmlCell: HTMLElement) {
    triggerAuraEffect(
        htmlCell,
        () => getComputedStyle(htmlCell).backgroundColor
    );
}

async function displayProjectileEffect(attackerCell: HTMLElement, targetCell: HTMLElement) {
    const projectile = document.createElement(HTMLElements.div);
    projectile.classList.add("projectile-effect");

    const attackerCenter = getElementCenterPoint(attackerCell);
    const targetCenter = getElementCenterPoint(targetCell);

    projectile.style.left = `${attackerCenter.x}px`;
    projectile.style.top = `${attackerCenter.y}px`;
    document.body.appendChild(projectile);

    const distanceX = targetCenter.x - attackerCenter.x;
    const distanceY = targetCenter.y - attackerCenter.y;
    const distance = Math.sqrt(distanceX ** 2 + distanceY ** 2);
    const durationInMs = Math.min(1000, distance * 2);

    projectile.animate(
        [
            { transform: `translate(0, 0)` },
            { transform: `translate(${distanceX}px, ${distanceY}px)` },
        ],
        {
            duration: durationInMs,
            easing: "ease-in-out",
            fill: "forwards",
        }
    );

    cleanup(projectile, durationInMs);

    await delay(durationInMs);
    triggerCellAura(targetCell);
}

