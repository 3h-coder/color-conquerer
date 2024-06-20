import { ReactNode, useEffect, useState } from "react";
import { undefinedMatch, useMatchInfo } from "../../contexts/MatchContext";
import { undefinedPlayer, usePlayerInfo } from "../../contexts/PlayerContext";
import GameBoard from "./components/GameBoard";
import GameMenu from "./components/GameMenu";

export default function PlayContent() {
    const { matchInfo, loading: matchInfoLoading } = useMatchInfo();
    const { playerInfo, loading: playerInfoLoading } = usePlayerInfo();
    const [canRenderContent, setCanRenderContent] = useState(false);

    useEffect(() => {
        if (matchInfoLoading || playerInfoLoading)
            return;

        if (matchInfo === undefinedMatch || playerInfo === undefinedPlayer) {
            console.log("Undefined!!");
            // location.href = "/";
        } else {
            setCanRenderContent(true);
        }
    }, [matchInfoLoading, playerInfoLoading])

    return (
        canRenderContent &&
        <PageContainer>
            <GameMenu />
            <GameBoard />
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