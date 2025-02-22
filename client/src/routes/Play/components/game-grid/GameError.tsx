interface GameErrorProps {
    errorMessage: string
}

export default function GameError(props: GameErrorProps) {
    const { errorMessage } = props;

    return <div className="game-error">{errorMessage}</div>
}