import { ReactNode, useEffect, useState } from "react";
import SingleButtonModal from "../../components/modals/SingleButtonModal";
import { undefinedMatch, useMatchInfo } from "../../contexts/MatchContext";
import { undefinedPlayer, usePlayerInfo } from "../../contexts/PlayerContext";
import { Events } from "../../enums/events";
import { socket } from "../../env";
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
        }
    }, [matchInfo, matchInfoLoading, playerInfo, playerInfoLoading]);

    useEffect(() => {
        function onOpponentLeft() {
            setModalVisible(true);
            setModalText("Your opponnent left");
        }

        socket.on(Events.SERVER_MATCH_OPPONENT_LEFT, onOpponentLeft);

        return () => {
            socket.off(Events.SERVER_MATCH_OPPONENT_LEFT, onOpponentLeft);
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