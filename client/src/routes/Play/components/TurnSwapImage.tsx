interface TurnSwapImageProps {
    imagePath: string;
}

export default function TurnSwapImage(props: TurnSwapImageProps) {
    const { imagePath } = props;

    return (
        <div className="turn-swap-image-container">
            <img className="turn-swap-image" src={imagePath} />
        </div>
    )
}