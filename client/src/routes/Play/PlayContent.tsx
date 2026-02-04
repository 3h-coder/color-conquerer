import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ContainerProps } from "../../components/containers";
import LoadingSpinner from "../../components/LoadingSpinner";
import SingleButtonModal from "../../components/modals/SingleButtonModal";
import { useAnimationContext } from "../../contexts/AnimationContext";
import { useMatchContext } from "../../contexts/MatchContext";
import { usePlayerContext } from "../../contexts/PlayerContext";
import { usePlayerMode } from "../../contexts/PlayerModeContext";
import { useTurnContext } from "../../contexts/TurnContext";
import { TurnContextDto } from "../../dto/gameState/TurnContextDto";
import { EndingReason, MatchClosureDto } from "../../dto/match/MatchClosureDto";
import { ErrorDto } from "../../dto/misc/ErrorDto";
import { MessageDto } from "../../dto/misc/MessageDto";
import { Events } from "../../enums/events";
import { ModalIcon } from "../../enums/modalIcons";
import { PlayerMode } from "../../enums/playerMode";
import { EMPTY_STRING, isDevelopment, socket } from "../../env";
import { developmentLog } from "../../utils/loggingUtils";
import { fullPaths } from "../paths";
import ActionBoard from "./components/action-board/ActionBoard";
import GameGrid from "./components/game-grid/GameGrid";
import GameTopInfo from "./components/game-top-info/GameTopInfo";
import InactivityWarning from "./components/inactivity-warning/InactivityWarning";
import MyPlayerResources from "./components/player-resources/MyPlayerResources";
import OpponentResources from "./components/player-resources/OpponentResources";
import SideControls from "./components/side-controls/SideControls";

