import React from "react";
import { LandMineIcon, SwordIcon } from "../../../../assets/svg";
import { CellDto } from "../../../../dto/CellDto";
import { CellHiddenState } from "../../../../enums/cellHiddenState";
import {
    CellState,
    CellStateUtils,
} from "../../../../enums/cellState";
import { CellTransientState } from "../../../../enums/cellTransientState";
import { Events } from "../../../../enums/events";
import { EMPTY_STRING, socket, WHITE_SPACE } from "../../../../env";
import { cellStyle } from "../../../../style/constants";
import {
    canBeSpawnedOrMovedInto,
    getCellBackgroundColor,
    isOwnedAndCanBeSpellTargetted,
    isSelectable
} from "../../../../utils/cellUtils";
import "./styles/GameCell.css";

interface GameCellProps {
    id: string;
    isPlayer1: boolean;
    cellInfo: CellDto;
    canInteract: boolean;
    canDisplayPossibleActions: boolean;
}

export default function GameCell(props: GameCellProps) {
    const { id, isPlayer1, cellInfo, canInteract, canDisplayPossibleActions } =
        props;
    const selectable = canInteract && isSelectable(cellInfo);

    const selected = cellInfo.transientState === CellTransientState.SELECTED;
    const attackable = cellInfo.transientState === CellTransientState.CAN_BE_ATTACKED;
    const canBeSpellTargetted = cellInfo.transientState === CellTransientState.CAN_BE_SPELL_TARGETTED;
    const isManaBubble = CellStateUtils.contains(cellInfo.state, CellState.MANA_BUBBLE);
    const isMineTrap = cellInfo.hiddenState == CellHiddenState.MINE_TRAP;

    function onCellClick() {
        if (!selectable) return;

        socket.emit(Events.CLIENT_CELL_CLICK, cellInfo);
    }

    const allClassNames = [
        selectable ? cellStyle.classNames.selectable : EMPTY_STRING,
        canDisplayPossibleActions && canBeSpawnedOrMovedInto(cellInfo)
            ? cellStyle.classNames.spawnOrMovePossible
            : EMPTY_STRING,
        canDisplayPossibleActions && canBeSpellTargetted
            ? cellStyle.classNames.possibleSpellTarget
            : EMPTY_STRING
    ];
    const classes = `${cellStyle.className} ${allClassNames.join(WHITE_SPACE)}`.trim();

    const computedBackgroundColor = getCellBackgroundColor(cellInfo, isPlayer1);

    return (
        <div
            className={classes}
            id={id}
            onClick={onCellClick}
            style={computedBackgroundColor}
        >
            {/* Uncomment the line below to see each cell's row and column index */}
            {/* <span style={{ position: "absolute", fontSize: "px", color: "black" }}>{`[${rowIndex}, ${columnIndex}]`}</span> */}
            {selected && <SelectedIndicator />}
            {attackable && <AttackableIndicator isPlayer1={isPlayer1} />}
            {isManaBubble && <ManaBubble isPlayer1={isPlayer1} />}
            {isMineTrap && <LandMine isPlayer1={isPlayer1} isBlinking={false} />}
            {isOwnedAndCanBeSpellTargetted(cellInfo) && <SpellTargetIndicator />}
        </div>
    );
}

function SelectedIndicator() {
    return (
        <div className={`selected-indicator ${cellStyle.classNames.absPosition}`} />
    );
}

function AttackableIndicator({ isPlayer1 }: { isPlayer1: boolean; }) {
    const rotateStyle = isPlayer1 ? "rotate(180deg)" : undefined;

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
    const rotateStyle = isPlayer1 ? "rotate(180deg)" : undefined;
    const description =
        "Gain an extra mana point when moving to this cell or spawning on it";
    return (
        <div className={`mana-bubble`}>
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
                    transform: isPlayer1 ? "rotate(180deg)" : undefined,
                    animation: isBlinking ? "fill-blink 0.2s infinite" : EMPTY_STRING,
                    ...blinkStyle,
                }}
            />
        </div>
    );
}
