import { createContext, useContext, useState } from "react";
import { PlayerResourceBundleDto, undefinedPlayerResourceBundleDto } from "../dto/player/PlayerInfoBundleDto";

interface PlayerResourcesContextObject {
    playerResourceBundle: PlayerResourceBundleDto;
    setPlayerResourceBundle: (p: PlayerResourceBundleDto) => void;
}

const PlayerResourcesContext = createContext<PlayerResourcesContextObject>({
    playerResourceBundle: undefinedPlayerResourceBundleDto,
    setPlayerResourceBundle: () => { },
});

interface PlayersResourcesContextProviderProps {
    children: React.ReactNode;
}

export default function PlayersResourcesContextProvider(
    props: PlayersResourcesContextProviderProps
) {
    const { children } = props;
    const [playerResourceBundle, setPlayerResourceBundle] = useState(
        undefinedPlayerResourceBundleDto
    );

    return (
        <PlayerResourcesContext.Provider
            value={{
                playerResourceBundle,
                setPlayerResourceBundle,
            }}
        >
            {children}
        </PlayerResourcesContext.Provider>
    );
}

// eslint-disable-next-line react-refresh/only-export-components
export function usePlayersGameInfo() {
    return useContext(PlayerResourcesContext);
}
