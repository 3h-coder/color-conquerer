import { useEffect, useState } from "react";
import { XMarkIcon } from "../../../assets/svg";
import { SvgContainer } from "../../../components/containers";
import { useHomeError } from "../../../contexts/HomeErrorContext";

export default function HomeError() {
    const { error, setHomeError } = useHomeError();
    const [display, setDisplay] = useState(false);

    useEffect(() => {
        if (error !== "" && error !== undefined) {
            setDisplay(true);
        }
    }, [error])

    function onClose() {
        setDisplay(false);
        setHomeError("");
    }

    const crossButtonDimensions = "max(15px, 2.4vmin)";

    return (
        <div className="home-error-container" style={{ opacity: display ? 1 : 0, userSelect: display ? "text" : "none" }}>
            <span>{error}</span>
            <button className="transparent no-border fit-content" onClick={onClose}>
                <SvgContainer style={{ width: "fit-content", height: "fit-content" }}>
                    <XMarkIcon style={{
                        width: crossButtonDimensions,
                        height: crossButtonDimensions,
                    }} />
                </SvgContainer>
            </button>
        </div>
    );
}