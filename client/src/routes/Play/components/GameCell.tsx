import { CellInfoDto } from "../../../dto/CellInfoDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { cellStyle } from "../../../style/constants";
import { getDefaultStyle } from "../../../utils/cellUtils";

interface GameCellProps {
    id: string;
    isPlayer1: boolean;
    cellInfo: CellInfoDto;
    selectable: boolean;
}

export default function GameCell(props: GameCellProps) {
    const { id, isPlayer1, cellInfo, selectable } = props;

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

    const computedStyle = getDefaultStyle(cellInfo, isPlayer1);

    return (
        <div
            className={`${cellStyle.className} ${selectable ? cellStyle.selectableClassName : ""}`}
            id={id}
            onMouseEnter={onCellMouseEnter}
            onMouseLeave={onCellMouseLeave}
            onClick={onCellClick}
            style={computedStyle}
        >
            {/* Uncomment the line below to see each cell's row and column index */}
            {/* <span style={{ position: "absolute", fontSize: "px", color: "black" }}>{`[${rowIndex}, ${columnIndex}]`}</span> */}
        </div>
    );
}
