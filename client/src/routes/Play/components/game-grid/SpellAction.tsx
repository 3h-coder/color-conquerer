import { ContainerProps, Separator, SvgContainer } from "../../../../components/containers";
import { PartialSpellDto } from "../../../../dto/PartialSpellDto";
import { getSpellIcon } from "../shared";

interface SpellActionProps {
    spell: PartialSpellDto;
}

export default function SpellAction(props: SpellActionProps) {
    const { spell } = props;

    const iconSize = "1.2rem";

    return (
        <div className="action-spell-description">
            <HeaderSection>
                <SvgContainer style={{ width: iconSize, height: iconSize }}>
                    {getSpellIcon(spell.id)}
                </SvgContainer>
                {spell.name}
            </HeaderSection>
            <Separator style={{ marginBottom: "max(1vmin, 5px)" }} />
            {spell.description}
            <div className="spell-mana-cost">
                {spell.manaCost}
            </div>
        </div>
    );
}

function HeaderSection(props: ContainerProps) {
    const { children } = props;

    return (
        <div className="casted-spell-header">
            {children}
        </div>
    );
}

