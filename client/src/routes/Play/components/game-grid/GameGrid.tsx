import { useEffect, useRef, useState } from "react";
import OpponentTurnImage from "../../../../assets/images/Your Opponent Turn.png";
import YourTurnImage from "../../../../assets/images/Your Turn.png";
import { animateActionCallbacks as animateActionCallback, animateProcessedAction, handlePossibleActionsAdditionalData } from "../../../../board-animations/main";
import { ContainerProps } from "../../../../components/containers";
import { useAnimationContext } from "../../../../contexts/AnimationContext";
import { useMatchInfo } from "../../../../contexts/MatchContext";
import { usePlayerInfo } from "../../../../contexts/PlayerContext";
import { usePlayerMode } from "../../../../contexts/PlayerModeContext";
import { usePlayersGameInfo } from "../../../../contexts/PlayersGameInfoContext";
import { useTurnContext } from "../../../../contexts/TurnContext";
import { ActionCallbackDto } from "../../../../dto/actions/ActionCallbackDto";
import { PossibleActionsDto } from "../../../../dto/actions/PossibleActionsDto";
import { ProcessedActionDto } from "../../../../dto/actions/ProcessedActionDto";
import { undefinedTurnContext } from "../../../../dto/gameState/TurnContextDto";
import { MessageDto } from "../../../../dto/misc/MessageDto";
import { PartialSpellDto } from "../../../../dto/spell/PartialSpellDto";
import { Events } from "../../../../enums/events";
import { EMPTY_STRING, socket } from "../../../../env";
import { cellStyle } from "../../../../style/constants";
import { create2DArray } from "../../../../utils/arrayUtils";
import {
    AttachedCellBehavior,
    getCellId,
} from "../../../../utils/cellUtils";
import { developmentLog } from "../../../../utils/loggingUtils";
import GameCell from "./GameCell";
import GameError from "./GameError";
import SpellAction from "./SpellAction";
import TurnSwapImage from "./TurnSwapImage";
import "./styles/GameGrid.css";

