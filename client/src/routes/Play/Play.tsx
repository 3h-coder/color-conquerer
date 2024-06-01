import MatchContextProvider from "../../contexts/MatchContext";
import GameBoard from "./components/GameBoard";

export default function Play() {

    return (
        <MatchContextProvider>
            <GameBoard />
        </MatchContextProvider>
    )
}