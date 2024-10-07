import React from "react";
import { SpinnerIcon } from "../assets/svg";
import { SvgContainer } from "./containers";

interface LoadingSpinnerProps {
    style?: React.CSSProperties;
    className?: string;
}

export default function LoadingSpinner(props: LoadingSpinnerProps) {
    const { style, className } = props;

    return (
        <SvgContainer style={{ animation: "rotate 2s infinite", ...style }} className={className}>
            <SpinnerIcon />
        </SvgContainer>
    )
}