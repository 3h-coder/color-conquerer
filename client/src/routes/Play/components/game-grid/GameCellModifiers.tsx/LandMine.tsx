import { LandMineIcon } from "../../../../../assets/svg";
import { EMPTY_STRING } from "../../../../../env";
import { cellStyle } from "../../../../../style/constants";
import { WithIconProps } from "../GameCellModifier";

interface LandMineProps extends WithIconProps {
    isBlinking: boolean;
}

export function LandMine(props: LandMineProps) {
    const { rotateIcon, isBlinking } = props;

    const blinkStyle: React.CSSProperties = {
        ["--color1" as string]: "black",
        ["--color2" as string]: "red",
        ["--frequency" as string]: "0.2s",
    };

    return (
        <div className={`land-mine ${cellStyle.classNames.absPosition}`}>
            <LandMineIcon
                style={{
                    fill: "black",
                    transform: rotateIcon ? cellStyle.rotate180deg : undefined,
                    animation: isBlinking ? "fill-blink 0.2s infinite" : EMPTY_STRING,
                    ...blinkStyle,
                }}
            />
        </div>
    );
}