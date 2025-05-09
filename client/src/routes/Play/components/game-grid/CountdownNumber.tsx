interface CountdownNumberProps {
    count: number;
}

export default function CountdownNumber(props: CountdownNumberProps) {
    const { count } = props;

    return (
        <div className="countdown-number-container">
            <div className="countdown-number">{count}</div>
        </div>
    );
}
