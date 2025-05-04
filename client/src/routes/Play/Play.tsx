import AnimationContextProvider from "../../contexts/AnimationContext";
import MatchContextProvider from "../../contexts/MatchContext";
import PlayerContextProvider from "../../contexts/PlayerContext";
import PlayerModeContextProvider from "../../contexts/PlayerModeContext";
import PlayersResourcesContextProvider from "../../contexts/PlayerResourcesContext";
import TurnInfoContextProvider from "../../contexts/TurnContext";
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
                    <TurnInfoContextProvider>
                        <PlayersResourcesContextProvider>
                            <PlayerModeContextProvider>
                                {children}
                            </PlayerModeContextProvider>
                        </PlayersResourcesContextProvider>
                    </TurnInfoContextProvider>
                </PlayerContextProvider>
            </MatchContextProvider>
        </AnimationContextProvider>
    );
}

