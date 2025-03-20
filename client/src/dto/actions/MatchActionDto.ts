import { ActionType } from "../../enums/actionType";
import { CoordinatesDto } from "../misc/CoordinatesDto";
import { PartialSpellDto } from "../spell/PartialSpellDto";

export interface MatchActionDto {
    player1: boolean;
    type: ActionType;
    // Spell castings have no originating coordinates
    originatingCellCoords: CoordinatesDto | null;
    impactedCoords: CoordinatesDto;
    // Only if the action type is spell
    spell: PartialSpellDto | null;
    metadata: unknown;
}