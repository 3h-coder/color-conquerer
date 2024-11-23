/* eslint-disable react-refresh/only-export-components */
import {
    ReactNode,
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";
import { fetchMatchInfo } from "../api/game";
import { ParseErrorDto } from "../dto/ErrorDto";
import {
    PartialMatchInfoDto,
    undefinedMatch,
} from "../dto/PartialMatchInfoDto";
import { developmentErrorLog } from "../utils/loggingUtils";
import { useUser } from "./UserContext";

interface MatchContextObject {
    matchInfo: PartialMatchInfoDto;
    loading: boolean;
}

const MatchContext = createContext<MatchContextObject>({
    matchInfo: undefinedMatch,
    loading: false,
});

interface MatchContextProviderProps {
    children?: ReactNode;
}

export default function MatchContextProvider(props: MatchContextProviderProps) {
    const { children } = props;
    const { user } = useUser();
    const [matchInfo, setMatchInfo] =
        useState<PartialMatchInfoDto>(undefinedMatch);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user.isAuthenticating) return;
        getMatchInfo();
    }, [user.isAuthenticating]);

    async function getMatchInfo() {
        try {
            const fetchedMatchInfo = await fetchMatchInfo();
            setMatchInfo(fetchedMatchInfo);
        } catch (error: unknown) {
            developmentErrorLog(
                "Could not fetch the match info",
                ParseErrorDto(error)
            );
            setMatchInfo(undefinedMatch);
        } finally {
            setLoading(false);
        }
    }

    return (
        <MatchContext.Provider value={{ matchInfo, loading }}>
            {children}
        </MatchContext.Provider>
    );
}

export function useMatchInfo() {
    return useContext(MatchContext);
}
