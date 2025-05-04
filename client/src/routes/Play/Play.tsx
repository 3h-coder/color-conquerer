import AnimationContextProvider from "../../contexts/AnimationContext";
import GameContextProvider from "../../contexts/GameContext";
import MatchContextProvider from "../../contexts/MatchContext";
import PlayerContextProvider from "../../contexts/PlayerContext";
import PlayerModeContextProvider from "../../contexts/PlayerModeContext";
import TurnContextProvider from "../../contexts/TurnContext";
import './Play.css';
import PlayContent from "./PlayContent";

export default function Play() {
    return (
        <ContextProviders>
            <PlayContent />
        </ContextProviders>
    );
}

interface ContextProvidersProps {
    children: React.ReactNode;
}


function ContextProviders(props: ContextProvidersProps) {
    const { children } = props;

    return (
        <AnimationContextProvider>
            <MatchContextProvider>
                <PlayerContextProvider>
                    <TurnContextProvider>
                        <GameContextProvider>
                            <PlayerModeContextProvider>
                                {children}
                            </PlayerModeContextProvider>
                        </GameContextProvider>
                    </TurnContextProvider>
                </PlayerContextProvider>
            </MatchContextProvider>
        </AnimationContextProvider>
    );
}

