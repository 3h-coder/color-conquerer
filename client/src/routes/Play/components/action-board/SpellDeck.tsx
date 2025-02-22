import { useEffect, useState } from "react";
import { SpellDto } from "../../../../dto/SpellDto";
import { SpellsDto } from "../../../../dto/SpellsDto";
import { Events } from "../../../../enums/events";
import { socket } from "../../../../env";
import { developmentLog } from "../../../../utils/loggingUtils";
import SpellCard from "./SpellCard";

export default function SpellDeck() {
    const [spells, setSpells] = useState<SpellDto[]>([]);

    useEffect(() => {
        socket.emit(Events.CLIENT_REQUEST_SPELLS);
    }, []);

    useEffect(() => {
        function onSpellsReceived(spellsDto: SpellsDto) {
            developmentLog("Received the spells", spellsDto);
            setSpells(spellsDto.spells);
        }

        socket.on(Events.SERVER_SEND_SPELLS, onSpellsReceived);

        return () => {
            socket.off(Events.SERVER_SEND_SPELLS, onSpellsReceived);
        };
    }, []);

    return (
        <div className="spell-deck">
            {spells.map((spell: SpellDto, index: number) => (
                <SpellCard key={index} spell={spell} />
            ))}
        </div>
    );
}