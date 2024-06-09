import LoadingSpinner from "../../../components/LoadingSpinner";

interface OpponentSearchProps {
    opponentFound: boolean
}

export default function OpponentSearch(props: OpponentSearchProps) {

    const { opponentFound } = props;

    const loadingSpinnerDimensions = "max(20px, 3vmin)";

    return (
        <div className="opponent-search-container">
            <LoadingSpinner style={{ width: loadingSpinnerDimensions, height: loadingSpinnerDimensions }} />
            <h3 className="no-margin">{opponentFound ? "Opponent found, preparing..." : "Searching for an opponent..."}</h3>
        </div>
    );
}