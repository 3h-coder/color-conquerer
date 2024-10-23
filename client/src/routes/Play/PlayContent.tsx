import { ReactNode, useEffect, useState } from "react";
import { fetchGameContextInfoFromLocalStorage } from "../../api/game";
import { clearMatchInfoFromSession } from "../../api/session";
import LoadingSpinner from "../../components/LoadingSpinner";
import SingleButtonModal from "../../components/modals/SingleButtonModal";
import { undefinedMatch, useMatchInfo } from "../../contexts/MatchContext";
import { undefinedPlayer, usePlayerInfo } from "../../contexts/PlayerContext";
import { ErrorDto, ParseErrorDto } from "../../dto/ErrorDto";
import { GameContextDto } from "../../dto/GameContextDto";
import { EndingReason, MatchClosureDto } from "../../dto/MatchClosureDto";
import { MessageDto } from "../../dto/MessageDto";
import { Events } from "../../enums/events";
import { socket } from "../../env";
import { developmentLog } from "../../utils/loggingUtils";
import GameGrid from "./components/GameGrid";
import GameInfo from "./components/GameInfo";
import GameMenu from "./components/GameMenu";

export default function PlayContent() {
  const { matchInfo, loading: matchInfoLoading, setMatchInfo } = useMatchInfo();
  const {
    playerInfo,
    loading: playerInfoLoading,
    setPlayerInfo,
  } = usePlayerInfo();
  const [waitingText, setWaitingText] = useState("Connecting to your match...");
  const [canRenderContent, setCanRenderContent] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalText, setModalText] = useState("");
  const [modalExit, setModalExit] = useState<() => unknown>(() => {
    return () => setModalVisible(false);
  });

  useEffect(() => {
    if (matchInfoLoading || playerInfoLoading) return;

    if (matchInfo === undefinedMatch || playerInfo === undefinedPlayer) {
      fetchGameContextInfoFromLocalStorage()
        .then((gameContext: GameContextDto) => {
          setMatchInfo(gameContext.matchInfo);
          setPlayerInfo(gameContext.playerInfo);
        })
        .catch((error: unknown) => {
          onMatchContextError(ParseErrorDto(error));
        });
    } else {
      if (!socket.connected) socket.connect();

      socket.emit(Events.CLIENT_READY);
    }
  }, [
    matchInfo,
    matchInfoLoading,
    playerInfo,
    playerInfoLoading,
    setMatchInfo,
    setPlayerInfo,
  ]);

  useEffect(() => {
    function onSetWaitingText(messageDto: MessageDto) {
      setWaitingText(messageDto.message);
    }

    function onMatchStarted() {
      setCanRenderContent(true);
    }

    function onTurnSwap() {
      developmentLog("Turn swap!");
    }

    function onMatchEnded(matchClosureDto: MatchClosureDto) {
      developmentLog("Received match ending ", matchClosureDto);
      setModalText(getMatchEndingText(matchClosureDto));
      setModalVisible(true);

      setModalExit(() => {
        return () => {
          location.href = "/";
        };
      });
      socket.emit(Events.CLIENT_CLEAR_SESSION);
    }

    function onError(errorDto: ErrorDto) {
      if (!errorDto.displayToUser) return;

      setModalVisible(true);
      setModalText(errorDto.error);

      // Only errors 
      if (errorDto.socketConnectionKiller) {
        socket.disconnect();
        setModalExit(() => {
          return () => setModalVisible(false);
        });
      }
    }

    socket.on(Events.SERVER_SET_WAITING_TEXT, onSetWaitingText);
    socket.on(Events.SERVER_MATCH_STARTED, onMatchStarted);
    socket.on(Events.SERVER_TURN_SWAP, onTurnSwap);
    socket.on(Events.SERVER_MATCH_END, onMatchEnded);
    socket.on(Events.SERVER_ERROR, onError);

    return () => {
      socket.off(Events.SERVER_SET_WAITING_TEXT, onSetWaitingText);
      socket.off(Events.SERVER_MATCH_STARTED, onMatchStarted);
      socket.off(Events.SERVER_TURN_SWAP, onTurnSwap);
      socket.off(Events.SERVER_MATCH_END, onMatchEnded);
      socket.off(Events.SERVER_ERROR, onError);
    };
  });

  function onMatchContextError(error: ErrorDto) {
    developmentLog("lalalala")
    clearMatchInfoFromSession();
    setModalText(error.error);
    setModalVisible(true);
    setModalExit(() => {
      return () => {
        location.href = "/";
      };
    });
  }

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
          <GameMenu />
          <GameGrid />
          <GameInfo />
        </>
      ) : (
        <div>
          <LoadingSpinner className="initial-loading" />
          <h3>{waitingText}</h3>
        </div>
      )}
      {modalVisible && (
        <SingleButtonModal buttonText="OK" onClose={modalExit}>
          <h3>{modalText}</h3>
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
