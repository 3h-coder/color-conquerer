import { ActionCallbackId } from "../../enums/actionCallbackId";
import { GameContextDto } from "../gameState/GameContextDto";
import { CoordinatesDto } from "../misc/CoordinatesDto";
import { PartialSpellDto } from "../spell/PartialSpellDto";
import { MatchActionDto } from "./MatchActionDto";


export interface ActionCallbackDto {
    id: ActionCallbackId;
    parentAction: MatchActionDto;
    parentCallbackId: ActionCallbackId;
    spellCause: PartialSpellDto | null;
    impactedCoords: CoordinatesDto | null;
    deaths: CoordinatesDto[];
    updatedGameContext: GameContextDto;
}