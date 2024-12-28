import { useEffect, useState } from "react";
import OpponentTurnImage from "../../../assets/images/Your Opponent Turn.png";
import YourTurnImage from "../../../assets/images/Your Turn.png";
import { ContainerProps } from "../../../components/containers";
import { useMatchInfo } from "../../../contexts/MatchContext";
import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { useTurnInfo } from "../../../contexts/TurnContext";
import { PartialCellInfoDto } from "../../../dto/PartialCellInfoDto";
import { PossibleActionsDto } from "../../../dto/PossibleActionsDto";
import { ProcessedActionDto } from "../../../dto/ProcessedActionDto";
import { undefinedTurnInfo } from "../../../dto/TurnInfoDto";
import { Events } from "../../../enums/events";
import { EMPTY_STRING, socket } from "../../../env";
import {
    colorHoveredCell,
    decolorHoveredCell,
    getCellId,
} from "../../../utils/cellUtils";
import { developmentLog } from "../../../utils/loggingUtils";
import GameCell from "./GameCell";
import TurnSwapImage from "./TurnSwapImage";
import GameError from "./GameError";
import { MessageDto } from "../../../dto/MessageDto";
import { usePlayerMode } from "../../../contexts/PlayerModeContext";
import { usePlayersGameInfo } from "../../../contexts/PlayersGameInfoContext";

export default function GameGrid() {
    const { matchInfo } = useMatchInfo();
    const { playerId, isPlayer1 } = usePlayerInfo();
    const { turnInfo, canInteract, setCanInteract } = useTurnInfo();
    const { setPlayerGameInfoBundle } = usePlayersGameInfo();
    const { setPlayerMode } = usePlayerMode();

    const [turnSwapImagePath, setTurnSwapImagePath] = useState(YourTurnImage);
    const [showTurnSwapImage, setShowTurnSwapImage] = useState(false);
    const [isMyTurn, setIsMyTurn] = useState(false);
    const [actionErrorMessage, setActionErrorMessage] = useState(EMPTY_STRING);

    const [boardArray, setBoardArray] = useState(matchInfo.boardArray);

    // Set the isMyTurn variable on turn change
    // Reset the colors on the boardArray variable change
    useEffect(() => {
        handleTurnChange();

        function handleTurnChange() {
            setBoardArray(turnInfo.updatedBoardArray);
            setPlayerGameInfoBundle(turnInfo.playerGameInfoBundle);
            setActionErrorMessage(EMPTY_STRING);

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

    // Clear the error message ~1 second after it has been set
    useEffect(() => {
        delayedErrorMessageClearance();

        function delayedErrorMessageClearance() {
            if (!actionErrorMessage)
                return;

            const timeout = setTimeout(() => {
                setActionErrorMessage(EMPTY_STRING);
            }, 1400);

            return () => clearTimeout(timeout);
        }
    }, [actionErrorMessage])

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

        function onServerPossibleActions(possibleActions: PossibleActionsDto) {
            developmentLog("Received the possible actions", possibleActions);

            // Update the player mode for the dependent components to react to
            setPlayerMode(possibleActions.playerMode);

            // Apply the new coloring and selectable cells
            setBoardArray(possibleActions.transientBoardArray);
        }

        function onServerProcessedActions(processedActions: ProcessedActionDto) {
            developmentLog("Received the processed actions", processedActions);

            // Update the player mode for the dependent components to react to
            setPlayerMode(processedActions.playerMode);

            // Update the player info bundle to display the proper HP/MP values
            setPlayerGameInfoBundle(processedActions.updatedMatchInfo.playerInfoBundle);

            // Update the board array with the new cell info
            setBoardArray(processedActions.updatedMatchInfo.boardArray);
        }

        function onServerActionError(errorMessageDto: MessageDto) {
            const gameErrorMessage = errorMessageDto.message;
            developmentLog("Received the game error", gameErrorMessage);

            setActionErrorMessage(gameErrorMessage);
        }

        socket.on(Events.SERVER_CELL_HOVER, onServerCellHover);
        socket.on(Events.SERVER_CELL_HOVER_END, onServerCellHoverEnd);
        socket.on(Events.SERVER_POSSIBLE_ACTIONS, onServerPossibleActions);
        socket.on(Events.SERVER_PROCESSED_ACTIONS, onServerProcessedActions);
        socket.on(Events.SERVER_ACTION_ERROR, onServerActionError);

        return () => {
            socket.off(Events.SERVER_CELL_HOVER, onServerCellHover);
            socket.off(Events.SERVER_CELL_HOVER_END, onServerCellHoverEnd);
            socket.off(Events.SERVER_POSSIBLE_ACTIONS, onServerPossibleActions);
            socket.off(Events.SERVER_PROCESSED_ACTIONS, onServerProcessedActions);
            socket.off(Events.SERVER_ACTION_ERROR, onServerActionError);
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
                                canInteract={canInteract}
                            />
                        ))}
                    </GridRow>
                ))}
            </GridInner>
            {showTurnSwapImage && <TurnSwapImage imagePath={turnSwapImagePath} />}
            {actionErrorMessage && <GameError errorMessage={actionErrorMessage} />}
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