export default function PlayContent() {
  const navigate = useNavigate();
  const {
    loading: matchInfoLoading,
    failedToResolve: failedToResolveMatchInfo,
  } = useMatchContext();
  const {
    playerId,
    loading: playerInfoLoading,
    failedToResolve: failedToResolvePlayerInfo,
  } = usePlayerContext();
  const { getAnimationOngoing, addEndOfAnimationCallback } = useAnimationContext();
  const { turnContext, setTurnContext } =
    useTurnContext();
  const { setPlayerMode } = usePlayerMode();

  const [waitingText, setWaitingText] = useState(EMPTY_STRING);
  const [canRenderContent, setCanRenderContent] = useState(false);
  const [showInactivityWarning, setShowInactivityWarning] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalText, setModalText] = useState(EMPTY_STRING);
  const [modalIcon, setModalIcon] = useState(ModalIcon.None);
  const [modalExit, setModalExit] = useState<() => unknown>(() => {
    return () => setModalOpen(false);
  });
  const FAILED_TO_CONNECT_ERROR = "Failed to connect to your match";

  // Connect to the server on mount/rendering
  // This is used to assert that the player is effectively in a match.
  // If not, they will be redirected to the home page.
  useEffect(() => {
    connectToServer();

    function connectToServer() {
      if (matchInfoLoading || playerInfoLoading)
        return;

      if (failedToResolveMatchInfo || failedToResolvePlayerInfo) {
        if (socket.connected)
          socket.disconnect();
        sendHomeWithError(FAILED_TO_CONNECT_ERROR);
      }

      else {

        if (!socket.connected)
          socket.connect();

        setWaitingText("Connecting to your match...");
        socket.emit(Events.CLIENT_READY);
      }
    }
  }, [matchInfoLoading, playerInfoLoading]);

  // React to a turnInfo update
  useEffect(() => {
    resetPlayerModeOnTurnInfoUpdate();

    function resetPlayerModeOnTurnInfoUpdate() {
      setPlayerMode(PlayerMode.IDLE);
    }
  }, [turnContext]);

  // Socket events
  useEffect(() => {
    function onWaitingForOpponent() {
      setWaitingText("Waiting for your opponent...");
    }

    function onMatchBeginning(turnContextDto: TurnContextDto) {
      onMatchOngoing(turnContextDto);
    }

    function onMatchOngoing(turnContextDto: TurnContextDto) {
      setCanRenderContent(true);
      setTurnContext(turnContextDto);
      developmentLog(
        `The match is ongoing.\nThere are ${turnContextDto.remainingTimeInS} seconds left in the turn`
      );
    }

    function onTurnSwap(turnContextDto: TurnContextDto) {
      developmentLog(
        `Turn swap!\nThe new turn lasts ${turnContextDto.remainingTimeInS} seconds `
      );
      setTurnContext(turnContextDto);
    }

    function onServerInactivityWarning() {
      setShowInactivityWarning(true);
    }

    function onMatchEnded(matchClosureDto: MatchClosureDto) {
      developmentLog("Received match ending ", matchClosureDto);

      if (getAnimationOngoing())
        addEndOfAnimationCallback(handleMatchEnding);
      else
        handleMatchEnding();

      function handleMatchEnding() {
        setModalIcon(ModalIcon.None);
        setModalText(getMatchEndingText(playerId, matchClosureDto));
        setModalOpen(true);
        setModalExit(() => {
          return () => navigate(fullPaths.home, { state: { intentionalDisconnect: true } });
        });

        socket.disconnect();
      }
    }

    function onServerError(errorDto: ErrorDto) {
      developmentLog("Received the error", errorDto);
      if (!errorDto.displayToUser)
        return;

      showErrorInModal(errorDto);

      if (errorDto.socketConnectionKiller) {
        socket.disconnect();
        setModalExit(() => {
          return () => navigate(fullPaths.home, { state: { intentionalDisconnect: true } });
        });
      }
    }

    function onHomeErrorRedirection(messageDto: MessageDto) {
      sendHomeWithError(messageDto.message);
    }

    function onDisconnect() {
      // This is to facilitate development in order to not have to
      // manually go back to the home screen each time the server is reboot.
      // ⚠️ Do not use in production as page refreshes will cause disconnection.
      if (!isDevelopment)
        return;

      // navigate(fullPaths.home);
    }

    socket.on(Events.DISCONNECT, onDisconnect);
    socket.on(Events.SERVER_WAITING_FOR_OPPONENT, onWaitingForOpponent);
    socket.on(Events.SERVER_MATCH_START, onMatchBeginning);
    socket.on(Events.SERVER_MATCH_ONGOING, onMatchOngoing);
    socket.on(Events.SERVER_TURN_SWAP, onTurnSwap);
    socket.on(Events.SERVER_INACTIVITY_WARNING, onServerInactivityWarning);
    socket.on(Events.SERVER_MATCH_END, onMatchEnded);
    socket.on(Events.SERVER_ERROR, onServerError);
    socket.on(Events.SERVER_HOME_ERROR_REDIRECT, onHomeErrorRedirection);

    // Ensure the event handlers are attached only once on component mounting
    return () => {
      socket.off(Events.DISCONNECT, onDisconnect);
      socket.off(Events.SERVER_WAITING_FOR_OPPONENT, onWaitingForOpponent);
      socket.off(Events.SERVER_MATCH_START, onMatchBeginning);
      socket.off(Events.SERVER_MATCH_ONGOING, onMatchOngoing);
      socket.off(Events.SERVER_TURN_SWAP, onTurnSwap);
      socket.off(Events.SERVER_INACTIVITY_WARNING, onServerInactivityWarning);
      socket.off(Events.SERVER_MATCH_END, onMatchEnded);
      socket.off(Events.SERVER_ERROR, onServerError);
      socket.off(Events.SERVER_HOME_ERROR_REDIRECT, onHomeErrorRedirection);
    };
  }, [playerId]);

  function sendHomeWithError(errorMessage: string) {
    navigate(fullPaths.home, { state: { error: errorMessage, intentionalDisconnect: true } });
  }

  function showErrorInModal(errorDto: ErrorDto) {
    setModalIcon(ModalIcon.Error);
    setModalText(errorDto.error);
    setModalOpen(true);
  }

  function getMatchEndingText(
    playerId: string,
    matchClosureDto: MatchClosureDto
  ) {
    const endingReason = matchClosureDto.endingReason;

    if (endingReason === EndingReason.DRAW || !matchClosureDto.winner)
      return "Draw";

    const isWinner = matchClosureDto.winner.playerId === playerId;

    if ((endingReason === EndingReason.PLAYER_LEFT || endingReason === EndingReason.PLAYER_INACTIVE) && isWinner)
      return "Your opponent left";

    else if (endingReason === EndingReason.PLAYER_CONCEDED && isWinner)
      return "Your opponent gave up";

    else if (isWinner)
      return "Victory!";

    else if (endingReason === EndingReason.PLAYER_INACTIVE)
      return "You lost due to being inactive";

    else return "Defeat";
  }

  return (
    <PageContainer>
      {canRenderContent ? (
        <MainOuterContainer>
          {/* Right side controls -> End turn, concede, etc. */}
          {/* These controls are displayed on top on small screens */}
          <SideControls />

          {/* The player whom it is the turn + turn time bar */}
          <GameTopInfo />

          <MainInnerContainer>
            {/* Opponent information (HP/MP) */}
            <OpponentResources />

            <GameGrid />

            {/* Player information (HP/MP) */}
            <MyPlayerResources />

            {/* Action board -> Spawning cells, casting spells, etc. */}
            <ActionBoard />

            {showInactivityWarning && <InactivityWarning setShowInactivityWarning={setShowInactivityWarning} />}
          </MainInnerContainer>
        </MainOuterContainer>
      ) : (
        <>
          <LoadingSpinner className="initial-loading" />
          <h3>{waitingText}</h3>
        </>
      )}
      <SingleButtonModal
        isOpenState={[modalOpen, setModalOpen]}
        buttonText="OK"
        onClose={modalExit}
        icon={modalIcon}
        style={{ animation: "slide-in 0.5s ease, glow 1s infinite alternate" }}
      >
        <h3 className="no-margin">{modalText}</h3>
      </SingleButtonModal>
    </PageContainer>
  );
}

function PageContainer(props: ContainerProps) {
  return <div className="page-container">{props.children}</div>;
}

function MainOuterContainer(props: ContainerProps) {
  return <div id="main-outer-container">{props.children}</div>;
}

function MainInnerContainer(props: ContainerProps) {
  return <div id="main-inner-container">{props.children}</div>;
}
