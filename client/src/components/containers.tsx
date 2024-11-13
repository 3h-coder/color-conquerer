interface ContainerProps {
    style?: React.CSSProperties;
    className?: string;
    children?: React.ReactNode;
}

export function SvgContainer(props: ContainerProps) {
    const { style, className, children } = props;

    const extraClassStyle = className !== undefined ? ` ${className}` : "";

    return (
        <div className={`svg-container${extraClassStyle}`} style={style}>
            {children}
        </div>
    );
}

export function CenteredContainer(props: ContainerProps) {
    const { style, className, children } = props;

    const extraClassStyle = className !== undefined ? ` ${className}` : "";

    return (
        <div className={`centered-container${extraClassStyle}`} style={style}>
            {children}
        </div>
    );
}