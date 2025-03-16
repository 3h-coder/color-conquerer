import LoadingSpinner from "../../../components/LoadingSpinner";

export default function OpponentSearch() {
    const loadingSpinnerDimensions = "max(20px, 3vmin)";

    return (
        <div className="opponent-search-container">
            <LoadingSpinner style={{ width: loadingSpinnerDimensions, height: loadingSpinnerDimensions }} />
            <h3 className="no-margin">Searching for an opponent...</h3>
        </div>
    );
}