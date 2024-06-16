import { ReactNode, createContext, useContext, useEffect, useState } from "react";
import { fetchMatchInfo } from "../api/game";
import { ParseErrorDto } from "../dto/ErrorDto";
import { MatchInfoDto } from "../dto/MatchInfoDto";
import { developmentErrorLog } from "../utils/loggingUtils";

const undefinedMatch: MatchInfoDto = {
    id: "",
    roomId: "",
    boardArray: [],
    player1: undefined,
    player2: undefined,
    currentTurn: 0,
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const MatchContext = createContext({ matchInfo: undefinedMatch, setMatchInfo: (_matchInfo: MatchInfoDto) => { } });

interface MatchContextProviderProps {
    children?: ReactNode;
}

export default function MatchContextProvider(props: MatchContextProviderProps) {
    const { children } = props;
    const [matchInfo, setMatchInfo] = useState<MatchInfoDto>(undefinedMatch);

    useEffect(() => {
        getMatchInfo();
    }, []);

    async function getMatchInfo() {
        try {
            const fetchedMatchInfo = await fetchMatchInfo();

            const matchInfo: MatchInfoDto = {
                id: fetchedMatchInfo.id,
                roomId: fetchedMatchInfo.roomId,
                boardArray: fetchedMatchInfo.boardArray,
                player1: fetchedMatchInfo.player1,
                player2: fetchedMatchInfo.player2,
                currentTurn: fetchedMatchInfo.currentTurn
            };

            setMatchInfo(matchInfo);
        } catch (error: unknown) {
            developmentErrorLog("Could not fetch the match info", ParseErrorDto(error));
            setMatchInfo(undefinedMatch);
        }
    }

    return (
        <MatchContext.Provider value={{ matchInfo, setMatchInfo }}>
            {children}
        </MatchContext.Provider>
    );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useMatch() {
    return useContext(MatchContext);
}