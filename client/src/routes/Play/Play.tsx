import MatchContextProvider from "../../contexts/MatchContext";
import PlayerContextProvider from "../../contexts/PlayerContext";
import PlayerModeContextProvider from "../../contexts/PlayerModeContext";
import PlayersResourcesContextProvider from "../../contexts/PlayersGameInfoContext";
import TurnInfoContextProvider from "../../contexts/TurnContext";
import '../../style/css/Play.css';
import PlayContent from "./PlayContent";

export default function Play() {
    return (
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
    );
}


