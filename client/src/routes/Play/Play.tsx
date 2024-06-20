import { ReactNode, useEffect, useState } from "react";
import MatchContextProvider, { undefinedMatch, useMatchInfo } from "../../contexts/MatchContext";
import PlayerContextProvider, { undefinedPlayer, usePlayerInfo } from "../../contexts/PlayerContext";
import '../../style/css/Play.css';
import GameBoard from "./components/GameBoard";
import GameMenu from "./components/GameMenu";

export default function Play() {
    const { matchInfo, loading: matchInfoLoading } = useMatchInfo();
    const { playerInfo, loading: playerInfoLoading } = usePlayerInfo();
    const [canRenderContent, setCanRenderContent] = useState(false);

    useEffect(() => {
        if (matchInfoLoading || playerInfoLoading) {
            return;
        }

        if (matchInfo === undefinedMatch || playerInfo === undefinedPlayer) {
            location.href = "/";
        } else {
            setCanRenderContent(true);
        }
    }, [matchInfoLoading, playerInfoLoading]);

    return (
        <MatchContextProvider>
            <PlayerContextProvider>
                {
                    canRenderContent &&
                    <PageContainer>
                        <GameMenu />
                        <GameBoard />
                    </PageContainer>
                }
            </PlayerContextProvider>
        </MatchContextProvider>
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