export default function GameGrid() {
    const { animationOngoing, signalAnimationStart, signalAnimationEnd } = useAnimationContext();
    const { matchInfo } = useMatchInfo();
    const { playerId, isPlayer1 } = usePlayerInfo();
    const { turnContext, canInteract, setCanInteract } = useTurnContext();
    const { setPlayerResourceBundle } = usePlayersGameInfo();
    const { setPlayerMode } = usePlayerMode();

    const [turnSwapImagePath, setTurnSwapImagePath] = useState(YourTurnImage);
    const [showTurnSwapImage, setShowTurnSwapImage] = useState(false);
    const [isMyTurn, setIsMyTurn] = useState(false);
    const [actionErrorMessage, setActionErrorMessage] = useState(EMPTY_STRING);
    const [actionSpell, setActionSpell] = useState<PartialSpellDto | null>(null);

    const [boardArray, setBoardArray] = useState(matchInfo.boardArray);
    const [canDisplayPossibleActions, setCanDisplayPossibleActions] = useState(true);
    const [attachedCellBehaviors, setAttachedCellBehaviors] = useState<(AttachedCellBehavior | undefined)[][]>(
        create2DArray<AttachedCellBehavior>(matchInfo.boardArray[0].length)
    );


    const callbackAnimationQueueRef = useRef<ActionCallbackDto[]>([]);

    /** Used to force cells to restart their animations all together synchronously */
    function triggerPossibleActionsAnimationSync() {
        setCanDisplayPossibleActions(false);
        setTimeout(() => setCanDisplayPossibleActions(true), 100); // Force a reflow
    }

    // React to a turnContext update (from either a turn change or a page refresh)
    // - Set the board array
    // - Set the players game infos (HP/MP)
    useEffect(() => {
        handleturnContextUpdate();

        function handleturnContextUpdate() {
            setBoardArray(turnContext.gameContext.gameBoard);
            setPlayerResourceBundle(turnContext.gameContext.playerResourceBundle);
            setActionErrorMessage(EMPTY_STRING);

            if (turnContext === undefinedTurnContext) return;
            setIsMyTurn(turnContext.currentPlayerId === playerId);
        }
    }, [turnContext]);

    // React to the isMyTurn change
    useEffect(() => {
        controlInteractionEnabling();
        resetNonPermanentBehaviors();

        // Allows/disallows the player to interact with elements such as the game cells
        // or the end turn button according to whether it is their turn or not and if the
        // turn swap animation is done running.
        function controlInteractionEnabling() {
            setCanInteract(false);

            // If not a turn change, the user may interact immediately
            // if it's their turn (typically after a page refresh)
            if (!turnContext.notifyTurnChange) {
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

        function resetNonPermanentBehaviors() {
            setAttachedCellBehaviors(prev => {
                const newBehaviors = prev.map(row =>
                    row.map(behavior =>
                        behavior?.isPermanent ? behavior : undefined
                    )
                );
                return newBehaviors;
            });
        }
    }, [isMyTurn]);

    // Action callbacks animations
    useEffect(() => {
        if (!animationOngoing)
            return;

        animateActionCallbacks();

        async function animateActionCallbacks() {
            if (isMyTurn)
                setCanInteract(false);
            try {
                while (callbackAnimationQueueRef.current.length > 0) {
                    const actionCallback = callbackAnimationQueueRef.current.shift();
                    await animateActionCallback(actionCallback!, isPlayer1, { setBoardArray, setActionSpell, setPlayerResourceBundle });
                }
                triggerPossibleActionsAnimationSync();
            } finally {
                signalAnimationEnd();

                if (isMyTurn)
                    setCanInteract(true);
            }
        }
    }, [animationOngoing]);

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
    }, [actionErrorMessage]);

    // Register socket events
    useEffect(() => {

        function onServerPossibleActions(possibleActions: PossibleActionsDto) {
            developmentLog("Received the possible actions", possibleActions);

            // Update the player mode for the dependent components to react to
            setPlayerMode(possibleActions.playerMode);

            const transientBoardArray = possibleActions.transientBoardArray;
            // Apply the new coloring and selectable cells
            setBoardArray(transientBoardArray);

            if (possibleActions.additionalData)
                handlePossibleActionsAdditionalData(possibleActions, setAttachedCellBehaviors);

            triggerPossibleActionsAnimationSync();
        }

        function onServerProcessedActions(processedActionDto: ProcessedActionDto) {
            developmentLog("Received the processed actions", processedActionDto);

            // Update the player mode for the dependent components to react to
            setPlayerMode(processedActionDto.playerMode);

            // Update the player info bundle to display the proper HP/MP values
            setPlayerResourceBundle(processedActionDto.updatedGameContext.playerResourceBundle);

            // Trigger animations
            animateProcessedAction(processedActionDto.processedAction, isPlayer1, isMyTurn, boardArray, setActionSpell);

            // Update the board array with the new cell info
            if (isMyTurn && processedActionDto.overridingTransientBoard) {
                setBoardArray(processedActionDto.overridingTransientBoard);
                triggerPossibleActionsAnimationSync();
            } else {
                setBoardArray(processedActionDto.updatedGameContext.gameBoard);
            }
        }

        async function onServerActionCallback(actionCallback: ActionCallbackDto) {
            developmentLog("Received the action callback", actionCallback);

            callbackAnimationQueueRef.current.push(actionCallback);
            if (!animationOngoing)
                signalAnimationStart();
        }

        function onServerActionError(errorMessageDto: MessageDto) {
            const gameErrorMessage = errorMessageDto.message;
            developmentLog("Received the game error", gameErrorMessage);

            setActionErrorMessage(gameErrorMessage);
        }

        socket.on(Events.SERVER_POSSIBLE_ACTIONS, onServerPossibleActions);
        socket.on(Events.SERVER_PROCESSED_ACTIONS, onServerProcessedActions);
        socket.on(Events.SERVER_ACTION_ERROR, onServerActionError);
        socket.on(Events.SERVER_ACTION_CALLBACK, onServerActionCallback);

        return () => {
            socket.off(Events.SERVER_POSSIBLE_ACTIONS, onServerPossibleActions);
            socket.off(Events.SERVER_PROCESSED_ACTIONS, onServerProcessedActions);
            socket.off(Events.SERVER_ACTION_ERROR, onServerActionError);
            socket.off(Events.SERVER_ACTION_CALLBACK, onServerActionCallback);
        };
    });

    const gridStyle: React.CSSProperties = {
        transform: `${isPlayer1 ? cellStyle.rotate180deg : undefined}`,
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
                                canDisplayPossibleActions={canDisplayPossibleActions}
                                attachedBehavior={attachedCellBehaviors[rowIndex][colIndex]}
                            />
                        ))}
                    </GridRow>
                ))}
            </GridInner>
            { /* Image whenever the turn changes */}
            {showTurnSwapImage && <TurnSwapImage imagePath={turnSwapImagePath} />}

            { /* Error message from the server to display */}
            {actionErrorMessage && <GameError errorMessage={actionErrorMessage} />}

            { /* Spell description card whenever a player casts a spell */}
            {actionSpell && <SpellAction spell={actionSpell} />}
        </GridOuter>
    );
}

function GridOuter(props: ContainerProps) {
    return <div id="grid-outer">{props.children}</div>;
}

function GridInner(props: ContainerProps) {
    return (
        <div id="grid-inner" style={props.style}>
            {props.children}
        </div>
    );
}

function GridRow(props: ContainerProps) {
    return <div className="row">{props.children}</div>;
}
