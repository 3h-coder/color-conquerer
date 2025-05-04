import { createContext, useContext, useState } from "react";
import { GameContextDto, undefinedGameContextDto } from "../dto/gameState/GameContextDto";

interface GameContextObject {
    gameContext: GameContextDto;
    setGameContext: React.Dispatch<React.SetStateAction<GameContextDto>>;
}

const GameContext = createContext<GameContextObject>({
    gameContext: undefinedGameContextDto,
    setGameContext: () => { },
});

interface GameContextProviderProps {
    children: React.ReactNode;
}

export default function GameContextProvider(
    props: GameContextProviderProps
) {
    const { children } = props;
    const [gameContext, setGameContext] = useState<GameContextDto>(undefinedGameContextDto);

    return (
        <GameContext.Provider value={{ gameContext, setGameContext }}>
            {children}
        </GameContext.Provider>
    );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useGameContext() {
    return useContext(GameContext);
}
