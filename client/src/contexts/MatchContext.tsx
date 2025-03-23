/* eslint-disable react-refresh/only-export-components */
import {
    ReactNode,
    createContext,
    useCallback,
    useContext,
    useEffect,
    useRef,
    useState,
} from "react";
import { fetchMatchInfo } from "../api/game";
import {
    MatchContextDto,
    undefinedMatch,
} from "../dto/match/MatchContextDto";
import { ParseErrorDto } from "../dto/misc/ErrorDto";
import { developmentErrorLog } from "../utils/loggingUtils";
import { useUser } from "./UserContext";
import { socket } from "../env";

type EmitCallback = () => void;

interface MatchContextObject {
    matchInfo: MatchContextDto;
    loading: boolean;
    failedToResolve: boolean;
    emit: (event: string, ...args: unknown[]) => void;
    onEmit: (callback: EmitCallback) => () => void; // Returns cleanup function
}

const MatchContext = createContext<MatchContextObject>({
    matchInfo: undefinedMatch,
    loading: false,
    failedToResolve: false,
    emit: () => { },
    onEmit: () => () => { },
});

interface MatchContextProviderProps {
    children?: ReactNode;
}

export default function MatchContextProvider(props: MatchContextProviderProps) {
    const { children } = props;
    const { user } = useUser();
    const [matchInfo, setMatchInfo] =
        useState<MatchContextDto>(undefinedMatch);
    const [loading, setLoading] = useState(true);
    const [failedToResolve, setFailedToResolve] = useState(false);

    // Store callbacks in a ref to prevent unnecessary re-renders
    const emitCallbacks = useRef<Set<EmitCallback>>(new Set());

    const onEmit = useCallback((callback: EmitCallback) => {
        emitCallbacks.current.add(callback);

        // Return cleanup function
        return () => {
            emitCallbacks.current.delete(callback);
        };
    }, []);

    const emit = useCallback((event: string, ...args: unknown[]) => {
        socket.emit(event, ...args);

        emitCallbacks.current.forEach(callback => callback());
    }, []);

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
        <MatchContext.Provider value={{ matchInfo, loading, failedToResolve, emit, onEmit }}>
            {children}
        </MatchContext.Provider>
    );
}

export function useMatchContext() {
    return useContext(MatchContext);
}
