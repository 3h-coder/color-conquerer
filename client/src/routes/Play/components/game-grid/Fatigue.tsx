import { SkullIcon } from "../../../../assets/svg";

interface FatigueProps {
    fatigue: number;
}

export default function Fatigue(props: FatigueProps) {
    const { fatigue } = props;
    const text = `Exhausted, taking ${fatigue} damage`;
    const iconSize = "2.2rem";

    return (
        <div id="fatigue-container">
            <SkullIcon style={{ width: iconSize, height: iconSize }} />
            <h3>Fatigue</h3>
            <span id="fatigue-value">{text}</span>
        </div>
    );

}