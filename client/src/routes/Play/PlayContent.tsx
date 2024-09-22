import { ReactNode, useEffect, useState } from "react";
import SingleButtonModal from "../../components/modals/SingleButtonModal";
import { undefinedMatch, useMatchInfo } from "../../contexts/MatchContext";
import { undefinedPlayer, usePlayerInfo } from "../../contexts/PlayerContext";
import { EndingReason, MatchClosureDto } from "../../dto/MatchClosureDto";
import { Events } from "../../enums/events";
import { socket } from "../../env";
import { developmentLog } from "../../utils/loggingUtils";
import GameGrid from "./components/GameGrid";
import GameInfo from "./components/GameInfo";
import GameMenu from "./components/GameMenu";


export default function PlayContent() {
    const { matchInfo, loading: matchInfoLoading } = useMatchInfo();
    const { playerInfo, loading: playerInfoLoading } = usePlayerInfo();
    const [canRenderContent, setCanRenderContent] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [modalText, setModalText] = useState("");

    useEffect(() => {
        if (matchInfoLoading || playerInfoLoading)
            return;

        if (matchInfo === undefinedMatch || playerInfo === undefinedPlayer) {
            location.href = "/";
        } else {
            setCanRenderContent(true);

            if (!socket.connected)
                socket.connect();

            socket.emit(Events.CLIENT_READY);
        }
    }, [matchInfo, matchInfoLoading, playerInfo, playerInfoLoading]);

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
            if (matchClosureDto.endingReason === EndingReason.PLAYER_LEFT && isWinner) {
                setModalText("Your opponent left");
            }
            else if (isWinner) {
                setModalText("You won!");
            } else {
                setModalText("You lost");
            }
        }

        socket.on(Events.SERVER_START_MATCH, onMatchStarted);
        socket.on(Events.SERVER_TURN_SWAP, onTurnSwap);
        socket.on(Events.SERVER_MATCH_END, onMatchEnded);

        return () => {
            socket.off(Events.SERVER_START_MATCH, onMatchStarted);
            socket.off(Events.SERVER_TURN_SWAP, onTurnSwap);
            socket.off(Events.SERVER_MATCH_END, onMatchEnded);
        };
    });

    return (
        canRenderContent &&
        <PageContainer>
            <GameMenu />
            <GameGrid />
            <GameInfo />
            {modalVisible &&
                <SingleButtonModal buttonText="OK" onClose={() => location.href = "/"}>
                    <h3>{modalText}</h3>
                </SingleButtonModal>
            }
        </PageContainer>
    );
}

interface PageContainerProps {
    children: ReactNode;
}


function PageContainer(props: PageContainerProps) {
    const { children } = props;

    return (
        <div className="page-container">
            {children}
        </div>
    );
}