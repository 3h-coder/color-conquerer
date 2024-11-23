/* eslint-disable react-refresh/only-export-components */
import {
    ReactNode,
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";
import { fetchPlayerInfoBundle } from "../api/game";
import { ParseErrorDto } from "../dto/ErrorDto";
import {
    undefinedPlayerGameInfo
} from "../dto/PartialPlayerGameInfoDto";
import {
    undefinedPlayer
} from "../dto/PartialPlayerInfoDto";
import { PlayerInfoBundleDto } from "../dto/PlayerInfoBundleDto";
import { developmentErrorLog } from "../utils/loggingUtils";
import { useUser } from "./UserContext";

interface PlayerContextObject extends PlayerInfoBundleDto {
    loading: boolean;
    resolved: boolean;
}

const PlayerContext = createContext<PlayerContextObject>({
    playerInfo: undefinedPlayer,
    playerGameInfo: undefinedPlayerGameInfo,
    opponentGameInfo: undefinedPlayerGameInfo,
    loading: false,
    resolved: false
});

interface PlayerContextProviderProps {
    children?: ReactNode;
}

export default function PlayerContextProvider(
    props: PlayerContextProviderProps
) {
    const { children } = props;
    const { user } = useUser();
    const [resolved, setPlayerContextResolved] = useState(false);
    const [playerInfo, setPlayerInfo] = useState(undefinedPlayer);
    const [playerGameInfo, setPlayerGameInfo] = useState(undefinedPlayerGameInfo);
    const [opponentGameInfo, setOpponentGameInfo] = useState(undefinedPlayerGameInfo);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user.isAuthenticating) return;
        getPlayerInfo();
    }, [user.isAuthenticating]);

    async function getPlayerInfo() {
        try {
            const fetchedPlayerInfoBundle = await fetchPlayerInfoBundle();
            setPlayerInfo(fetchedPlayerInfoBundle.playerInfo);
            setPlayerGameInfo(fetchedPlayerInfoBundle.playerGameInfo);
            setOpponentGameInfo(fetchedPlayerInfoBundle.opponentGameInfo);
            setPlayerContextResolved(true);
        } catch (error: unknown) {
            developmentErrorLog(
                "Could resolve the player info",
                ParseErrorDto(error)
            );
            setPlayerInfo(undefinedPlayer);
            setPlayerContextResolved(false);
        } finally {
            setLoading(false);
        }
    }

    return (
        <PlayerContext.Provider value={{ playerInfo, playerGameInfo, opponentGameInfo, loading, resolved }}>
            {children}
        </PlayerContext.Provider>
    );
}

export function usePlayerInfo() {
    return useContext(PlayerContext);
}
