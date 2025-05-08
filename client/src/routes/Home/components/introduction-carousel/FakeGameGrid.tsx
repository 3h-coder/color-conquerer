import { useEffect, useState } from "react";
import { getCellId } from "../../../../utils/cellUtils";
import GameCell from "../../../Play/components/game-grid/GameCell";
import { GridInner, GridOuter, GridRow } from "../../../Play/components/game-grid/GameGrid";
import { getDefaultGameGrid } from "./fakeGameGridSetupUtils";
import { FakeGameGridSetup } from "./Setups/FakeGameGridSetup";

export interface FakeGameGridProps {
    setup: FakeGameGridSetup;
}

export default function FakeGameGrid(props: FakeGameGridProps) {
    const { setup } = props;
    const [boardArray, setBoardArray] = useState(getDefaultGameGrid(setup.coordinatesSetup));
    const gridStyle: React.CSSProperties = {
        gridTemplateColumns: `repeat(${boardArray.length}, 1fr)`
    };
    const cellSize = "max(15px, 3vmin)";
    const cellStyle: React.CSSProperties = {
        width: cellSize,
        height: cellSize
    };

    useEffect(() => {

    }, []);

    return (
        <GridOuter className="fake-game-grid">
            <GridInner style={gridStyle}>
                {boardArray.map((row, rowIndex) => (
                    <GridRow className="row" id={`r-${rowIndex}`} key={rowIndex}>
                        {row.map((cellInfo, colIndex) => (
                            <GameCell
                                key={colIndex}
                                id={getCellId(rowIndex, colIndex)}
                                isPlayer1={true}
                                cellInfo={cellInfo}
                                canInteract={false}
                                canDisplayEffects={false}
                                attachedBehavior={undefined}
                                style={cellStyle}
                            />
                        ))}
                    </GridRow>
                ))}
            </GridInner>
        </GridOuter>
    );
}

