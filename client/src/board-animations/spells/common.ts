import { MatchActionDto } from "../../dto/actions/MatchActionDto";
import { isPositioningMetadataDto, PositioningMetadataDto } from "../../dto/spell/metadata/PositioningMetadataDto";
import { HTMLElements } from "../../env";
import { convertCoordsToKey } from "../../utils/actionHintUtils";
import { getHtmlCell } from "../../utils/cellUtils";
import { cleanup } from "../../utils/domUtils";

export function getCellsInFormation(spellAction: MatchActionDto) {
    const metadata = spellAction.metadata;
    // Should never happen, but just in case
    if (!isPositioningMetadataDto(metadata))
        return [];

    const shieldFormationMetadata = metadata as PositioningMetadataDto;
    const squarePerCoordinates = shieldFormationMetadata.formationPerCoordinates;
    const squares = shieldFormationMetadata.cellFormations;
    const { rowIndex: chosenRowIndex, columnIndex: chosenColumnIndex } = spellAction.impactedCoords;

    const correspondingSquareIndex = squarePerCoordinates[convertCoordsToKey(chosenRowIndex, chosenColumnIndex)];
    if (correspondingSquareIndex === undefined)
        return [];

    const square = squares[correspondingSquareIndex];
    const htmlCells = square
        .map(cellCoords => getHtmlCell(cellCoords.rowIndex, cellCoords.columnIndex))
        .filter((cell): cell is HTMLElement => cell !== null);

    return htmlCells;
}

export function displayAppliedSpellEffect(cell: HTMLElement) {
    const auraContainer = document.createElement(HTMLElements.div);
    auraContainer.classList.add("spell-applied-effect");

    cell.appendChild(auraContainer);

    cleanup(auraContainer, 1700);
}