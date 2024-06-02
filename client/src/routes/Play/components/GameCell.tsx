interface GameCellProps {
    id: string;
}

export default function GameCell(props: GameCellProps) {
    const {id} = props;

    return (
        <div className="cell" id={id}/>
    )
}