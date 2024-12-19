import { CellInfoDto } from "../../../dto/CellInfoDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { cellStyle } from "../../../style/constants";

interface GameCellProps {
    id: string;
    rowIndex: number;
    columnIndex: number;
    selectable: boolean;
}

export default function GameCell(props: GameCellProps) {
    const { id, rowIndex, columnIndex, selectable } = props;

    function onCellMouseEnter() {
        if (!selectable) return;

        socket.emit(Events.CLIENT_CELL_HOVER, getCellInfoDto());
    }

    function onCellMouseLeave() {
        if (!selectable) return;

        socket.emit(Events.CLIENT_CELL_HOVER_END, getCellInfoDto());
    }

    function onCellClick() {
        if (!selectable) return;

        socket.emit(Events.CLIENT_CELL_CLICK, getCellInfoDto());
    }

    function getCellInfoDto() {
        // Note that only the row and column indexes matter, as the server
        // always has the up-to-date board information.
        return {
            owner: -1,
            isMaster: false,
            rowIndex: rowIndex,
            columnIndex: columnIndex,
            state: -1,
        } as unknown as CellInfoDto;
    }

    return (
        <div
            className={`${cellStyle.className} ${selectable ? cellStyle.selectableClassName : ""}`}
            id={id}
            onMouseEnter={onCellMouseEnter}
            onMouseLeave={onCellMouseLeave}
            onClick={onCellClick}
            style={{ position: "relative" }}
        >
            {/* Uncomment the line below to see each cell's row and column index */}
            {/* <span style={{ position: "absolute", fontSize: "px", color: "black" }}>{`[${rowIndex}, ${columnIndex}]`}</span> */}
        </div>
    );
}
