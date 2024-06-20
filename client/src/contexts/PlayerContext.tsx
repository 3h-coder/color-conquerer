/* eslint-disable react-refresh/only-export-components */
import { ReactNode, createContext, useContext, useEffect, useState } from "react";
import { fetchPlayerInfo } from "../api/game";
import { ParseErrorDto } from "../dto/ErrorDto";
import { PlayerInfoDto } from "../dto/PlayerInfoDto";
import { developmentErrorLog } from "../utils/loggingUtils";

interface PlayerContextObject {
    playerInfo: PlayerInfoDto;
    setPlayerInfo: (p: PlayerInfoDto) => void;
    loading: Boolean
}

export const undefinedPlayer: PlayerInfoDto = {
    user: null,
    playerId: "",
    isPlayer1: false
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const PlayerContext = createContext<PlayerContextObject>({ playerInfo: undefinedPlayer, setPlayerInfo: (_playerInfo: PlayerInfoDto) => { }, loading: false });

interface PlayerontextProviderProps {
    children?: ReactNode;
}

export default function PlayerContextProvider(props: PlayerontextProviderProps) {
    const { children } = props;
    const [playerInfo, setPlayerInfo] = useState(undefinedPlayer);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getPlayerInfo();
    }, []);

    async function getPlayerInfo() {
        try {
            const fetchedPlayerInfo = await fetchPlayerInfo();

            const playerInfo: PlayerInfoDto = {
                user: fetchedPlayerInfo.user,
                playerId: fetchedPlayerInfo.playerId,
                isPlayer1: fetchedPlayerInfo.isPlayer1
            };

            setPlayerInfo(playerInfo);
        } catch (error: unknown) {
            developmentErrorLog("Could not fetch the player info", ParseErrorDto(error));
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