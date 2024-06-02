import MatchContextProvider from "../../contexts/MatchContext";
import GameBoard from "./components/GameBoard";
import '../../style/css/Play.css';
import GameMenu from "./components/GameMenu";
import { ReactNode } from "react";

export default function Play() {

    return (
        <MatchContextProvider>
            <PageContainer>
                <GameMenu />
                <GameBoard />
            </PageContainer>
        </MatchContextProvider>
    )
}

interface PageContainerProps {
    children : ReactNode;
}

function PageContainer(props: PageContainerProps) {
    const {children} = props;

    return (
        <div className="page-container">
            {children}
        </div>
    );
}