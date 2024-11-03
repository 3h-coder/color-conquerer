import { useEffect, useState } from "react";
import { CellInfoDto } from "../../../dto/CellInfoDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { animations } from "../../../style/constants";

interface GameCellProps {
    id: string;
    rowIndex: number;
    columnIndex: number;
    canBeSelected: boolean;
    arrayRowLength: number;
    animate: boolean;
}

export default function GameCell(props: GameCellProps) {
    const { id, rowIndex, columnIndex, canBeSelected, arrayRowLength, animate } = props;
    const [opacity, setOpacity] = useState(animate ? "0" : "1");
    const animationDelayInMs = (rowIndex * arrayRowLength) * animations.grid.cellAnimationDelayFactor;
    const animationStyle = `appear-growing ${animations.grid.cellAnimationTimeInMs}ms ${animationDelayInMs}ms ease-in-out`;

    useEffect(() => {
        if (!animate)
            return;

        const timeout = setTimeout(() => {
            setOpacity("1");
        }, animationDelayInMs);

        return () => clearTimeout(timeout);
    })

    function onCellMouseEnter() {
        if (canBeSelected)
            socket.emit(Events.CLIENT_CELL_HOVER, {
                owner: -1,
                rowIndex: rowIndex,
                columnIndex: columnIndex,
                state: -1,
            } as unknown as CellInfoDto);
    }

    function onCellMouseLeave() {
        if (canBeSelected)
            socket.emit(Events.CLIENT_CELL_HOVER_END, {
                owner: -1,
                rowIndex: rowIndex,
                columnIndex: columnIndex,
                state: -1,
            } as unknown as CellInfoDto);
    }

    return (
        <div
            className={`cell ${canBeSelected ? "selectable" : ""}`}
            id={id}
            onMouseEnter={onCellMouseEnter}
            onMouseLeave={onCellMouseLeave}
            style={{ position: "relative", opacity: opacity, animation: animate ? animationStyle : undefined }}
        >
            {/* Uncomment the line below to see each cell's row and column index */}
            {/* <span style={{ position: "absolute", fontSize: "px", color: "black" }}>{`[${rowIndex}, ${columnIndex}]`}</span> */}
        </div>
    );
}
