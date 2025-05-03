import { usePlayerInfo } from "../../../../contexts/PlayerContext";
import { usePlayerResources } from "../../../../contexts/PlayerResourcesContext";
import PlayerResourcesInfo from "./PlayerResourcesInfo";

export default function MyPlayerResources() {
    const { isPlayer1 } = usePlayerInfo();
    const { playerResourceBundle } = usePlayerResources();

    const playerResources = isPlayer1
        ? playerResourceBundle.player1Resources
        : playerResourceBundle.player2Resources;

    return (
        <PlayerResourcesInfo
            playerResourcesDto={playerResources}
            hpFirst={true}
        />
    );
}
