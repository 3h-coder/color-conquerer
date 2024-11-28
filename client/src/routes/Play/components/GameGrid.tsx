import { useEffect, useState } from "react";
import OpponentTurnImage from "../../../assets/images/Your Opponent Turn.png";
import YourTurnImage from "../../../assets/images/Your Turn.png";
import { ContainerProps } from "../../../components/containers";
import { useMatchInfo } from "../../../contexts/MatchContext";
import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { useTurnInfo } from "../../../contexts/TurnContext";
import { CellInfoDto } from "../../../dto/CellInfoDto";
import { undefinedTurnInfo } from "../../../dto/TurnInfoDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { colors } from "../../../style/constants";
import GameCell from "./GameCell";
import TurnSwapImage from "./TurnSwapImage";

export default function GameGrid() {
    const { matchInfo } = useMatchInfo();
    const { playerId, isPlayer1 } = usePlayerInfo();
    const { turnInfo } = useTurnInfo();

    const boardArray = matchInfo.boardArray;
    const rotate = isPlayer1;
    const gridStyle: React.CSSProperties = {
        transform: `${rotate ? "rotate(180deg)" : undefined}`,
        gridTemplateColumns: `repeat(${boardArray.length}, 1fr)`,
    };

    const [canSelect, setCanSelect] = useState(false);
    const [turnSwapImagePath, setTurnSwapImagePath] = useState(YourTurnImage);
    const [showTurnSwapImage, setShowTurnSwapImage] = useState(false);
    const [isMyTurn, setIsMyTurn] = useState(false);

    useEffect(() => {
        if (turnInfo === undefinedTurnInfo) return;

        setIsMyTurn(turnInfo.currentPlayerId === playerId);
    }, [playerId, turnInfo]);

    useEffect(() => {
        if (!turnInfo.notifyTurnChange) {
            setCanSelect(isMyTurn);
            return;
        }

        setTurnSwapImagePath(isMyTurn ? YourTurnImage : OpponentTurnImage);
        setShowTurnSwapImage(true);

        const timeout = setTimeout(() => {
            setShowTurnSwapImage(false);
            setCanSelect(isMyTurn);
        }, 2000);

        return () => clearTimeout(timeout);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isMyTurn]);

    useEffect(() => {
        colorBoard();
    });

    useEffect(() => {
        // To let the player know that the opponent has their cursor 
        // over a specific cell (by coloring the cell's border in red)
        function onServerCellHover(cell: CellInfoDto) {
            if (isMyTurn)
                return;

            const htmlCell = document.getElementById(getCellId(cell.rowIndex, cell.columnIndex));
            if (!htmlCell)
                return;

            const currentClassName = htmlCell.className;
            htmlCell.className = `${currentClassName} selected`;
        }

        // End the red border coloring once the opponent is no longer hovering it
        function onServerCellHoverEnd(cell: CellInfoDto) {
            if (isMyTurn)
                return;

            const htmlCell = document.getElementById(getCellId(cell.rowIndex, cell.columnIndex))
            if (!htmlCell)
                return;

            const currentClassName = htmlCell.className;
            htmlCell.className = currentClassName.replace(" selected", "");
        }

        socket.on(Events.SERVER_CELL_HOVER, onServerCellHover);
        socket.on(Events.SERVER_CELL_HOVER_END, onServerCellHoverEnd);

        return () => {
            socket.off(Events.SERVER_CELL_HOVER, onServerCellHover);
            socket.off(Events.SERVER_CELL_HOVER_END, onServerCellHoverEnd);
        }
    });

    function colorBoard() {
        boardArray.forEach((row) => {
            row.forEach((cell) => {
                if (cell.owner === 0) return;

                const htmlCell = document.getElementById(
                    getCellId(cell.rowIndex, cell.columnIndex)
                );
                if (isPlayer1) {
                    htmlCell!.style.backgroundColor =
                        cell.owner === 1 ? colors.ownCell : colors.opponentCell;
                } else {
                    htmlCell!.style.backgroundColor =
                        cell.owner === 2 ? colors.ownCell : colors.opponentCell;
                }
            });
        });
    }

    function getCellId(rowIndex: number, colIndex: number) {
        return `c-${rowIndex}-${colIndex}`;
    }

    return (
        <GridOuter>
            <GridInner style={gridStyle}>
                {boardArray.map((row, rowIndex) => (
                    <GridRow className="row" id={`r-${rowIndex}`} key={rowIndex}>
                        {row.map((_cell, colIndex) => (
                            <GameCell
                                key={colIndex}
                                id={getCellId(rowIndex, colIndex)}
                                rowIndex={rowIndex}
                                columnIndex={colIndex}
                                canBeSelected={canSelect}
                            />
                        ))}
                    </GridRow>
                ))}
            </GridInner>
            {showTurnSwapImage && <TurnSwapImage imagePath={turnSwapImagePath} />}
        </GridOuter>

    );
}

function GridOuter(props: ContainerProps) {
    return (
        <div className="grid-outer">
            {props.children}
        </div>
    );
}

function GridInner(props: ContainerProps) {
    return (
        <div className="grid-inner" style={props.style}>
            {props.children}
        </div>
    );
}

function GridRow(props: ContainerProps) {
    return (
        <div className="row">
            {props.children}
        </div>
    );
}
