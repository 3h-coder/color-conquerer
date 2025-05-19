import LoadingSpinner from "../../../components/LoadingSpinner";

interface OpponentSearchProps {
    text: string;
}

export default function OpponentSearch(props: OpponentSearchProps) {
    const { text } = props;
    const loadingSpinnerDimensions = "max(20px, 3vmin)";

    return (
        <div id="opponent-search-container">
            <LoadingSpinner style={{ width: loadingSpinnerDimensions, height: loadingSpinnerDimensions }} />
            <h3 className="no-margin">{text}</h3>
        </div>
    );
}