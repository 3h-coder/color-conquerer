import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ContainerProps } from "../../components/containers";
import LoadingSpinner from "../../components/LoadingSpinner";
import SingleButtonModal from "../../components/modals/SingleButtonModal";
import { useMatchInfo } from "../../contexts/MatchContext";
import { usePlayerInfo } from "../../contexts/PlayerContext";
import { usePlayerMode } from "../../contexts/PlayerModeContext";
import { useTurnInfo } from "../../contexts/TurnContext";
import { ErrorDto } from "../../dto/ErrorDto";
import { EndingReason, MatchClosureDto } from "../../dto/MatchClosureDto";
import { MessageDto } from "../../dto/MessageDto";
import { TurnInfoDto } from "../../dto/TurnInfoDto";
import { Events } from "../../enums/events";
import { ModalIcon } from "../../enums/modalIcons";
import { PlayerMode } from "../../enums/playerMode";
import { constants, EMPTY_STRING, socket } from "../../env";
import { developmentLog } from "../../utils/loggingUtils";
import ActionBoard from "./components/action_board/ActionBoard";
import GameGrid from "./components/GameGrid";
import GameTopInfo from "./components/GameTopInfo";
import MyPlayerInfo from "./components/MyPlayerInfo";
import OpponentInfo from "./components/OpponentInfo";
import RightSideControls from "./components/RightSideControls";

export default function PlayContent() {
  const navigate = useNavigate();
  const {
    matchInfo,
    loading: matchInfoLoading,
    failedToResolve: failedToResolveMatchInfo,
  } = useMatchInfo();
  const {
    playerId,
    loading: playerInfoLoading,
    failedToResolve: failedToResolvePlayerInfo,
  } = usePlayerInfo();
  const { turnInfo, setTurnInfo } = useTurnInfo();
  const { setPlayerMode } = usePlayerMode();


  const [waitingText, setWaitingText] = useState(EMPTY_STRING);
  const [canRenderContent, setCanRenderContent] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalText, setModalText] = useState(EMPTY_STRING);
  const [modalIcon, setModalIcon] = useState(ModalIcon.None);
  const [modalExit, setModalExit] = useState<() => unknown>(() => {
    return () => setModalVisible(false);
  });

  // Connect to the server on mount/rendering
  // If the connection fails, redirects to the home page
  useEffect(() => {
    connectToServer();

    function connectToServer() {
      if (matchInfoLoading || playerInfoLoading) return;

      if (failedToResolveMatchInfo || failedToResolvePlayerInfo) {
        localStorage.setItem(
          constants.localStorageKeys.homeError,
          "Failed to connect to your match"
        );
        navigate("/");
      } else {
        if (!socket.connected) socket.connect();

        setWaitingText("Connecting to your match...");
        socket.emit(Events.CLIENT_READY);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [matchInfo, matchInfoLoading, playerId, playerInfoLoading]);

  // React to a turnInfo update
  useEffect(() => {
    resetPlayerModeOnTurnInfoUpdate();

    function resetPlayerModeOnTurnInfoUpdate() {
      setPlayerMode(PlayerMode.IDLE);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [turnInfo]);

  // Socket events
  useEffect(() => {
    function onSetWaitingText(messageDto: MessageDto) {
      setWaitingText(messageDto.message);
    }

    function onMatchBeginning(turnInfoDto: TurnInfoDto) {
      onMatchOngoing(turnInfoDto);
    }

    function onMatchOngoing(turnInfoDto: TurnInfoDto) {
      setCanRenderContent(true);
      setTurnInfo(turnInfoDto);
      developmentLog(
        `The match is ongoing.\nThere are ${turnInfoDto.durationInS} seconds left in the turn`
      );
    }

    function onTurnSwap(turnInfoDto: TurnInfoDto) {
      developmentLog(
        `Turn swap!\nThe new turn lasts ${turnInfoDto.durationInS} seconds `
      );
      setTurnInfo(turnInfoDto);
    }

    function onMatchEnded(matchClosureDto: MatchClosureDto) {
      developmentLog("Received match ending ", matchClosureDto);

      setModalIcon(ModalIcon.None);
      setModalText(getMatchEndingText(matchClosureDto));
      setModalVisible(true);
      setModalExit(() => {
        return () => navigate("/");
      });

      socket.emit(Events.CLIENT_CLEAR_SESSION);
      socket.disconnect();
    }

    function onError(errorDto: ErrorDto) {
      if (!errorDto.displayToUser) return;

      setModalIcon(ModalIcon.Error);
      setModalText(errorDto.error);
      setModalVisible(true);

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

    socket.on(Events.SERVER_SET_WAITING_TEXT, onSetWaitingText);
    socket.on(Events.SERVER_MATCH_START, onMatchBeginning);
    socket.on(Events.SERVER_MATCH_ONGOING, onMatchOngoing);
    socket.on(Events.SERVER_TURN_SWAP, onTurnSwap);
    socket.on(Events.SERVER_MATCH_END, onMatchEnded);
    socket.on(Events.SERVER_ERROR, onError);
    socket.on(Events.SERVER_REDIRECT, onRedirection);

    // Ensure the event handlers are attached only once on component mounting
    return () => {
      socket.off(Events.SERVER_SET_WAITING_TEXT, onSetWaitingText);
      socket.off(Events.SERVER_MATCH_START, onMatchBeginning);
      socket.off(Events.SERVER_MATCH_ONGOING, onMatchOngoing);
      socket.off(Events.SERVER_TURN_SWAP, onTurnSwap);
      socket.off(Events.SERVER_MATCH_END, onMatchEnded);
      socket.off(Events.SERVER_ERROR, onError);
      socket.off(Events.SERVER_REDIRECT, onRedirection);
    };
  });

  function getMatchEndingText(matchClosureDto: MatchClosureDto) {
    if (matchClosureDto.endingReason === EndingReason.DRAW || !matchClosureDto.winner) return "Draw";

    const isWinner = matchClosureDto.winner.playerId === playerId;
    if (matchClosureDto.endingReason === EndingReason.PLAYER_LEFT && isWinner)
      return "Your opponent left";
    else if (
      matchClosureDto.endingReason === EndingReason.NEVER_JOINED &&
      isWinner
    )
      return "Your opponent did not join the match";
    else if (isWinner) return "Victory!";
    else return "Defeat";
  }

  return (
    <PageContainer>
      {canRenderContent ? (
        <>
          {turnInfo && <GameTopInfo />}
          <MainInnerContainer>
            <OpponentInfo />
            <GameGrid />
            <MyPlayerInfo />
            <ActionBoard />
            <RightSideContainer>
              <RightSideControls />
            </RightSideContainer>
          </MainInnerContainer>
        </>
      ) : (
        <>
          <LoadingSpinner className="initial-loading" />
          <h3>{waitingText}</h3>
        </>
      )}
      {modalVisible && (
        <SingleButtonModal buttonText="OK" onClose={modalExit} icon={modalIcon}>
          <h3 className="no-margin">{modalText}</h3>
        </SingleButtonModal>
      )}
    </PageContainer>
  );
}

function PageContainer(props: ContainerProps) {
  return <div className="page-container">{props.children}</div>;
}

function MainInnerContainer(props: ContainerProps) {
  return <div className="main-inner-container">{props.children}</div>;
}

function RightSideContainer(props: ContainerProps) {
  return <div className="right-side-container">{props.children}</div>;
}