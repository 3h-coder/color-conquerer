import { LocationPinIcon } from "../../../../assets/svg";
import { SvgContainer } from "../../../../components/containers";
import { useTurnInfo } from "../../../../contexts/TurnContext";

export default function SpawnButton() {
    const { canInteract } = useTurnInfo();

    const spawnIconSize = "max(10px, 0.8vmin)";

    return (
        <button id="spawn-button" disabled={!canInteract}>
            <SvgContainer style={{ height: spawnIconSize, width: spawnIconSize }}>
                <LocationPinIcon />
            </SvgContainer>
            Spawn
        </button>
    );
}