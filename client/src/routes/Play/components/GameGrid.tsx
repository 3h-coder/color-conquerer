import { useEffect, useState } from "react";
import OpponentTurnImage from "../../../assets/images/Your Opponent Turn.png";
import YourTurnImage from "../../../assets/images/Your Turn.png";
import { useMatchInfo } from "../../../contexts/MatchContext";
import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { undefinedTurnInfo, useTurnInfo } from "../../../contexts/TurnContext";
import { CellInfoDto } from "../../../dto/CellInfoDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { animations, colors } from "../../../style/constants";
import GameCell from "./GameCell";
import TurnSwapImage from "./TurnSwapImage";

export default function GameGrid() {
    const { matchInfo } = useMatchInfo();
    const { playerInfo } = usePlayerInfo();
    const { turnInfo } = useTurnInfo();
    const boardArray = matchInfo.boardArray;
    const gridStyle: React.CSSProperties = {
        transform: `${playerInfo.isPlayer1 ? "rotate(180deg)" : undefined}`,
        gridTemplateColumns: `repeat(${boardArray.length}, 1fr)`,
    };
    const [canSelect, setCanSelect] = useState(false);
    const [turnSwapImagePath, setTurnSwapImagePath] = useState(YourTurnImage);
    const [showTurnSwapImage, setShowTurnSwapImage] = useState(false);
    const [isMyTurn, setIsMyTurn] = useState(false);
    //const shouldAnimate = Boolean(extractKey(constants.localStorageKeys.animateGrid));
    const shouldAnimate = false;

    useEffect(() => {
        if (turnInfo === undefinedTurnInfo) return;

        setIsMyTurn(turnInfo.currentPlayerId === playerInfo.playerId);
    }, [playerInfo.playerId, turnInfo]);

    useEffect(() => {
        setTurnSwapImagePath(isMyTurn ? YourTurnImage : OpponentTurnImage);
        setShowTurnSwapImage(true);

        const timeOut = setTimeout(() => {
            setShowTurnSwapImage(false);
            setCanSelect(isMyTurn);
        }, 2200);

        return () => clearTimeout(timeOut);
    }, [isMyTurn]);

    useEffect(() => {
        if (!shouldAnimate) {
            colorBoard();
        } else {
            const arrayRowLength = boardArray[0].length;
            const longestAnimationDelayInMs = (arrayRowLength - 1) * arrayRowLength * animations.grid.cellAnimationDelayFactor;
            const totalAnimationCompletionTimeInMs = longestAnimationDelayInMs + animations.grid.cellAnimationTimeInMs;

            const timeout = setTimeout(() => {
                colorBoard();
            }, totalAnimationCompletionTimeInMs);

            return () => clearTimeout(timeout);
        }


        function colorBoard() {
            boardArray.forEach((row) => {
                row.forEach((cell) => {
                    if (cell.owner === 0) return;

                    const htmlCell = document.getElementById(
                        getCellId(cell.rowIndex, cell.columnIndex)
                    );
                    if (playerInfo.isPlayer1) {
                        htmlCell!.style.backgroundColor =
                            cell.owner === 1 ? colors.ownCell : colors.opponentCell;
                    } else {
                        htmlCell!.style.backgroundColor =
                            cell.owner === 2 ? colors.ownCell : colors.opponentCell;
                    }
                });
            });
        }
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

    function getCellId(rowIndex: number, colIndex: number) {
        return `c-${rowIndex}-${colIndex}`;
    }

    return (
        <div className="grid" style={gridStyle}>
            {boardArray.map((row, rowIndex) => (
                <div className="row" id={`r-${rowIndex}`} key={rowIndex}>
                    {row.map((_cell, colIndex) => (
                        <GameCell
                            key={colIndex}
                            id={getCellId(rowIndex, colIndex)}
                            rowIndex={rowIndex}
                            columnIndex={colIndex}
                            canBeSelected={canSelect}
                            arrayRowLength={boardArray[0].length}
                            animate={shouldAnimate}
                        />
                    ))}
                </div>
            ))}
            {showTurnSwapImage && <TurnSwapImage imagePath={turnSwapImagePath} />}
        </div>
    );
}
