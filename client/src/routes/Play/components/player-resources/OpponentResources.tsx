import { usePlayerInfo } from "../../../../contexts/PlayerContext";
import { usePlayerResources } from "../../../../contexts/PlayerResourcesContext";
import PlayerResourcesInfo from "./PlayerResourcesInfo";

export default function OpponentResources() {
    const { isPlayer1 } = usePlayerInfo();
    const { playerResourceBundle: playerGameInfoBundle } = usePlayerResources();

    const opponentResources = isPlayer1
        ? playerGameInfoBundle.player2Resources
        : playerGameInfoBundle.player1Resources;

    return (
        <PlayerResourcesInfo playerResourcesDto={opponentResources} />
    );
}
