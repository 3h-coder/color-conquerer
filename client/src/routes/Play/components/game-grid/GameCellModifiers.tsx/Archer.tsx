import { BowArrowIcon } from "../../../../../assets/svg";
import { cellStyle } from "../../../../../style/constants";
import { WithIconProps } from "../GameCellModifier";

export function Archer(props: WithIconProps) {
    const { rotateIcon } = props;
    const rotateStyle = rotateIcon ? cellStyle.rotate180deg : undefined;

    return (
        <div className="archer">
            <BowArrowIcon style={{ transform: rotateStyle }} />
        </div>
    );

}