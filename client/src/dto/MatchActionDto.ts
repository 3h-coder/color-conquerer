import { ActionType } from "../enums/actionType";
import { CoordinatesDto } from "./CoordinatesDto";
import { PartialSpellDto } from "./PartialSpellDto";

export interface MatchActionDto {
    player1: boolean;
    type: ActionType;
    // Spell castings have no originating coordinates
    originatingCellCoords: CoordinatesDto | null;
    impactedCoords: CoordinatesDto[];
    // Only if the action type is spell
    spell: PartialSpellDto | null;
}