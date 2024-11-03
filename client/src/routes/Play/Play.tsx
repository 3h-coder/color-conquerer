import MatchContextProvider from "../../contexts/MatchContext";
import PlayerContextProvider from "../../contexts/PlayerContext";
import TurnInfoContextProvider from "../../contexts/TurnContext";
import '../../style/css/Play.css';
import PlayContent from "./PlayContent";

export default function Play() {
    return (
        <MatchContextProvider>
            <PlayerContextProvider>
                <TurnInfoContextProvider>
                    <PlayContent />
                </TurnInfoContextProvider>
            </PlayerContextProvider>
        </MatchContextProvider>
    );
}


