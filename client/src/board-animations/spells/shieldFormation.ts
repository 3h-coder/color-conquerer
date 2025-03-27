import { MatchActionDto } from "../../dto/actions/MatchActionDto";
import { isShieldFormationMetadata, ShieldFormationMetadataDto } from "../../dto/spell/metadata/ShieldFormationMetadataDto";
import { convertCoordsToKey } from "../../utils/actionHintUtils";
import { getHtmlCell } from "../../utils/cellUtils";
import { cleanup } from "../../utils/domUtils";

export function handleShieldFormationAnimation(spellAction: MatchActionDto) {
    const metadata = spellAction.metadata;
    // Should never happen, but just in case
    if (!isShieldFormationMetadata(metadata))
        return;

    const shieldFormationMetadata = metadata as ShieldFormationMetadataDto;
    const squarePerCoordinates = shieldFormationMetadata.squarePerCoordinates;
    const squares = shieldFormationMetadata.squares;
    const { rowIndex: chosenRowIndex, columnIndex: chosenColumnIndex } = spellAction.impactedCoords;

    const correspondingSquareIndex = squarePerCoordinates[convertCoordsToKey(chosenRowIndex, chosenColumnIndex)];
    if (correspondingSquareIndex === undefined)
        return;

    const square = squares[correspondingSquareIndex];
    const htmlCells = square
        .map(cellCoords => getHtmlCell(cellCoords.rowIndex, cellCoords.columnIndex))
        .filter((cell): cell is HTMLElement => cell !== null);

    displayReinforcementEffect(htmlCells);
}

function displayReinforcementEffect(cells: HTMLElement[]) {
    if (cells.length === 0)
        return;

    const styleClass = "shield-applied-effect";
    const cleanupDelayInMs = 1700;

    const auraContainer = document.createElement('div');
    auraContainer.classList.add(styleClass);

    // Determine the bounding box of the cells
    const rects = cells.map(cell => cell.getBoundingClientRect());
    const minX = Math.min(...rects.map(rect => rect.left));
    const minY = Math.min(...rects.map(rect => rect.top));
    const maxX = Math.max(...rects.map(rect => rect.right));
    const maxY = Math.max(...rects.map(rect => rect.bottom));

    // Calculate square dimensions
    const width = maxX - minX;
    const height = maxY - minY;
    const size = Math.max(width, height); // Ensures it's a square

    // Position the aura container
    auraContainer.style.left = `${minX}px`;
    auraContainer.style.top = `${minY}px`;
    auraContainer.style.width = `${size}px`;
    auraContainer.style.height = `${size}px`;

    document.body.appendChild(auraContainer);

    cleanup(auraContainer, cleanupDelayInMs);
}