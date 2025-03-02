import React from "react";
import { LandMineIcon, SwordIcon } from "../../../../assets/svg";
import { CellDto } from "../../../../dto/CellDto";
import {
    CellHiddenState,
    CellState,
    CellTransientState,
} from "../../../../enums/cellState";
import { Events } from "../../../../enums/events";
import { EMPTY_STRING, socket } from "../../../../env";
import { cellStyle } from "../../../../style/constants";
import {
    canBeTargetted,
    getCellStyle,
    isSelectable,
} from "../../../../utils/cellUtils";

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
    const attackable =
        cellInfo.transientState === CellTransientState.CAN_BE_ATTACKED;
    const isManaBubble = cellInfo.state == CellState.MANA_BUBBLE;
    const isMineTrap = cellInfo.hiddenState == CellHiddenState.MINE_TRAP;

    function onCellClick() {
        if (!selectable) return;

        socket.emit(Events.CLIENT_CELL_CLICK, cellInfo);
    }

    const allClassNames = [
        selectable ? cellStyle.selectableClassName : EMPTY_STRING,
        canDisplayPossibleActions && canBeTargetted(cellInfo)
            ? cellStyle.possibleActionClassName
            : EMPTY_STRING,
    ];
    const classes = `${cellStyle.className} ${allClassNames.join(" ")}`.trim();

    const computedStyle = getCellStyle(cellInfo, isPlayer1);

    return (
        <div
            className={classes}
            id={id}
            onClick={onCellClick}
            style={computedStyle}
        >
            {/* Uncomment the line below to see each cell's row and column index */}
            {/* <span style={{ position: "absolute", fontSize: "px", color: "black" }}>{`[${rowIndex}, ${columnIndex}]`}</span> */}
            {selected && <SelectedIndicator />}
            {attackable && <AttackableIndicator isPlayer1={isPlayer1} />}
            {isManaBubble && <ManaBubble />}
            {isMineTrap && <LandMine isPlayer1={isPlayer1} isBlinking={false} />}
        </div>
    );
}

function SelectedIndicator() {
    return (
        <div className={`selected-indicator ${cellStyle.absPositionClassName}`} />
    );
}

function AttackableIndicator({ isPlayer1 }: { isPlayer1: boolean; }) {
    const rotateStyle = isPlayer1 ? "rotate(180deg)" : undefined;

    return (
        <div className={`attackable-indicator ${cellStyle.absPositionClassName}`}>
            <SwordIcon style={{ transform: rotateStyle }} />
        </div>
    );
}

function ManaBubble() {
    return <div className="mana-bubble absolute-positioning-centered" />;
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
        <div
            className="land-mine absolute-positioning-centered"
        >
            <LandMineIcon
                style={{
                    fill: "black",
                    transform: isPlayer1 ? "rotate(180deg)" : undefined,
                    animation: isBlinking ? "fill-blink 0.2s infinite" : EMPTY_STRING,
                    ...blinkStyle
                }}
            />
        </div>
    );
}
