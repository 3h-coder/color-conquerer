import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ContainerProps } from "../../components/containers";
import LoadingSpinner from "../../components/LoadingSpinner";
import SingleButtonModal from "../../components/modals/SingleButtonModal";
import { useAnimationContext } from "../../contexts/AnimationContext";
import { useMatchContext } from "../../contexts/MatchContext";
import { usePlayerInfo } from "../../contexts/PlayerContext";
import { usePlayerMode } from "../../contexts/PlayerModeContext";
import { useTurnContext } from "../../contexts/TurnContext";
import { TurnContextDto } from "../../dto/gameState/TurnContextDto";
import { EndingReason, MatchClosureDto } from "../../dto/match/MatchClosureDto";
import { ErrorDto } from "../../dto/misc/ErrorDto";
import { MessageDto } from "../../dto/misc/MessageDto";
import { Events } from "../../enums/events";
import { ModalIcon } from "../../enums/modalIcons";
import { PlayerMode } from "../../enums/playerMode";
import { EMPTY_STRING, isDevelopment, localStorageKeys, socket } from "../../env";
import { developmentLog } from "../../utils/loggingUtils";
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
  } = usePlayerInfo();
  const { getAnimationOngoing, addEndOfAnimationCallback } = useAnimationContext();
  const { turnContext: turnInfo, setTurnContext: setTurnInfo } =
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

  // Connect to the server on mount/rendering
  // If the connection fails, redirects to the home page
  useEffect(() => {
    connectToServer();

    function connectToServer() {
      if (matchInfoLoading || playerInfoLoading) return;

      if (failedToResolveMatchInfo || failedToResolvePlayerInfo) {
        localStorage.setItem(
          localStorageKeys.homePage.error,
          "Failed to connect to your match"
        );
        navigate("/");
      } else {
        if (!socket.connected) socket.connect();

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
  }, [turnInfo]);

  // Socket events
  useEffect(() => {
    function onWaitingForOpponent() {
      setWaitingText("Waiting for your opponent...");
    }

    function onMatchBeginning(turnInfoDto: TurnContextDto) {
      onMatchOngoing(turnInfoDto);
    }

    function onMatchOngoing(turnInfoDto: TurnContextDto) {
      setCanRenderContent(true);
      setTurnInfo(turnInfoDto);
      developmentLog(
        `The match is ongoing.\nThere are ${turnInfoDto.remainingTimeInS} seconds left in the turn`
      );
    }

    function onTurnSwap(turnInfoDto: TurnContextDto) {
      developmentLog(
        `Turn swap!\nThe new turn lasts ${turnInfoDto.remainingTimeInS} seconds `
      );
      setTurnInfo(turnInfoDto);
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
          return () => navigate("/");
        });

        socket.emit(Events.CLIENT_CLEAR_SESSION);
        socket.disconnect();
      }
    }

    function onError(errorDto: ErrorDto) {
      if (!errorDto.displayToUser) return;

      setModalIcon(ModalIcon.Error);
      setModalText(errorDto.error);
      setModalOpen(true);

      if (errorDto.socketConnectionKiller) {
        socket.disconnect();
        setModalExit(() => {
          return () => navigate("/");
        });
      }
    }

    function onRedirection(messageDto: MessageDto) {
      navigate(messageDto.message);
    }

    function onDisconnect() {
      // This is to facilitate development in order to not have to
      // manually go back to the home screen each time the server is reboot.
      // ⚠️ Do not use in production as page refreshes will cause disconnection.
      if (!isDevelopment)
        return;

      // navigate("/");
    }

    socket.on(Events.DISCONNECT, onDisconnect);
    socket.on(Events.SERVER_WAITING_FOR_OPPONENT, onWaitingForOpponent);
    socket.on(Events.SERVER_MATCH_START, onMatchBeginning);
    socket.on(Events.SERVER_MATCH_ONGOING, onMatchOngoing);
    socket.on(Events.SERVER_TURN_SWAP, onTurnSwap);
    socket.on(Events.SERVER_INACTIVITY_WARNING, onServerInactivityWarning);
    socket.on(Events.SERVER_MATCH_END, onMatchEnded);
    socket.on(Events.SERVER_ERROR, onError);
    socket.on(Events.SERVER_REDIRECT, onRedirection);

    // Ensure the event handlers are attached only once on component mounting
    return () => {
      socket.off(Events.DISCONNECT, onDisconnect);
      socket.off(Events.SERVER_WAITING_FOR_OPPONENT, onWaitingForOpponent);
      socket.off(Events.SERVER_MATCH_START, onMatchBeginning);
      socket.off(Events.SERVER_MATCH_ONGOING, onMatchOngoing);
      socket.off(Events.SERVER_TURN_SWAP, onTurnSwap);
      socket.off(Events.SERVER_INACTIVITY_WARNING, onServerInactivityWarning);
      socket.off(Events.SERVER_MATCH_END, onMatchEnded);
      socket.off(Events.SERVER_ERROR, onError);
      socket.off(Events.SERVER_REDIRECT, onRedirection);
    };
  }, [playerId]);

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

    else if (endingReason === EndingReason.NEVER_JOINED && isWinner)
      return "Your opponent did not join the match";

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
        style={{ animation: "slide-in 0.5s ease" }}
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
