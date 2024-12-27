import { createContext, useContext, useState } from "react";
import {
    PlayerGameInfoBundleDto,
    undefinedPlayerInfoBundleDto,
} from "../dto/PlayerInfoBundleDto";

interface PlayersGameInfoContextObject {
    playerGameInfoBundle: PlayerGameInfoBundleDto;
    setPlayerGameInfoBundle: (p: PlayerGameInfoBundleDto) => void;
}

const PlayerGameInfoContext = createContext<PlayersGameInfoContextObject>({
    playerGameInfoBundle: undefinedPlayerInfoBundleDto,
    setPlayerGameInfoBundle: (_p: PlayerGameInfoBundleDto) => { },
});

interface PlayersGameInfoContextProviderProps {
    children: React.ReactNode;
}

export default function PlayersGameInfoContextProvider(
    props: PlayersGameInfoContextProviderProps
) {
    const { children } = props;
    const [playerGameInfoBundle, setPlayerGameInfoBundle] = useState(
        undefinedPlayerInfoBundleDto
    );

    return (
        <PlayerGameInfoContext.Provider
            value={{
                playerGameInfoBundle,
                setPlayerGameInfoBundle,
            }}
        >
            {children}
        </PlayerGameInfoContext.Provider>
    );
}

export function usePlayersGameInfo() {
    return useContext(PlayerGameInfoContext);
}
