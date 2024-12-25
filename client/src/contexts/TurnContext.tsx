/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState } from "react";
import { TurnInfoDto, undefinedTurnInfo } from "../dto/TurnInfoDto";

interface TurnContextObject {
    turnInfo: TurnInfoDto;
    setTurnInfo: (t: TurnInfoDto) => void;
    canInteract: boolean;
    setCanInteract: (c: boolean) => void;
}


const TurnContext = createContext<TurnContextObject>({
    turnInfo: undefinedTurnInfo,
    setTurnInfo: (_turnInfo: TurnInfoDto) => { },
    canInteract: false,
    setCanInteract: (_canInteract: boolean) => { },
});

interface TurnInfoContextProviderProps {
    children: React.ReactNode;
}

export default function TurnInfoContextProvider(
    props: TurnInfoContextProviderProps
) {
    const { children } = props;
    const [turnInfo, setTurnInfo] = useState(undefinedTurnInfo);
    const [canInteract, setCanInteract] = useState(false);

    return (
        <TurnContext.Provider
            value={{ turnInfo, setTurnInfo, canInteract, setCanInteract }}
        >
            {children}
        </TurnContext.Provider>
    );
}

export function useTurnInfo() {
    return useContext(TurnContext);
}
