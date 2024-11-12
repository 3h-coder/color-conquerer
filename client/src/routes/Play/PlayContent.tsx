import { ReactNode, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import LoadingSpinner from "../../components/LoadingSpinner";
import SingleButtonModal from "../../components/modals/SingleButtonModal";
import { undefinedMatch, useMatchInfo } from "../../contexts/MatchContext";
import { undefinedPlayer, usePlayerInfo } from "../../contexts/PlayerContext";
import { useTurnInfo } from "../../contexts/TurnContext";
import { ErrorDto } from "../../dto/ErrorDto";
import { EndingReason, MatchClosureDto } from "../../dto/MatchClosureDto";
import { MessageDto } from "../../dto/MessageDto";
import { TurnInfoDto } from "../../dto/TurnInfoDto";
import { Events } from "../../enums/events";
import { ModalIcon } from "../../enums/modalIcons";
import { constants, socket } from "../../env";
import { developmentLog } from "../../utils/loggingUtils";
import GameGrid from "./components/GameGrid";
import GameTopInfo from "./components/GameTopInfo";

export default function PlayContent() {
  const navigate = useNavigate();
  const { matchInfo, loading: matchInfoLoading } = useMatchInfo();
  const {
    playerInfo,
    loading: playerInfoLoading,
  } = usePlayerInfo();
  const { turnInfo, setTurnInfo } = useTurnInfo();
  const [waitingText, setWaitingText] = useState("");
  const [canRenderContent, setCanRenderContent] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalText, setModalText] = useState("");
  const [modalIcon, setModalIcon] = useState(ModalIcon.None);
  const [modalExit, setModalExit] = useState<() => unknown>(() => {
    return () => setModalVisible(false);
  });

  useEffect(() => {
    if (matchInfoLoading || playerInfoLoading) return;

    if (matchInfo === undefinedMatch || playerInfo === undefinedPlayer) {
      localStorage.setItem(constants.localStorageKeys.homeError, "Failed to connect to your match")
      navigate("/");
    } else {
      if (!socket.connected) socket.connect();

      setWaitingText("Connecting to your match...");
      socket.emit(Events.CLIENT_READY);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    matchInfo,
    matchInfoLoading,
    playerInfo,
    playerInfoLoading
  ]);

  useEffect(() => {
    function onSetWaitingText(messageDto: MessageDto) {
      setWaitingText(messageDto.message);
    }

    function onMatchBeginning(turnInfoDto: TurnInfoDto) {
      // TODO : Display a big beginning animation on screen here
      onMatchAlreadyStarted(turnInfoDto);
    }

    function onMatchAlreadyStarted(turnInfoDto: TurnInfoDto) {
      setCanRenderContent(true);
      setTurnInfo(turnInfoDto);
      developmentLog(`The match started! \nHow much time is there left ? -> ${turnInfoDto.durationInS} seconds`);
    }

    function onTurnSwap(turnInfoDto: TurnInfoDto) {
      setTurnInfo(turnInfoDto);
      developmentLog(`Turn swap!\nHow much time is there left ? -> ${turnInfoDto.durationInS} seconds `)
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

    socket.on(Events.SERVER_SET_WAITING_TEXT, onSetWaitingText);
    socket.on(Events.SERVER_MATCH_START, onMatchBeginning);
    socket.on(Events.SERVER_MATCH_ONGOING, onMatchAlreadyStarted);
    socket.on(Events.SERVER_TURN_SWAP, onTurnSwap);
    socket.on(Events.SERVER_MATCH_END, onMatchEnded);
    socket.on(Events.SERVER_ERROR, onError);

    return () => {
      socket.off(Events.SERVER_SET_WAITING_TEXT, onSetWaitingText);
      socket.off(Events.SERVER_MATCH_START, onMatchBeginning);
      socket.off(Events.SERVER_MATCH_ONGOING, onMatchAlreadyStarted);
      socket.off(Events.SERVER_TURN_SWAP, onTurnSwap);
      socket.off(Events.SERVER_MATCH_END, onMatchEnded);
      socket.off(Events.SERVER_ERROR, onError);
    };
  });

  function getMatchEndingText(matchClosureDto: MatchClosureDto) {
    if (!matchClosureDto.winner) return "Draw";

    const isWinner = matchClosureDto.winner.playerId === playerInfo.playerId;
    if (matchClosureDto.endingReason === EndingReason.PLAYER_LEFT && isWinner)
      return "Your opponent left";
    else if (matchClosureDto.endingReason === EndingReason.NEVER_JOINED && isWinner)
      return "Your opponent did not join the match";
    else if (isWinner) return "You won!";
    else return "You lost";
  }

  return (
    <PageContainer>
      {canRenderContent ? (
        <>
          {turnInfo && <GameTopInfo turnInfoDto={turnInfo} />}
          <div className="main-inner-container">
            <GameGrid />
          </div>
        </>
      ) : (
        <div>
          <LoadingSpinner className="initial-loading" />
          <h3>{waitingText}</h3>
        </div>
      )}
      {modalVisible && (
        <SingleButtonModal buttonText="OK" onClose={modalExit} icon={modalIcon}>
          <h3 className="no-margin">{modalText}</h3>
        </SingleButtonModal>
      )}
    </PageContainer>
  );
}

interface PageContainerProps {
  children: ReactNode;
}

function PageContainer(props: PageContainerProps) {
  const { children } = props;

  return <div className="page-container">{children}</div>;
}
