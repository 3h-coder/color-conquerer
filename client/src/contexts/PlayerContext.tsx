/* eslint-disable react-refresh/only-export-components */
import {
    ReactNode,
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";
import { fetchPlayerInfo } from "../api/game";
import { ParseErrorDto } from "../dto/ErrorDto";
import {
    PlayerDto,
    undefinedPlayer
} from "../dto/PlayerDto";
import { developmentErrorLog } from "../utils/loggingUtils";
import { useUser } from "./UserContext";

interface PlayerContextObject extends PlayerDto {
    loading: boolean;
    failedToResolve: boolean;
}

const PlayerContext = createContext<PlayerContextObject>({
    ...undefinedPlayer,
    loading: false,
    failedToResolve: false
});

interface PlayerContextProviderProps {
    children?: ReactNode;
}

export default function PlayerContextProvider(
    props: PlayerContextProviderProps
) {
    const { children } = props;
    const { user } = useUser();
    const [failedToResolve, setFailedToResolve] = useState(false);
    const [playerInfo, setPlayerInfo] = useState(undefinedPlayer);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user.isAuthenticating) return;
        getPlayerInfo();
    }, [user.isAuthenticating]);

    async function getPlayerInfo() {
        try {
            const fetchedPlayerInfo = await fetchPlayerInfo();
            setPlayerInfo(fetchedPlayerInfo);
            setFailedToResolve(false);
        } catch (error: unknown) {
            developmentErrorLog(
                "Could resolve the player info",
                ParseErrorDto(error)
            );
            setPlayerInfo(undefinedPlayer);
            setFailedToResolve(true);
        } finally {
            setLoading(false);
        }
    }

    return (
        <PlayerContext.Provider value={{ ...playerInfo, loading, failedToResolve: failedToResolve }}>
            {children}
        </PlayerContext.Provider>
    );
}

export function usePlayerInfo() {
    return useContext(PlayerContext);
}
