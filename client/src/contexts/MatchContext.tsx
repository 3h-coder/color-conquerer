import { ReactNode, createContext, useContext, useState } from "react";
import { MatchInfoDto } from "../dto/MatchInfoDto";

const unstartedMatch: MatchInfoDto = {
    boardArray: [],
    player1: undefined,
    player2: undefined,
    currentTurn: 0,
    started: false
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const MatchContext = createContext({ matchInfo: unstartedMatch, setMatchInfo: (_matchInfo: MatchInfoDto) => { } });

interface MatchContextProviderProps {
    children?: ReactNode;
}

export default function MatchContextProvider(props: MatchContextProviderProps) {
    const { children } = props;
    const [matchInfo, setMatchInfo] = useState<MatchInfoDto>(unstartedMatch);

    return (
        <MatchContext.Provider value={{ matchInfo, setMatchInfo }}>
            {children}
        </MatchContext.Provider>
    );
}

export function useMatch() {
    return useContext(MatchContext);
};