import { useEffect } from "react";
import { PartialCellInfoDto } from "../../../dto/PartialCellInfoDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { cellStyle } from "../../../style/constants";
import { getCellStyle as getCellStyle, isSelectable } from "../../../utils/cellUtils";
import { CellTransientState } from "../../../enums/cellStates";
import { SwordIcon } from "../../../assets/svg";

interface GameCellProps {
    id: string;
    isPlayer1: boolean;
    cellInfo: PartialCellInfoDto;
    canInteract: boolean;
}

export default function GameCell(props: GameCellProps) {
    const { id, isPlayer1, cellInfo, canInteract } = props;
    const selectable = canInteract && isSelectable(cellInfo);

    const selected = cellInfo.transientState === CellTransientState.SELECTED;
    const attackable = cellInfo.transientState === CellTransientState.CAN_BE_ATTACKED;

    // If the cell was previously hovered and is being re-rendered
    // send a HOVER_END event to the server to clear the hover effect 
    // for the opponent client
    useEffect(() => {
        if (!selectable)
            socket.emit(Events.CLIENT_CELL_HOVER_END, cellInfo);
    });

    function onCellMouseEnter() {
        if (!selectable) return;

        socket.emit(Events.CLIENT_CELL_HOVER, cellInfo);
    }

    function onCellMouseLeave() {
        if (!selectable) return;

        socket.emit(Events.CLIENT_CELL_HOVER_END, cellInfo);
    }

    function onCellClick() {
        if (!selectable) return;

        socket.emit(Events.CLIENT_CELL_CLICK, cellInfo);
    }

    const computedStyle = getCellStyle(cellInfo, isPlayer1);
    const className = `${cellStyle.className} ${selectable ? cellStyle.selectableClassName : ""}`.trim();

    return (
        <div
            className={className}
            id={id}
            onMouseEnter={onCellMouseEnter}
            onMouseLeave={onCellMouseLeave}
            onClick={onCellClick}
            style={computedStyle}
        >
            {/* Uncomment the line below to see each cell's row and column index */}
            {/* <span style={{ position: "absolute", fontSize: "px", color: "black" }}>{`[${rowIndex}, ${columnIndex}]`}</span> */}
            {selected && <SelectedIndicator />}
            {attackable && <AttackableIndicator isPlayer1={isPlayer1} />}
        </div>
    );
}

function SelectedIndicator() {
    return <div className={`selected-indicator ${cellStyle.absPositionClassName}`} />;
}


function AttackableIndicator({ isPlayer1 }: { isPlayer1: boolean }) {
    const rotateStyle = isPlayer1 ? "rotate(180deg)" : undefined;

    return (
        <div className={`attackable-indicator ${cellStyle.absPositionClassName}`}>
            <SwordIcon style={{ transform: rotateStyle }} />
        </div>
    );
}
