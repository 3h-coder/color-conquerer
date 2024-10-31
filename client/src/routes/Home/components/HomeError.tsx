import { useEffect, useState } from "react";
import { XMarkIcon } from "../../../assets/svg";
import { SvgContainer } from "../../../components/containers";
import { useHomeError } from "../../../contexts/HomeErrorContext";
import { constants } from "../../../env";
import { extractKey } from "../../../utils/localStorageUtils";

export default function HomeError() {
    const { error, setHomeError } = useHomeError();
    const [display, setDisplay] = useState(false);
    const [errorFromLocalStorage] = useState(() => {
        return extractKey(constants.localStorageKeys.homeError);
    });

    useEffect(() => {
        if (error || errorFromLocalStorage) {
            setDisplay(true);
        }
    }, [error, errorFromLocalStorage])

    function onClose() {
        setDisplay(false);
        setHomeError("");
    }

    const crossButtonDimensions = "max(15px, 2.4vmin)";

    return (
        <div className="home-error-container" style={{ opacity: display ? 1 : 0, userSelect: display ? "text" : "none" }}>
            <span>{error || errorFromLocalStorage}</span>
            <button className="transparent no-border fit-content" onClick={onClose}>
                <SvgContainer style={{ width: crossButtonDimensions, height: crossButtonDimensions }}>
                    <XMarkIcon />
                </SvgContainer>
            </button>
        </div>
    );
}