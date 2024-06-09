import { CellInfoDto } from "../../../dto/CellInfoDto";
import { BoardHelper } from "../Helpers/BoardHelper";
import GameCell from "./GameCell";


export default function GameBoard() {
    const size = 15;
    const boardArray: CellInfoDto[][] = BoardHelper.createBoardArray(size);

    return (
        <div className="board">
            {boardArray.map((row, rowIndex) => (
                <div className="row" id={`r-${rowIndex}`} key={rowIndex}>
                    {row.map((_cell, colIndex) => (
                        <GameCell key={colIndex} id={`cell-${rowIndex}-${colIndex}`} />
                    ))}
                </div>
            ))}
        </div>
    );
}