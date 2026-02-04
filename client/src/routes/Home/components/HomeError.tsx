import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { XMarkIcon } from "../../../assets/svg";
import { SvgContainer } from "../../../components/containers";
import { useHomeError } from "../../../contexts/HomeErrorContext";
import { EMPTY_STRING } from "../../../env";

export default function HomeError() {
    const location = useLocation();
    const { error, setHomeError } = useHomeError();
    const [display, setDisplay] = useState(false);
    const [errorFromNavigation] = useState(() => {
        return location.state?.error || null;
    });

    useEffect(() => {
        if (error || errorFromNavigation) {
            setDisplay(true);
        }
    }, [error, errorFromNavigation]);

    function onClose() {
        setDisplay(false);
        setHomeError(EMPTY_STRING);
    }

    const crossButtonDimensions = "max(15px, 2.4vmin)";

    return (
        <div className="home-error-container" style={{ opacity: display ? 1 : 0, userSelect: display ? "text" : "none" }}>
            <span>{error || errorFromNavigation}</span>
            <button className="transparent no-border fit-content" onClick={onClose}>
                <SvgContainer style={{ width: crossButtonDimensions, height: crossButtonDimensions }}>
                    <XMarkIcon />
                </SvgContainer>
            </button>
        </div>
    );
}