import { useEffect, useRef, useState } from "react";
import OpponentTurnImage from "../../../../assets/images/Your Opponent Turn.png";
import YourTurnImage from "../../../../assets/images/Your Turn.png";
import { animateActionCallback, animateProcessedAction } from "../../../../board-animations/main";
import { ContainerProps } from "../../../../components/containers";
import { useAnimationContext } from "../../../../contexts/AnimationContext";
import { useMatchContext } from "../../../../contexts/MatchContext";
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
    const { playerId, isPlayer1 } = usePlayerInfo();
    const { turnContext, canInteract, setCanInteract } = useTurnContext();
    const { setPlayerResourceBundle } = usePlayersGameInfo();
    const { getAnimationOngoing, addEndOfAnimationCallback, signalAnimationStart, signalAnimationEnd } = useAnimationContext();
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
        const cleanupFunction = handleTurnContextAndInteraction();
        cleanupAttachedCellBehaviors();

        return () => {
            if (typeof cleanupFunction === "function") cleanupFunction();
        };

        function handleTurnContextAndInteraction() {
            developmentLog("Received the turn context", turnContext);
            // Handle turnContext update
            setBoardArray(turnContext.gameContext.gameBoard);
            setPlayerResourceBundle(turnContext.gameContext.playerResourceBundle);
            setActionErrorMessage(EMPTY_STRING);

            if (turnContext === undefinedTurnContext)
                return;

            const isCurrentPlayerTurn = turnContext.currentPlayerId === playerId;
            setIsMyTurn(isCurrentPlayerTurn);

            // Control interaction enabling
            setCanInteract(false);

            if (!turnContext.notifyTurnChange) {
                setCanInteract(isCurrentPlayerTurn);
                return;
            }

            signalAnimationStart();

            // Trigger the turn swap image animation
            setTurnSwapImagePath(isCurrentPlayerTurn ? YourTurnImage : OpponentTurnImage);
            setShowTurnSwapImage(true);

            // Wait for the turn image animation to end before allowing interaction
            const timeout = setTimeout(() => {
                setShowTurnSwapImage(false);
                setCanInteract(isCurrentPlayerTurn);
                signalAnimationEnd();
            }, 2000);

            return () => clearTimeout(timeout);
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
                    await animateActionCallback(actionCallback!, isPlayer1, { setBoardArray, setActionSpell, setPlayerResourceBundle });
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
            developmentLog("Received the possible actions", possibleActions);

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
            developmentLog("Received the processed actions", processedActionDto);

            cleanupAttachedCellBehaviors();

            // Update the player mode for the dependent components to react to
            setPlayerMode(processedActionDto.playerMode);

            // Update the player info bundle to display the proper HP/MP values
            setPlayerResourceBundle(processedActionDto.updatedGameContext.playerResourceBundle);

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

        async function onServerFatigue(fatigueDamage: number) {
            addEndOfAnimationCallback(animateFatigue);

            async function animateFatigue() {
                try {
                    // Signal the animation start for the eventual match end t*&é"'(-è_tfygr-) 
                    // trigger afterwards
                    if (!getAnimationOngoing())
                        signalAnimationStart();

                    setFatigueDamage(fatigueDamage);
                    await delay(1900);
                    setFatigueDamage(null);
                } finally {
                    signalAnimationEnd();
                }
            }
        }

        socket.on(Events.SERVER_POSSIBLE_ACTIONS, onServerPossibleActions);
        socket.on(Events.SERVER_PROCESSED_ACTIONS, onServerProcessedActions);
        socket.on(Events.SERVER_ACTION_ERROR, onServerActionError);
        socket.on(Events.SERVER_ACTION_CALLBACK, onServerActionCallback);
        socket.on(Events.SERVER_FATIGUE, onServerFatigue);

        return () => {
            socket.off(Events.SERVER_POSSIBLE_ACTIONS, onServerPossibleActions);
            socket.off(Events.SERVER_PROCESSED_ACTIONS, onServerProcessedActions);
            socket.off(Events.SERVER_ACTION_ERROR, onServerActionError);
            socket.off(Events.SERVER_ACTION_CALLBACK, onServerActionCallback);
            socket.off(Events.SERVER_FATIGUE, onServerFatigue);
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
