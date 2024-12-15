import { useMatchInfo } from "../../../../contexts/MatchContext";
import { useTurnInfo } from "../../../../contexts/TurnContext";
import { Events } from "../../../../enums/events";
import { socket } from "../../../../env";
import { clearBoardColoring } from "../../../../utils/boardUtils";

export default function EndTurnButton() {
    const { matchInfo } = useMatchInfo();
    const { canInteract } = useTurnInfo();

    const text = "End Turn";

    function onClick() {
        clearBoardColoring(matchInfo.boardArray, (cell) => cell.owner !== 0);
        socket.emit(Events.CLIENT_TURN_END);
    }

    return (
        <button className="end-turn" disabled={!canInteract} onClick={onClick}>
            {text}
        </button>
    );
}