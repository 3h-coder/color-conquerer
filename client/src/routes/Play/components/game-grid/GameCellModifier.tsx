import { LandMineIcon, SwordIcon } from "../../../../assets/svg";
import { CellDto } from "../../../../dto/misc/CellDto";
import { CellHiddenState } from "../../../../enums/cellHiddenState";
import { CellState, CellStateUtils } from "../../../../enums/cellState";
import { CellTransientState } from "../../../../enums/cellTransientState";
import { EMPTY_STRING } from "../../../../env";
import { cellStyle } from "../../../../style/constants";
import { isOwnedAndCanBeSpellTargetted } from "../../../../utils/cellUtils";

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
    // If not owned, a background color is being applied to the cell instead
    const ownedAndCanBeSpellTargetted = isOwnedAndCanBeSpellTargetted(cellInfo);

    return (
        <>
            {selected && <SelectedIndicator />}
            {attackable && <AttackableIndicator rotateIcon={isPlayer1} />}
            {isManaBubble && <ManaBubble rotateIcon={isPlayer1} />}
            {isMineTrap && <LandMine rotateIcon={isPlayer1} isBlinking={false} />}
            {isShielded && <Shield />}
            {ownedAndCanBeSpellTargetted && <SpellTargetIndicator />}
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

function ManaBubble(props: WithIconProps) {
    const { rotateIcon } = props;
    const rotateStyle = rotateIcon ? cellStyle.rotate180deg : undefined;
    const description =
        "Gain an extra mana point when moving to this cell or spawning on it";

    return (
        <div className="mana-bubble">
            <div className="mana-bubble-description">
                <div style={{ transform: rotateStyle }}>{description}</div>
            </div>
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
        <div className={`shield `}>
        </div>
    );
}
