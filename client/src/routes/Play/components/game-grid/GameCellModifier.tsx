import { useEffect, useRef } from "react";
import { LandMineIcon, SwordIcon } from "../../../../assets/svg";
import { CellDto } from "../../../../dto/misc/CellDto";
import { CellHiddenState } from "../../../../enums/cellHiddenState";
import { CellState, CellStateUtils } from "../../../../enums/cellState";
import { CellTransientState } from "../../../../enums/cellTransientState";
import { EMPTY_STRING } from "../../../../env";
import { cellStyle } from "../../../../style/constants";
import { isOwnedAndCanBeSpellTargetted } from "../../../../utils/cellUtils";
import { bindTooltip } from "../../../../utils/tooltipUtils";

interface GameCellModifierProps {
    cellInfo: CellDto;
    isPlayer1: boolean;
}

/**
 * Returns all the HTML elements that represent a cell modifier.
 */
export default function GameCellModifier(props: GameCellModifierProps) {
    const { cellInfo, isPlayer1 } = props;

    const selected = cellInfo.transientState === CellTransientState.SELECTED;
    const attackable =
        cellInfo.transientState === CellTransientState.CAN_BE_ATTACKED;
    const isManaBubble = CellStateUtils.contains(
        cellInfo.state,
        CellState.MANA_BUBBLE
    );
    const isMineTrap = cellInfo.hiddenState == CellHiddenState.MINE_TRAP;
    const isShielded = CellStateUtils.contains(
        cellInfo.state,
        CellState.SHIELDED
    );
    const isAccelerated = CellStateUtils.contains(
        cellInfo.state,
        CellState.ACCELERATED
    );
    // If not owned, a background color is being applied to the cell instead
    const ownedAndCanBeSpellTargetted = isOwnedAndCanBeSpellTargetted(cellInfo);

    return (
        <>
            {selected && <SelectedIndicator />}
            {attackable && <AttackableIndicator rotateIcon={isPlayer1} />}
            {isManaBubble && <ManaBubble />}
            {isMineTrap && <LandMine rotateIcon={isPlayer1} isBlinking={false} />}
            {isShielded && <Shield />}
            {ownedAndCanBeSpellTargetted && <SpellTargetIndicator />}
            {isAccelerated && <WindSpiral />}
        </>
    );
}

interface WithIconProps {
    rotateIcon: boolean;
}

function SelectedIndicator() {
    return (
        <div className="selected-indicator" />
    );
}

function AttackableIndicator(props: WithIconProps) {
    const { rotateIcon } = props;
    const rotateStyle = rotateIcon ? cellStyle.rotate180deg : undefined;

    return (
        <div className={`attackable-indicator ${cellStyle.classNames.absPosition}`}>
            <SwordIcon style={{ transform: rotateStyle }} />
        </div>
    );
}

function SpellTargetIndicator() {
    return (
        <div className="possible-spell-target-indicator" />
    );
}

function ManaBubble() {
    const bubbleRef = useRef<HTMLDivElement>(null);
    const description =
        "Gain an extra mana point when moving to this cell or spawning on it";

    useEffect(() => {
        const cleanup = bindTooltip(bubbleRef, {
            tooltipText: description,
        });
        return cleanup;
    }, [description, bubbleRef]);

    return (
        <div className="mana-bubble" ref={bubbleRef}>
        </div>
    );
}

interface LandMineProps extends WithIconProps {
    isBlinking: boolean;
}

export function LandMine(props: LandMineProps) {
    const { rotateIcon, isBlinking } = props;

    const blinkStyle: React.CSSProperties = {
        ["--color1" as string]: "black",
        ["--color2" as string]: "red",
        ["--frequency" as string]: "0.2s",
    };

    return (
        <div className={`land-mine ${cellStyle.classNames.absPosition}`}>
            <LandMineIcon
                style={{
                    fill: "black",
                    transform: rotateIcon ? cellStyle.rotate180deg : undefined,
                    animation: isBlinking ? "fill-blink 0.2s infinite" : EMPTY_STRING,
                    ...blinkStyle,
                }}
            />
        </div>
    );
}

export function Shield() {
    return (
        <div className="shield" />
    );
}

export function WindSpiral() {
    const trailCount = 50; // Number of trail elements
    const trailElements = Array.from({ length: trailCount }, (_, index) => {
        const delay = `${index * 0.006}s`; // Staggered animation delay
        const opacity = 1 - index * 0.1; // Gradually decrease opacity

        return (
            <div
                key={index}
                className="wind-spiral-trail"
                style={{
                    animationDelay: delay,
                    opacity: opacity,
                }}
            />
        );
    });

    return (
        <div className="wind-spiral">
            {trailElements}
        </div>
    );
}