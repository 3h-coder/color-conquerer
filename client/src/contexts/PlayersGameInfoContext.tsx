/* eslint-disable @typescript-eslint/no-unused-vars */
import { createContext, useContext, useState } from "react";
import {
    PlayerResourceBundleDto,
    undefinedPlayerResourceBundleDto,
} from "../dto/PlayerInfoBundleDto";

interface PlayersGameInfoContextObject {
    playerResourceBundle: PlayerResourceBundleDto;
    setPlayerResourceBundle: (p: PlayerResourceBundleDto) => void;
}

const PlayerGameInfoContext = createContext<PlayersGameInfoContextObject>({
    playerResourceBundle: undefinedPlayerResourceBundleDto,
    setPlayerResourceBundle: (_p: PlayerResourceBundleDto) => { },
});

interface PlayersGameInfoContextProviderProps {
    children: React.ReactNode;
}

export default function PlayersGameInfoContextProvider(
    props: PlayersGameInfoContextProviderProps
) {
    const { children } = props;
    const [playerResourceBundle, setPlayerResourceBundle] = useState(
        undefinedPlayerResourceBundleDto
    );

    return (
        <PlayerGameInfoContext.Provider
            value={{
                playerResourceBundle,
                setPlayerResourceBundle,
            }}
        >
            {children}
        </PlayerGameInfoContext.Provider>
    );
}

// eslint-disable-next-line react-refresh/only-export-components
export function usePlayersGameInfo() {
    return useContext(PlayerGameInfoContext);
}
