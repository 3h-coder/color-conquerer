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
    const attackable = cellInfo.transientState === CellTransientState.CAN_BE_ATTACKED;
    const isManaBubble = CellStateUtils.contains(cellInfo.state, CellState.MANA_BUBBLE);
    const isMineTrap = cellInfo.hiddenState == CellHiddenState.MINE_TRAP;
    // If not owned, a background color is being applied to the cell instead
    const ownedAndCanBeSpellTargetted = isOwnedAndCanBeSpellTargetted(cellInfo);

    return (
        <>
            {selected && <SelectedIndicator />}
            {attackable && <AttackableIndicator isPlayer1={isPlayer1} />}
            {isManaBubble && <ManaBubble isPlayer1={isPlayer1} />}
            {isMineTrap && <LandMine isPlayer1={isPlayer1} isBlinking={false} />}
            {ownedAndCanBeSpellTargetted && <SpellTargetIndicator />}
        </>
    );

}

function SelectedIndicator() {
    return (
        <div className={`selected-indicator ${cellStyle.classNames.absPosition}`} />
    );
}

function AttackableIndicator({ isPlayer1 }: { isPlayer1: boolean; }) {
    const rotateStyle = isPlayer1 ? cellStyle.rotate180deg : undefined;

    return (
        <div className={`attackable-indicator ${cellStyle.classNames.absPosition}`}>
            <SwordIcon style={{ transform: rotateStyle }} />
        </div>
    );
}

function SpellTargetIndicator() {
    return <div className={`possible-spell-target-indicator ${cellStyle.classNames.absPosition}`} />;
}

function ManaBubble({ isPlayer1 }: { isPlayer1: boolean; }) {
    const rotateStyle = isPlayer1 ? cellStyle.rotate180deg : undefined;
    const description = "Gain an extra mana point when moving to this cell or spawning on it";

    return (
        <div className="mana-bubble">
            <div className="mana-bubble-description">
                <div style={{ transform: rotateStyle }}>{description}</div>
            </div>
        </div>
    );
}

interface LandMineProps {
    isPlayer1: boolean;
    isBlinking: boolean;
}

export function LandMine(props: LandMineProps) {
    const { isPlayer1, isBlinking } = props;

    const blinkStyle: React.CSSProperties = {
        ["--color1" as string]: "black",
        ["--color2" as string]: "red",
        ["--frequency" as string]: "0.2s",
    };

    return (
        <div className="land-mine absolute-positioning-centered">
            <LandMineIcon
                style={{
                    fill: "black",
                    transform: isPlayer1 ? cellStyle.rotate180deg : undefined,
                    animation: isBlinking ? "fill-blink 0.2s infinite" : EMPTY_STRING,
                    ...blinkStyle,
                }}
            />
        </div>
    );
}