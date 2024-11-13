import { CenteredContainer } from "../../../components/containers";

interface TurnSwapImageProps {
    imagePath: string;
}

export default function TurnSwapImage(props: TurnSwapImageProps) {
    const { imagePath } = props;

    return (
        <CenteredContainer className="turn-swap-image-container">
            <img className="turn-swap-image" src={imagePath} />
        </CenteredContainer>
    )
}