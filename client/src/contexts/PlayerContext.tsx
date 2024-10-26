/* eslint-disable react-refresh/only-export-components */
import { ReactNode, createContext, useContext, useEffect, useState } from "react";
import { fetchPlayerInfo } from "../api/game";
import { ParseErrorDto } from "../dto/ErrorDto";
import { PartialPlayerInfoDto } from "../dto/PartialPlayerInfoDto";
import { developmentErrorLog } from "../utils/loggingUtils";
import { useUser } from "./UserContext";

interface PlayerContextObject {
    playerInfo: PartialPlayerInfoDto;
    setPlayerInfo: (p: PartialPlayerInfoDto) => void;
    loading: boolean;
}

export const undefinedPlayer: PartialPlayerInfoDto = {
    playerId: "undefined",
    isPlayer1: false
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const PlayerContext = createContext<PlayerContextObject>({ playerInfo: undefinedPlayer, setPlayerInfo: (_playerInfo: PartialPlayerInfoDto) => { }, loading: false });

interface PlayerontextProviderProps {
    children?: ReactNode;
}

export default function PlayerContextProvider(props: PlayerontextProviderProps) {
    const { children } = props;
    const { user } = useUser();
    const [playerInfo, setPlayerInfo] = useState(undefinedPlayer);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user.isAuthenticating)
            return;
        getPlayerInfo();
    }, [user.isAuthenticating]);

    async function getPlayerInfo() {
        try {
            const fetchedPlayerInfo = await fetchPlayerInfo();
            setPlayerInfo(fetchedPlayerInfo);
        } catch (error: unknown) {
            developmentErrorLog("Could resolve the player info", ParseErrorDto(error));
            setPlayerInfo(undefinedPlayer);
        } finally {
            setLoading(false);
        }
    }

    return (
        <PlayerContext.Provider value={{ playerInfo, setPlayerInfo, loading }}>
            {children}
        </PlayerContext.Provider>
    )
}

export function usePlayerInfo() {
    return useContext(PlayerContext);
}