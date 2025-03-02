/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState } from "react";
import { PlayerMode } from "../enums/playerMode";

interface PlayerModeContextObject {
    playerMode: PlayerMode;
    setPlayerMode: (mode: PlayerMode) => void;
}

export const PlayerModeContext = createContext<PlayerModeContextObject>({
    playerMode: PlayerMode.IDLE,
    setPlayerMode: () => { },
});

interface PlayerModeContextProviderProps {
    children: React.ReactNode;
}

export default function PlayerModeContextProvider(
    props: PlayerModeContextProviderProps
) {
    const { children } = props;
    const [playerMode, setPlayerMode] = useState(PlayerMode.IDLE);

    return (
        <PlayerModeContext.Provider value={{ playerMode, setPlayerMode }}>
            {children}
        </PlayerModeContext.Provider>
    );
}

export function usePlayerMode() {
    return useContext(PlayerModeContext);
}