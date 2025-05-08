import { useEffect, useRef, useState } from "react";
import OpponentTurnImage from "../../../../assets/images/Your Opponent Turn.png";
import YourTurnImage from "../../../../assets/images/Your Turn.png";
import { animateActionCallback, animateProcessedAction } from "../../../../board-animations/main";
import { ContainerProps } from "../../../../components/containers";
import { useAnimationContext } from "../../../../contexts/AnimationContext";
import { useGameContext } from "../../../../contexts/GameContext";
import { useMatchContext } from "../../../../contexts/MatchContext";
import { usePlayerContext } from "../../../../contexts/PlayerContext";
import { usePlayerMode } from "../../../../contexts/PlayerModeContext";
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
import { handlePossibleActionsAdditionalData } from "../../../../utils/actionHintUtils";
import { getCellId } from "../../../../utils/cellUtils";
import { delay } from "../../../../utils/domUtils";
import { developmentLog } from "../../../../utils/loggingUtils";
import Fatigue from "./Fatigue";
import GameCell from "./GameCell";
import GameError from "./GameError";
import SpellAction from "./SpellAction";
import TurnSwapImage from "./TurnSwapImage";
import { useAttachedCellBehaviors } from "./hooks/useAttachedCellBehaviors";
import { useCellEffectSync } from "./hooks/useCellEffectSync";
import "./styles/GameGrid.css";

