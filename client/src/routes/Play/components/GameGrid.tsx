import { useEffect, useState } from "react";
import OpponentTurnImage from "../../../assets/images/Your Opponent Turn.png";
import YourTurnImage from "../../../assets/images/Your Turn.png";
import { ContainerProps } from "../../../components/containers";
import { useMatchInfo } from "../../../contexts/MatchContext";
import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { useTurnInfo } from "../../../contexts/TurnContext";
import { CellInfoDto } from "../../../dto/CellInfoDto";
import { PossibleActionsDto } from "../../../dto/PossibleActionsDto";
import { ProcessedActionsDto } from "../../../dto/ProcessedActionsDto";
import { undefinedTurnInfo } from "../../../dto/TurnInfoDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { colorBoard, colorBoardFromPossibleActions, getCellId } from "../../../utils/boardUtils";
import { developmentLog } from "../../../utils/loggingUtils";
import GameCell from "./GameCell";
import TurnSwapImage from "./TurnSwapImage";

export default function GameGrid() {
    const { matchInfo } = useMatchInfo();
    const { playerId, isPlayer1 } = usePlayerInfo();
    const { turnInfo, canInteract, setCanInteract } = useTurnInfo();

    const boardArray = matchInfo.boardArray;
    const gridStyle: React.CSSProperties = {
        transform: `${isPlayer1 ? "rotate(180deg)" : undefined}`,
        gridTemplateColumns: `repeat(${boardArray.length}, 1fr)`,
    };

    const [turnSwapImagePath, setTurnSwapImagePath] = useState(YourTurnImage);
    const [showTurnSwapImage, setShowTurnSwapImage] = useState(false);
    const [isMyTurn, setIsMyTurn] = useState(false);

    useEffect(() => {
        if (turnInfo === undefinedTurnInfo) return;

        setIsMyTurn(turnInfo.currentPlayerId === playerId);
    }, [playerId, turnInfo]);

    useEffect(() => {
        controlInteractionEnabling();

        // Allows/disallows the player to interact with elements such as the game cells
        // or the end turn button according to whether it is their turn or not and if the
        // turn swap animation is done running.
        function controlInteractionEnabling() {
            setCanInteract(false);

            // If not a turn change, the user may interact immediately
            // if it's theiur turn (typically after a page refresh)
            if (!turnInfo.notifyTurnChange) {
                setCanInteract(isMyTurn);
                return;
            }

            // Trigger the turn swap image animation
            setTurnSwapImagePath(isMyTurn ? YourTurnImage : OpponentTurnImage);
            setShowTurnSwapImage(true);

            // The user must wait for the turn image animation to end before they can interact
            const timeout = setTimeout(() => {
                setShowTurnSwapImage(false);
                setCanInteract(isMyTurn);
            }, 2000);

            return () => clearTimeout(timeout);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isMyTurn]);

    useEffect(() => {
        colorBoard(boardArray, isPlayer1);
    });

    useEffect(() => {
        // To let the player know that the opponent has their cursor
        // over a specific cell (by coloring the cell's border in red)
        function onServerCellHover(cell: CellInfoDto) {
            if (isMyTurn) return;

            const htmlCell = document.getElementById(
                getCellId(cell.rowIndex, cell.columnIndex)
            );
            if (!htmlCell) return;

            const currentClassName = htmlCell.className;
            htmlCell.className = `${currentClassName} selected`;
        }

        // End the red border coloring once the opponent is no longer hovering it
        function onServerCellHoverEnd(cell: CellInfoDto) {
            if (isMyTurn) return;

            const htmlCell = document.getElementById(
                getCellId(cell.rowIndex, cell.columnIndex)
            );
            if (!htmlCell) return;

            const currentClassName = htmlCell.className;
            htmlCell.className = currentClassName.replace(" selected", "");
        }

        function onServerPossibleActions(actionsDto: PossibleActionsDto) {
            developmentLog("Received the possible actions", actionsDto);

            colorBoardFromPossibleActions(actionsDto);
        }

        function onServerProcessedActions(actions: ProcessedActionsDto) {
            developmentLog("Received the processed actions", actions);
        }

        socket.on(Events.SERVER_CELL_HOVER, onServerCellHover);
        socket.on(Events.SERVER_CELL_HOVER_END, onServerCellHoverEnd);
        socket.on(Events.SERVER_POSSIBLE_ACTIONS, onServerPossibleActions);
        socket.on(Events.SERVER_PROCESSED_ACTIONS, onServerProcessedActions);

        return () => {
            socket.off(Events.SERVER_CELL_HOVER, onServerCellHover);
            socket.off(Events.SERVER_CELL_HOVER_END, onServerCellHoverEnd);
            socket.off(Events.SERVER_POSSIBLE_ACTIONS, onServerPossibleActions);
            socket.off(Events.SERVER_PROCESSED_ACTIONS, onServerProcessedActions);
        };
    });

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
                                canInteractWith={canInteract && _cell.owner !== 0}
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
    return <div className="grid-outer">{props.children}</div>;
}

function GridInner(props: ContainerProps) {
    return (
        <div className="grid-inner" style={props.style}>
            {props.children}
        </div>
    );
}

function GridRow(props: ContainerProps) {
    return <div className="row">{props.children}</div>;
}
