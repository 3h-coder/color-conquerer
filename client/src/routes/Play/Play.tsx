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
        <AnimationContextProvider>
            <MatchContextProvider>
                <PlayerContextProvider>
                    <TurnInfoContextProvider>
                        <PlayersResourcesContextProvider>
                            <PlayerModeContextProvider>
                                <PlayContent />
                            </PlayerModeContextProvider>
                        </PlayersResourcesContextProvider>
                    </TurnInfoContextProvider>
                </PlayerContextProvider>
            </MatchContextProvider>
        </AnimationContextProvider>
    );
}


