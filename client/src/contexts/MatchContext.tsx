import { ReactNode, createContext, useContext, useEffect, useState } from "react";
import { fetchMatchInfo } from "../api/game";
import { ParseErrorDto } from "../dto/ErrorDto";
import { MatchInfoDto } from "../dto/MatchInfoDto";
import { developmentErrorLog } from "../utils/loggingUtils";

interface MatchContextObject {
    matchInfo: MatchInfoDto;
    setMatchInfo: (m: MatchInfoDto) => void;
    loading: Boolean
}

export const undefinedMatch: MatchInfoDto = {
    id: "",
    roomId: "",
    boardArray: [],
    player1: undefined,
    player2: undefined,
    currentTurn: 0,
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const MatchContext = createContext<MatchContextObject>({ matchInfo: undefinedMatch, setMatchInfo: (_matchInfo: MatchInfoDto) => { }, loading: false });

interface MatchContextProviderProps {
    children?: ReactNode;
}

export default function MatchContextProvider(props: MatchContextProviderProps) {
    const { children } = props;
    const [matchInfo, setMatchInfo] = useState<MatchInfoDto>(undefinedMatch);
    const [loading, setLoading] = useState(true);

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
        } finally {
            setLoading(false);
        }
    }

    return (
        <MatchContext.Provider value={{ matchInfo, setMatchInfo, loading }}>
            {children}
        </MatchContext.Provider>
    );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useMatchInfo() {
    return useContext(MatchContext);
}