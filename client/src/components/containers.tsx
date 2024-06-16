interface SvgContainerProps {
    style?: React.CSSProperties;
    className?: string;
    children?: React.ReactNode;
}

export function SvgContainer(props: SvgContainerProps) {
    const { style, className, children } = props;

    const extraClassStyle = className !== undefined ? ` ${className}` : "";

    return (
        <div className={`svg-container${extraClassStyle}`} style={style}>
            {children}
        </div>
    );
}