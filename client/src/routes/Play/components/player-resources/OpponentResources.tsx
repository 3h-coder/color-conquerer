import { usePlayerInfo } from "../../../../contexts/PlayerContext";
import { usePlayerResources } from "../../../../contexts/PlayerResourcesContext";
import PlayerResourcesInfo from "./PlayerResourcesInfo";

export default function OpponentResources() {
    const { isPlayer1 } = usePlayerInfo();
    const { playerResourceBundle } = usePlayerResources();

    const opponentResources = isPlayer1
        ? playerResourceBundle.player2Resources
        : playerResourceBundle.player1Resources;

    return (
        <PlayerResourcesInfo playerResourcesDto={opponentResources} own={false} />
    );
}
