import { CellInfoDto } from "../../../dto/CellInfoDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";

interface GameCellProps {
    id: string;
    rowIndex: number;
    colIndex: number;
    canBeSelected: boolean;
}

export default function GameCell(props: GameCellProps) {
    const { id, rowIndex, colIndex, canBeSelected } = props;

    function onCellMouseEnter() {
        if (canBeSelected)
            socket.emit(Events.CLIENT_CELL_HOVER, {
                owner: -1,
                rowIndex: rowIndex,
                columnIndex: colIndex,
                state: -1,
            } as unknown as CellInfoDto);
    }

    function onCellMouseLeave() {
        if (canBeSelected)
            socket.emit(Events.CLIENT_CELL_HOVER_END, {
                owner: -1,
                rowIndex: rowIndex,
                columnIndex: colIndex,
                state: -1,
            } as unknown as CellInfoDto);
    }

    return (
        <div
            className={`cell ${canBeSelected ? "selectable" : ""}`}
            id={id}
            onMouseEnter={onCellMouseEnter}
            onMouseLeave={onCellMouseLeave}
        />
    );
}
