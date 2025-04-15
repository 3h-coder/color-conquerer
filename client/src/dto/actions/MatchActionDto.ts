import { ActionType } from "../../enums/actionType";
import { PartialSpellDto } from "../spell/PartialSpellDto";
import { ActionMetadataDto } from "./ActionMetadataDto";

export interface MatchActionDto {
    player1: boolean;
    type: ActionType;
    // Only if the action type is spell
    spell: PartialSpellDto | null;
    metadata: ActionMetadataDto;
    specificMetadata: unknown | null;
}