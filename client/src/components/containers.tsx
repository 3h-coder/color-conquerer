export interface ContainerProps {
    style?: React.CSSProperties;
    id?: string;
    className?: string;
    children?: React.ReactNode;
}

export function SvgContainer(props: ContainerProps) {
    const { style, className, id, children } = props;

    const extraClassStyle = className !== undefined ? ` ${className}` : "";

    return (
        <div className={`svg-container${extraClassStyle}`} style={style} id={id}>
            {children}
        </div>
    );
}

export function CenteredContainer(props: ContainerProps) {
    const { style, className, id, children } = props;

    const extraClassStyle = className !== undefined ? ` ${className}` : "";

    return (
        <div className={`centered-container${extraClassStyle}`} style={style} id={id}>
            {children}
        </div>
    );
}