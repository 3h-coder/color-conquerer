import { Link } from "react-router-dom";
import { paths } from "../../paths";

interface HomeButtonsProps {
    ref: React.RefObject<HTMLDivElement>;    
}

export default function HomeButtons(props: HomeButtonsProps) {

    const {ref} = props;

    function requestMultiplayerMatch() {
        
    }

    return (
        <div className="home-buttons-container" ref={ref}>
            <Link to={`/${paths.play}`} className="play button">
                Solo
            </Link>
            <button onClick={requestMultiplayerMatch}>
                Multiplayer
            </button>
        </div>
    );
}