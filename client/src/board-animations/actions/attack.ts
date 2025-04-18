import {
    CellAttackMetadataDto,
    isCellAttackMetadataDto,
} from "../../dto/actions/CellAttackMetadataDto";
import { MatchActionDto } from "../../dto/actions/MatchActionDto";
import { CoordinatesDto } from "../../dto/misc/CoordinatesDto";
import { HTMLElements } from "../../env";
import { getHtmlCell } from "../../utils/cellUtils";
import { delay } from "../../utils/domUtils";
import { triggerAuraEffect } from "../common";

export async function handleCellClashAnimation(action: MatchActionDto) {
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
        cellAttackMetadata
    );
}

async function animateCellClash(
    attackerCoords: CoordinatesDto,
    targetCoords: CoordinatesDto,
    cellAttackMetadata: CellAttackMetadataDto | null
) {
    if (!cellAttackMetadata) return;

    const { rowIndex: attackerRowIndex, columnIndex: attackerColIndex } = attackerCoords;
    const { rowIndex: targetRowIndex, columnIndex: targetColIndex } = targetCoords;
    const attackerCell = getHtmlCell(attackerRowIndex, attackerColIndex);
    const targetCell = getHtmlCell(targetRowIndex, targetColIndex);

    if (!attackerCell || !targetCell) return;

    if (!cellAttackMetadata.isRangedAttack) {
        triggerCellAura(attackerCell);
        triggerCellAura(targetCell);
    } else {
        await displayProjectileEffect(attackerCell, targetCell);
        if (cellAttackMetadata.isRetaliated) {
            await delay(300);
            await displayProjectileEffect(targetCell, attackerCell);
        }
    }
}
function triggerCellAura(attackerCell: HTMLElement) {
    triggerAuraEffect(
        attackerCell,
        () => getComputedStyle(attackerCell).backgroundColor
    );
}

async function displayProjectileEffect(attackerCell: HTMLElement, targetCell: HTMLElement) {
    const projectile = document.createElement(HTMLElements.div);
    projectile.classList.add("projectile-effect");

    const attackerRect = attackerCell.getBoundingClientRect();
    const targetRect = targetCell.getBoundingClientRect();

    const startX = attackerRect.left + attackerRect.width / 2;
    const startY = attackerRect.top + attackerRect.height / 2;
    const endX = targetRect.left + targetRect.width / 2;
    const endY = targetRect.top + targetRect.height / 2;

    projectile.style.left = `${startX}px`;
    projectile.style.top = `${startY}px`;
    document.body.appendChild(projectile);

    const distanceX = endX - startX;
    const distanceY = endY - startY;
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

    setTimeout(() => {
        projectile.remove();
    }, durationInMs);

    await delay(durationInMs);
    triggerCellAura(targetCell);
}

