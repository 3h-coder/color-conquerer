import React from "react";
import { SpinnerIcon } from "../assets/svg";
import { SvgContainer } from "./containers";

interface LoadingSpinnerProps {
    style?: React.CSSProperties;
}

export default function LoadingSpinner(props: LoadingSpinnerProps) {
    const { style } = props;

    return (
        <SvgContainer style={{ animation: "rotate 2s infinite", ...style }}>
            <SpinnerIcon />
        </SvgContainer>
    )
}