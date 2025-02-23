import { ActionCallbackId } from "../enums/actionCallbackId";
import { GameContextDto } from "./GameContextDto";
import { MatchActionDto } from "./MatchActionDto";
import { PartialSpellDto } from "./PartialSpellDto";

export interface ActionCallbackDto {
    id: ActionCallbackId;
    parentAction: MatchActionDto;
    spellCause: PartialSpellDto | null;
    updatedGameContext: GameContextDto;
}