export default function GameGrid() {
    const { matchInfo, onEmit } = useMatchContext();
    const { playerId, isPlayer1 } = usePlayerContext();
    const { turnContext, canInteract, setCanInteract } = useTurnContext();
    const { setGameContext } = useGameContext();
    const { getAnimationOngoing, signalAnimationStart, signalAnimationEnd } = useAnimationContext();
    const { setPlayerMode } = usePlayerMode();

    const [turnSwapImagePath, setTurnSwapImagePath] = useState(YourTurnImage);
    const [showTurnSwapImage, setShowTurnSwapImage] = useState(false);
    const [isMyTurn, setIsMyTurn] = useState(false);
    const [actionErrorMessage, setActionErrorMessage] = useState(EMPTY_STRING);
    const [actionSpell, setActionSpell] = useState<PartialSpellDto | null>(null);
    const [fatigueDamage, setFatigueDamage] = useState<number | null>(null);
    const [boardArray, setBoardArray] = useState(matchInfo.boardArray);
    const { canDisplayCellEffects, triggerCellEffectSync } = useCellEffectSync();
    const {
        attachedCellBehaviors,
        setAttachedCellBehaviors,
        cleanupAttachedCellBehaviors
    } = useAttachedCellBehaviors(matchInfo.boardArray.length);

    const callbackAnimationQueueRef = useRef<ActionCallbackDto[]>([]);
    const [animatingCallbacks, setAnimatingCallbacks] = useState(false);

    useEffect(() => {
        const cleanup = onEmit((event, _args) => {
            if (event !== Events.CLIENT_CELL_CLICK)
                cleanupAttachedCellBehaviors();
        });

        return cleanup;
    }, [onEmit]);

    // React to a turnContext update (from either a turn change or a page refresh)
    // - Set the board array
    // - Set the players game infos (HP/MP)
    // - Reset the error message
    // - Reset the attached cell behaviors
    // - Show the turn swap image
    // - Enable/disable button interactions
    useEffect(() => {
        reactToTurnChange();

        async function reactToTurnChange() {
            await handleTurnContextChangeAndInteractionEnabling();
            cleanupAttachedCellBehaviors();
        }

        async function handleTurnContextChangeAndInteractionEnabling() {
            const isCurrentPlayerTurn = turnContext.currentPlayerId === playerId;
            setIsMyTurn(isCurrentPlayerTurn);

            if (turnContext === undefinedTurnContext)
                return;

            setCanInteract(false);

            updateGameElements(isCurrentPlayerTurn);
            if (!turnContext.notifyTurnChange) {
                setCanInteract(isCurrentPlayerTurn);
                return;
            }

            await triggerTurnChangeAnimations(isCurrentPlayerTurn);
        }

        function updateGameElements(isCurrentPlayerTurn: boolean) {
            setBoardArray(turnContext.gameContext.gameBoard);
            setPlayerResourcesWithoutApplyingFatigueDamage(isCurrentPlayerTurn);
            setActionErrorMessage(EMPTY_STRING);
        }

        function setPlayerResourcesWithoutApplyingFatigueDamage(isCurrentPlayerTurn: boolean) {
            const newTurnProcessingInfo = turnContext.newTurnProcessingInfo;
            const fatigueDamage = newTurnProcessingInfo?.fatigueDamage ?? 0;

            if (fatigueDamage > 0) {
                setGameContext(prevContext => {
                    const prevBundle = prevContext.playerResourceBundle;
                    // Clone the bundle to avoid mutating state
                    const gameContext = structuredClone(turnContext.gameContext);
                    const bundle = gameContext.playerResourceBundle;

                    // Prevent the fatigue damage from being applied straight away
                    if (isCurrentPlayerTurn) {
                        if (isPlayer1) {
                            bundle.player1Resources.currentHP = prevBundle.player1Resources.currentHP;
                        } else {
                            bundle.player2Resources.currentHP = prevBundle.player2Resources.currentHP;
                        }
                    } else {
                        if (isPlayer1) {
                            bundle.player2Resources.currentHP = prevBundle.player2Resources.currentHP;
                        } else {
                            bundle.player1Resources.currentHP = prevBundle.player1Resources.currentHP;
                        }
                    }

                    return gameContext;
                });
            } else {
                setGameContext(turnContext.gameContext);
            }
        }

        async function triggerTurnChangeAnimations(isCurrentPlayerTurn: boolean) {
            signalAnimationStart();

            // Trigger the turn swap image animation
            setTurnSwapImagePath(isCurrentPlayerTurn ? YourTurnImage : OpponentTurnImage);
            setShowTurnSwapImage(true);

            await delay(2000);
            setShowTurnSwapImage(false);

            // Trigger the fatigue damage animation if any
            if (turnContext.newTurnProcessingInfo !== null && turnContext.newTurnProcessingInfo.fatigueDamage > 0) {
                const fatigueDamage = turnContext.newTurnProcessingInfo.fatigueDamage;
                setFatigueDamage(fatigueDamage);
                await delay(1900);
                setFatigueDamage(null);

                // Apply the real resources bundle, including the fatigue damage
                setGameContext(turnContext.gameContext);
            }

            setCanInteract(isCurrentPlayerTurn);
            signalAnimationEnd();
        }
    }, [turnContext, playerId]);

    // Action callbacks animations
    useEffect(() => {
        if (!animatingCallbacks)
            return;

        animateActionCallbacks();

        async function animateActionCallbacks() {
            if (isMyTurn)
                setCanInteract(false);

            try {
                if (!getAnimationOngoing())
                    signalAnimationStart(true);

                while (callbackAnimationQueueRef.current.length > 0) {
                    const actionCallback = callbackAnimationQueueRef.current.shift();
                    await animateActionCallback(actionCallback!, isPlayer1, { setBoardArray, setActionSpell, setGameContext });
                }
                triggerCellEffectSync();
            } finally {
                setAnimatingCallbacks(false);

                if (isMyTurn)
                    setCanInteract(true);

                // Note : This is a hack to prevent pixi from stopping while some particles are still emitting
                // It should be fixed in the future by using a better way to handle the animation end
                await delay(1500);
                signalAnimationEnd(true);
            }
        }
    }, [animatingCallbacks]);

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
            // Update the player mode for the dependent components to react to
            setPlayerMode(possibleActions.playerMode);

            const transientBoardArray = possibleActions.transientBoardArray;
            // Apply the new coloring and selectable cells
            setBoardArray(transientBoardArray);

            if (possibleActions.additionalData)
                handlePossibleActionsAdditionalData(possibleActions, setAttachedCellBehaviors);

            triggerCellEffectSync();
        }

        async function onServerProcessedActions(processedActionDto: ProcessedActionDto) {
            developmentLog("Received the processed action", processedActionDto);

            cleanupAttachedCellBehaviors();

            // Update the player mode for the dependent components to react to
            setPlayerMode(processedActionDto.playerMode);

            // Update the player info bundle to display the proper HP/MP values
            setGameContext(processedActionDto.updatedGameContext);

            // Trigger animations
            await animateProcessedAction(processedActionDto.processedAction, isPlayer1, isMyTurn, boardArray, setActionSpell);

            // Update the board array with the new cell info
            if (isMyTurn && processedActionDto.overridingTransientBoard) {
                setBoardArray(processedActionDto.overridingTransientBoard);
                triggerCellEffectSync();
            } else {
                setBoardArray(processedActionDto.updatedGameContext.gameBoard);
            }
        }

        async function onServerActionCallback(actionCallback: ActionCallbackDto) {
            developmentLog("Received the action callback", actionCallback);

            callbackAnimationQueueRef.current.push(actionCallback);
            setAnimatingCallbacks(true);
        }

        function onServerActionError(errorMessageDto: MessageDto) {
            const errorMessage = errorMessageDto.message;
            developmentLog("Received the action error", errorMessage);

            setActionErrorMessage(errorMessage);
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
                                canDisplayEffects={canDisplayCellEffects}
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

            { /* Fatigue animation */}
            {fatigueDamage && <Fatigue fatigue={fatigueDamage} />}
        </GridOuter>
    );
}

export function GridOuter(props: ContainerProps) {
    return <div id="grid-outer">{props.children}</div>;
}

export function GridInner(props: ContainerProps) {
    return (
        <div id="grid-inner" style={props.style}>
            {props.children}
        </div>
    );
}

export function GridRow(props: ContainerProps) {
    return <div className="row">{props.children}</div>;
}
