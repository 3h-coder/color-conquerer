/* eslint-disable react-refresh/only-export-components */
import { ReactNode, createContext, useContext, useEffect, useState } from "react";
import { fetchMatchInfo } from "../api/game";
import { ParseErrorDto } from "../dto/ErrorDto";
import { PartialMatchInfoDto } from "../dto/PartialMatchInfoDto";
import { developmentErrorLog } from "../utils/loggingUtils";
import { useUser } from "./UserContext";

interface MatchContextObject {
    matchInfo: PartialMatchInfoDto;
    setMatchInfo: (m: PartialMatchInfoDto) => void;
    loading: boolean;
}

export const undefinedMatch: PartialMatchInfoDto = {
    id: "",
    roomId: "",
    boardArray: [],
    currentTurn: 0,
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const MatchContext = createContext<MatchContextObject>({ matchInfo: undefinedMatch, setMatchInfo: (_matchInfo: PartialMatchInfoDto) => { }, loading: false });

interface MatchContextProviderProps {
    children?: ReactNode;
}

export default function MatchContextProvider(props: MatchContextProviderProps) {
    const { children } = props;
    const { user } = useUser();
    const [matchInfo, setMatchInfo] = useState<PartialMatchInfoDto>(undefinedMatch);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user.isAuthenticating)
            return;
        getMatchInfo();
    }, [user.isAuthenticating]);

    async function getMatchInfo() {
        try {
            const fetchedMatchInfo = await fetchMatchInfo();

            const matchInfo: PartialMatchInfoDto = {
                id: fetchedMatchInfo.id,
                roomId: fetchedMatchInfo.roomId,
                boardArray: fetchedMatchInfo.boardArray,
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


export function useMatchInfo() {
    return useContext(MatchContext);
}