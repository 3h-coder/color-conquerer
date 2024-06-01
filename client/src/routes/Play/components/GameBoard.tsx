import { CellInfoDto } from "../../../dto/CellInfoDto";
import GameCell from "./GameCell";

const defaultCellInfo: CellInfoDto = {}

export default function GameBoard() {
    const rows = 20;
    const columns = rows;
    const boardArray: CellInfoDto[][] = new Array(rows).fill(defaultCellInfo)
        .map(() => new Array(columns).fill(defaultCellInfo));

    return (
        <div className="board-container">
            {boardArray.map((row, rowIndex) => (
                <div className="row" key={rowIndex}>
                    {row.map((_cell, colIndex) => (
                        <GameCell key={colIndex}></GameCell>
                    ))}
                </div>
            ))}
        </div>
    );
}