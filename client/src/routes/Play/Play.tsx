import MatchContextProvider from "../../contexts/MatchContext";
import PlayerContextProvider from "../../contexts/PlayerContext";
import '../../style/css/Play.css';
import PlayContent from "./PlayContent";

export default function Play() {
    return (
        <MatchContextProvider>
            <PlayerContextProvider>
                <PlayContent />
            </PlayerContextProvider>
        </MatchContextProvider>
    );
}


