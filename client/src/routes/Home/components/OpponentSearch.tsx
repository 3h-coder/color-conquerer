import LoadingSpinner from "../../../components/LoadingSpinner";

interface OpponentSearchProps {
    ref: React.RefObject<HTMLDivElement>;    
}

export default function OpponentSearch(props: OpponentSearchProps) {
    const { ref } = props;

    return (
        <div className="opponent-search-container" ref={ref}>
            <LoadingSpinner />
            <h3>Searching for an opponent</h3>
            <button>Cancel</button>
        </div>
    );
}