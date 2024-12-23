import { useEffect, useState } from "react";
import OpponentTurnImage from "../../../assets/images/Your Opponent Turn.png";
import YourTurnImage from "../../../assets/images/Your Turn.png";
import { ContainerProps } from "../../../components/containers";
import { useMatchInfo } from "../../../contexts/MatchContext";
import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { useTurnInfo } from "../../../contexts/TurnContext";
import { CoordinatesDto } from "../../../dto/CoordinatesDto";
import { PartialCellInfoDto } from "../../../dto/PartialCellInfoDto";
import { PossibleActionsDto } from "../../../dto/PossibleActionsDto";
import { ProcessedActionsDto } from "../../../dto/ProcessedActionsDto";
import { undefinedTurnInfo } from "../../../dto/TurnInfoDto";
import { Events } from "../../../enums/events";
import { socket } from "../../../env";
import { applyPossibleActionsToBoard, clearBoardColoring, getDefaultSelectableCells } from "../../../utils/boardUtils";
import { colorHoveredCell, decolorHoveredCell, getCellId, isOwned } from "../../../utils/cellUtils";
import { developmentLog } from "../../../utils/loggingUtils";
import GameCell from "./GameCell";
import TurnSwapImage from "./TurnSwapImage";

export default function GameGrid() {
    const { matchInfo } = useMatchInfo();
    const { playerId, isPlayer1 } = usePlayerInfo();
    const { turnInfo, canInteract, setCanInteract } = useTurnInfo();

    const [turnSwapImagePath, setTurnSwapImagePath] = useState(YourTurnImage);
    const [showTurnSwapImage, setShowTurnSwapImage] = useState(false);
    const [isMyTurn, setIsMyTurn] = useState(false);

    const [boardArray, setBoardArray] = useState(matchInfo.boardArray);
    const [selectableCells, setSelectableCells] = useState(
        // Initialize cells with an owner as selectable
        getDefaultSelectableCells(boardArray)
    );

    function setCellsSelectable(coordinates: CoordinatesDto[], isSelectable: boolean) {
        setSelectableCells(prevState => {
            const newState = prevState.map(row => [...row]); // Clone state
            coordinates.forEach((coord) => { // Update
                newState[coord.rowIndex][coord.columnIndex] = isSelectable;
            });
            return newState;
        });
    }

    // Reset the board colors and selectable cells when it changes
    useEffect(() => {
        handleBoardArrayChange();

        function handleBoardArrayChange() {
            clearBoardColoring(boardArray, cell => isOwned(cell));
            setSelectableCells(getDefaultSelectableCells(boardArray));
        }
    }, [boardArray])

    // Set the isMyTurn variable on turn change
    // Reset the colors on the boardArray variable change
    useEffect(() => {
        handleTurnChange();

        function handleTurnChange() {
            clearBoardColoring(boardArray, cell => isOwned(cell));

            if (turnInfo === undefinedTurnInfo) return;
            setIsMyTurn(turnInfo.currentPlayerId === playerId);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [turnInfo]);

    // React to the isMyTurn change
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

    // Register socket events
    useEffect(() => {
        // To let the player know that the opponent has their cursor
        // over a specific cell (by coloring the cell's border in red)
        function onServerCellHover(cell: PartialCellInfoDto) {
            if (isMyTurn) return;

            colorHoveredCell(cell);
        }

        // End the red border coloring once the opponent is no longer hovering it
        function onServerCellHoverEnd(cell: PartialCellInfoDto) {
            if (isMyTurn) return;

            decolorHoveredCell(cell);
        }

        function onServerPossibleActions(actionsDto: PossibleActionsDto) {
            developmentLog("Received the possible actions", actionsDto);

            clearBoardColoring(boardArray, (cell) => isOwned(cell));
            setSelectableCells(getDefaultSelectableCells(boardArray));
            applyPossibleActionsToBoard(actionsDto, setCellsSelectable);
        }

        function onServerProcessedActions(actions: ProcessedActionsDto) {
            developmentLog("Received the processed actions", actions);

            // Remove the animations on non owned cells before they eventually get
            // captured and escape animation clearing.
            clearBoardColoring(boardArray, (cell) => isOwned(cell));
            setBoardArray(actions.updatedBoardArray);
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

    const gridStyle: React.CSSProperties = {
        transform: `${isPlayer1 ? "rotate(180deg)" : undefined}`,
        gridTemplateColumns: `repeat(${boardArray.length}, 1fr)`,
    };

    return (
        <GridOuter>
            <GridInner style={gridStyle}>
                {boardArray.map((row, rowIndex) => (
                    <GridRow className="row" id={`r-${rowIndex}`} key={rowIndex}>
                        {row.map((cellInfo, colIndex) => (
                            <GameCell
                                key={colIndex}
                                id={getCellId(rowIndex, colIndex)}
                                isPlayer1={isPlayer1}
                                cellInfo={cellInfo}
                                selectable={canInteract && selectableCells[rowIndex][colIndex]}
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
