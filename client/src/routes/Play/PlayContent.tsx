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
  const [canRenderContent, setCanRenderContent] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalText, setModalText] = useState("");
  const [modalExit, setModalExit] = useState<() => unknown>(() => { return () => setModalVisible(false) });

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
      setModalText(getMatchEndingText(matchClosureDto));
      setModalVisible(true);

      setModalExit(() => {
        return () => { location.href = "/" };
      });
      socket.emit(Events.CLIENT_CLEAR_SESSION);
    }

    function onError(errorDto: ErrorDto) {
      if (!errorDto.displayToUser)
        return;

      setModalVisible(true);
      setModalText(errorDto.error);
      setModalExit(() => { return () => setModalVisible(false) });

      // An error here should never cause the match to end,
      // hence why we're not handling the socketConnectionKiller field.
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

  function onMatchContextError(error: ErrorDto) {
    setModalText(error.error);
    setModalVisible(true);
    setModalExit(() => {
      return () => { location.href = "/" };
    });
  }

  function getMatchEndingText(matchClosureDto: MatchClosureDto) {
    if (!matchClosureDto.winner)
      return "Draw";

    const isWinner = matchClosureDto.winner.playerId === playerInfo.playerId;
    if (
      (matchClosureDto.endingReason === EndingReason.PLAYER_LEFT && isWinner) ||
      (matchClosureDto.endingReason === EndingReason.NEVER_JOINED && isWinner))
      return "Your opponent left";

    else if (isWinner)
      return "You won!";

    else
      return "You lost";
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
