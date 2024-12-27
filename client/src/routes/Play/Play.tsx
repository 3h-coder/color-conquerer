import MatchContextProvider from "../../contexts/MatchContext";
import PlayerContextProvider from "../../contexts/PlayerContext";
import PlayerModeContextProvider from "../../contexts/PlayerModeContext";
import PlayersGameInfoContextProvider from "../../contexts/PlayersGameInfoContext";
import TurnInfoContextProvider from "../../contexts/TurnContext";
import '../../style/css/Play.css';
import PlayContent from "./PlayContent";

export default function Play() {
    return (
        <MatchContextProvider>
            <PlayerContextProvider>
                <TurnInfoContextProvider>
                    <PlayersGameInfoContextProvider>
                        <PlayerModeContextProvider>
                            <PlayContent />
                        </PlayerModeContextProvider>
                    </PlayersGameInfoContextProvider>
                </TurnInfoContextProvider>
            </PlayerContextProvider>
        </MatchContextProvider>
    );
}


