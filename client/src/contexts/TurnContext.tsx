/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState } from "react";
import { TurnContextDto, undefinedTurnInfo } from "../dto/TurnContextDto";

interface TurnContextObject {
    turnInfo: TurnContextDto;
    setTurnInfo: (t: TurnContextDto) => void;
    canInteract: boolean;
    setCanInteract: (c: boolean) => void;
}


const TurnContext = createContext<TurnContextObject>({
    turnInfo: undefinedTurnInfo,
    setTurnInfo: (_turnInfo: TurnContextDto) => { },
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
