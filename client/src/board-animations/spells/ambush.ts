import { MatchActionDto } from "../../dto/actions/MatchActionDto";
import { isSpawnInfoDto, SpawnInfoDto } from "../../dto/spell/metadata/SpawnInfoDto";
import { animateCellSpawn } from "../common";

export function handleAmbushAnimation(spellAction: MatchActionDto) {
    if (!isSpawnInfoDto(spellAction.specificMetadata))
        return;

    const spawnInfo = spellAction.specificMetadata as SpawnInfoDto;
    spawnInfo.coordinates.forEach((coord) => {
        animateCellSpawn(coord.rowIndex, coord.columnIndex, true);
    });
}