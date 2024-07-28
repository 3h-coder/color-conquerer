import { useEffect } from "react";
import { useMatchInfo } from "../../../contexts/MatchContext";
import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { colors } from "../../../style/constants";
import GameCell from "./GameCell";

export default function GameBoard() {
    const { matchInfo } = useMatchInfo();
    const { playerInfo } = usePlayerInfo();
    const boardArray = matchInfo.boardArray;

    useEffect(() => {

        colorBoard();

        function colorBoard() {
            boardArray.forEach(row => {
                row.forEach(cell => {
                    if (cell.owner === 0)
                        return;

                    const htmlCell = document.getElementById(`c-${cell.rowIndex}-${cell.columnIndex}`);
                    if (playerInfo.isPlayer1) {
                        htmlCell!.style.backgroundColor = cell.owner === 1 ? colors.ownCell : colors.opponentCell;
                    } else {
                        htmlCell!.style.backgroundColor = cell.owner === 2 ? colors.ownCell : colors.opponentCell;
                    }
                });
            });
        }
    });

    return (
        <div className="board" style={{ transform: `${playerInfo.isPlayer1 ? "rotate(180deg)" : ""}` }}>
            {boardArray.map((row, rowIndex) => (
                <div className="row" id={`r-${rowIndex}`} key={rowIndex}>
                    {row.map((_cell, colIndex) => (
                        <GameCell key={colIndex} id={`c-${rowIndex}-${colIndex}`} />
                    ))}
                </div>
            ))}
        </div>
    );
}