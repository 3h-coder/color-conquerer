import { PartialSpellDto } from "./PartialSpellDto";

export interface SpellDto extends PartialSpellDto {
    count: number;
    maxCount: number;
}