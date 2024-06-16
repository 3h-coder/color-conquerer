import { ReactNode, useEffect } from "react";
import MatchContextProvider from "../../contexts/MatchContext";
import PlayerContextProvider from "../../contexts/PlayerContext";
import { Events } from "../../enums/events";
import { socket } from "../../env";
import '../../style/css/Play.css';
import GameBoard from "./components/GameBoard";
import GameMenu from "./components/GameMenu";

export default function Play() {

    useEffect(() => {
        socket.emit(Events.CLIENT_MATCH_INFO);
    }, []);

    return (
        <MatchContextProvider>
            <PlayerContextProvider>
                <PageContainer>
                    <GameMenu />
                    <GameBoard />
                </PageContainer>
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