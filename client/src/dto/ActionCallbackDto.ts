import { ActionCallbackId } from "../enums/actionCallbackId";
import { CoordinatesDto } from "./CoordinatesDto";
import { GameContextDto } from "./GameContextDto";
import { MatchActionDto } from "./MatchActionDto";
import { PartialSpellDto } from "./PartialSpellDto";

export interface ActionCallbackDto {
    id: ActionCallbackId;
    parentAction: MatchActionDto;
    parentCallbackId: ActionCallbackId;
    spellCause: PartialSpellDto | null;
    impactedCoords: CoordinatesDto | null;
    updatedGameContext: GameContextDto;
}