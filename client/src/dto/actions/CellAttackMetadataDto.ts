export interface CellAttackMetadataDto {
    isRangedAttack: boolean;
    isRetaliated: boolean;
}

export function isCellAttackMetadataDto(
    metadata: unknown
): metadata is CellAttackMetadataDto {
    return (
        typeof metadata === "object" &&
        metadata !== null &&
        "isRangedAttack" in metadata &&
        typeof (metadata as CellAttackMetadataDto).isRangedAttack === "boolean"
        && "isRetaliated" in metadata &&
        typeof (metadata as CellAttackMetadataDto).isRetaliated === "boolean"
    );
}