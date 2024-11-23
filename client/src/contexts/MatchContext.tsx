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
    failedToResolve: boolean;
}

const MatchContext = createContext<MatchContextObject>({
    matchInfo: undefinedMatch,
    loading: false,
    failedToResolve: false
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
    const [failedToResolve, setFailedToResolve] = useState(false);

    useEffect(() => {
        if (user.isAuthenticating) return;
        getMatchInfo();
    }, [user.isAuthenticating]);

    async function getMatchInfo() {
        try {
            const fetchedMatchInfo = await fetchMatchInfo();
            setMatchInfo(fetchedMatchInfo);
            setFailedToResolve(false);
        } catch (error: unknown) {
            developmentErrorLog(
                "Could not fetch the match info",
                ParseErrorDto(error)
            );
            setMatchInfo(undefinedMatch);
            setFailedToResolve(true);
        } finally {
            setLoading(false);
        }
    }

    return (
        <MatchContext.Provider value={{ matchInfo, loading, failedToResolve: failedToResolve }}>
            {children}
        </MatchContext.Provider>
    );
}

export function useMatchInfo() {
    return useContext(MatchContext);
}
