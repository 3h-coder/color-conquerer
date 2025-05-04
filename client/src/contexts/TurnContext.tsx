/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState } from "react";
import { TurnContextDto, undefinedTurnContext } from "../dto/gameState/TurnContextDto";

interface TurnContextObject {
    turnContext: TurnContextDto;
    setTurnContext: (t: TurnContextDto) => void;
    canInteract: boolean;
    setCanInteract: (c: boolean) => void;
}


const TurnContext = createContext<TurnContextObject>({
    turnContext: undefinedTurnContext,
    setTurnContext: (_turnInfo: TurnContextDto) => { },
    canInteract: false,
    setCanInteract: (_canInteract: boolean) => { },
});

interface TurnContextProviderProps {
    children: React.ReactNode;
}

export default function TurnContextProvider(
    props: TurnContextProviderProps
) {
    const { children } = props;
    const [turnContext, setTurnContext] = useState(undefinedTurnContext);
    const [canInteract, setCanInteract] = useState(false);

    return (
        <TurnContext.Provider
            value={{ turnContext, setTurnContext, canInteract, setCanInteract }}
        >
            {children}
        </TurnContext.Provider>
    );
}

export function useTurnContext() {
    return useContext(TurnContext);
}
