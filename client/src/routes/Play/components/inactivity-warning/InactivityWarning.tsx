import { WarningTriangleIcon } from "../../../../assets/svg";
import { WHITE_SPACE } from "../../../../env";
import { useEffect } from "react";
import "./styles/InactivityWarning.css";

export interface InactivityWarningProps {
    setShowInactivityWarning: React.Dispatch<React.SetStateAction<boolean>>;
}

export default function InactivityWarning(props: InactivityWarningProps) {
    const { setShowInactivityWarning } = props;

    // Self removal on any mouse click
    useEffect(() => {
        const handleMouseClick = () => setShowInactivityWarning(false);
        window.addEventListener("click", handleMouseClick);

        return () => {
            window.removeEventListener("click", handleMouseClick);
        };
    }, [setShowInactivityWarning]);

    const text = "You must participate otherwise you will get kicked out and lose the match!";

    return (
        <div id="inactivity-warning">
            <WarningTriangleIcon />
            {WHITE_SPACE}
            {text}
        </div>
    );
}