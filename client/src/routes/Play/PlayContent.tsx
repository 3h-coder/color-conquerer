import { ReactNode, useEffect, useState } from "react";
import { fetchGameContextInfoFromLocalStorage } from "../../api/game";
import SingleButtonModal from "../../components/modals/SingleButtonModal";
import { undefinedMatch, useMatchInfo } from "../../contexts/MatchContext";
import { undefinedPlayer, usePlayerInfo } from "../../contexts/PlayerContext";
import { ErrorDto, ParseErrorDto } from "../../dto/ErrorDto";
import { GameContextDto } from "../../dto/GameContextDto";
import { EndingReason, MatchClosureDto } from "../../dto/MatchClosureDto";
import { Events } from "../../enums/events";
import { socket } from "../../env";
import { developmentErrorLog, developmentLog } from "../../utils/loggingUtils";
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
  const [canRenderContent, setCanRenderContent] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalText, setModalText] = useState("");
  const [modalExit, setModalExit] = useState<() => unknown>(() => { setModalVisible(false) });

  useEffect(() => {
    if (matchInfoLoading || playerInfoLoading) return;

    if (matchInfo === undefinedMatch || playerInfo === undefinedPlayer) {
      fetchGameContextInfoFromLocalStorage()
        .then((gameContext: GameContextDto) => {
          setMatchInfo(gameContext.matchInfo);
          setPlayerInfo(gameContext.playerInfo);
        })
        .catch((error: unknown) => {
          onError(ParseErrorDto(error));
        });
    } else {
      setCanRenderContent(true);

      if (!socket.connected) socket.connect();

      socket.emit(Events.CLIENT_READY);
    }
  }, [matchInfo, matchInfoLoading, playerInfo, playerInfoLoading, setMatchInfo, setPlayerInfo]);

  useEffect(() => {
    function onMatchStarted() {
      developmentLog("Match started!");
    }

    function onTurnSwap() {
      developmentLog("Turn swap!");
    }

    function onMatchEnded(matchClosureDto: MatchClosureDto) {
      developmentLog("Received match ending ", matchClosureDto);
      const isWinner = matchClosureDto.winner.playerId === playerInfo.playerId;

      setModalVisible(true);
      if (
        matchClosureDto.endingReason === EndingReason.PLAYER_LEFT &&
        isWinner
      ) {
        setModalText("Your opponent left");
      } else if (isWinner) {
        setModalText("You won!");
      } else {
        setModalText("You lost");
      }
    }

    socket.on(Events.SERVER_START_MATCH, onMatchStarted);
    socket.on(Events.SERVER_TURN_SWAP, onTurnSwap);
    socket.on(Events.SERVER_MATCH_END, onMatchEnded);
    socket.on(Events.SERVER_ERROR, onError);

    return () => {
      socket.off(Events.SERVER_START_MATCH, onMatchStarted);
      socket.off(Events.SERVER_TURN_SWAP, onTurnSwap);
      socket.off(Events.SERVER_MATCH_END, onMatchEnded);
      socket.off(Events.SERVER_ERROR, onError);
    };
  });

  function onError(errorDto: ErrorDto) {
    developmentErrorLog("An error occured", errorDto);

    if (errorDto.displayToUser) {
      setModalVisible(true);
      setModalText(errorDto.error);
    }

    if (errorDto.socketConnectionKiller) {
      socket.emit(Events.CLIENT_MATCH_FAILURE);
      socket.disconnect();
      setModalExit(() => { });
    }
  }

  return (
    <PageContainer>
      {canRenderContent && (
        <>
          <GameMenu />
          <GameGrid />
          <GameInfo />
        </>
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
