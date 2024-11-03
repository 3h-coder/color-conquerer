/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState } from "react";
import { TurnInfoDto } from "../dto/TurnInfoDto";

interface TurnContextObject {
    turnInfo: TurnInfoDto;
    setTurnInfo: (t: TurnInfoDto) => void;
}

export const undefinedTurnInfo: TurnInfoDto = {
    currentPlayerId: "", isPlayer1Turn: false, durationInS: 0
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const TurnContext = createContext<TurnContextObject>({ turnInfo: undefinedTurnInfo, setTurnInfo: (_turnInfo: TurnInfoDto) => { } });

interface TurnInfoContextProviderProps {
    children: React.ReactNode;
}

export default function TurnInfoContextProvider(props: TurnInfoContextProviderProps) {
    const { children } = props;
    const [turnInfo, setTurnInfo] = useState(undefinedTurnInfo);

    return (
        <TurnContext.Provider value={{ turnInfo, setTurnInfo }}>
            {children}
        </TurnContext.Provider>
    )
}

export function useTurnInfo() {
    return useContext(TurnContext);
}