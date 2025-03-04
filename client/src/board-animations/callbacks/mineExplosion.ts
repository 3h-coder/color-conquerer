import { Emitter, EmitterConfigV3 } from "@pixi/particle-emitter";
import { ParticleContainer, Texture } from "pixi.js";
import { createRoot } from "react-dom/client";
import sparkImage from "../../assets/images/spark.png";
import { ActionCallbackDto } from "../../dto/ActionCallbackDto";
import { PartialSpellDto } from "../../dto/PartialSpellDto";
import { pixiApp } from "../../env";
import { LandMine } from "../../routes/Play/components/game-grid/GameCell";
import { getHtmlCell } from "../../utils/cellUtils";
import { cleanup, cleanupStyleClass, delay } from "../../utils/domUtils";
import { startEmitting } from "../../utils/pixiUtils";

export async function animateMineExplosion(callback: ActionCallbackDto, currentPlayerisPlayer1: boolean, setActionSpell: (spellAction: PartialSpellDto | null) => void) {
    const parentAction = callback.parentAction;
    const explosionCenter = parentAction.impactedCoords;

    const htmlCell = getHtmlCell(explosionCenter.rowIndex, explosionCenter.columnIndex);
    if (!htmlCell)
        return;

    const mineBlinkingDurationInMs = 1000;

    showSpellCauseDescription(setActionSpell, callback);
    showBlinkingMine(htmlCell, currentPlayerisPlayer1, mineBlinkingDurationInMs);

    await delay(mineBlinkingDurationInMs);

    triggerShockWave(htmlCell);
    triggerSparks(htmlCell);
    shakeGameGrid();
}

function showSpellCauseDescription(setActionSpell: (spellAction: PartialSpellDto | null) => void, callback: ActionCallbackDto) {
    setActionSpell(callback.spellCause);
    setTimeout(() => setActionSpell(null), 3500);
}

function showBlinkingMine(htmlCell: HTMLElement, currentPlayerisPlayer1: boolean, lifetimeDurationInMs: number) {
    const landMine = LandMine({ isPlayer1: currentPlayerisPlayer1, isBlinking: true });
    const container = document.createElement("div");
    // const existingLandMine = htmlCell.querySelector(".land-mine");
    // if (existingLandMine)
    //     existingLandMine.remove();

    htmlCell.appendChild(container);
    const root = createRoot(container);
    root.render(landMine);

    setTimeout(() => {
        root.unmount(); // Properly unmount the React component
        container.remove(); // Remove the container
    }, lifetimeDurationInMs);

}

function triggerShockWave(htmlCell: HTMLElement) {
    const cleanupDelayInMs = 380;

    const explosion = document.createElement("div");
    explosion.classList.add("cell-explosion");

    htmlCell.appendChild(explosion);
    cleanup(explosion, cleanupDelayInMs);
}

function shakeGameGrid() {
    const shakeClass = "shake";
    const gameGrid = document.getElementById("grid-outer");
    if (!gameGrid)
        return;

    gameGrid.classList.add(shakeClass);
    cleanupStyleClass(gameGrid, shakeClass, 500);
}

function triggerSparks(htmlCell: HTMLElement) {
    const explosionContainer = new ParticleContainer();
    pixiApp.stage.addChild(explosionContainer);

    // Get the cell's position relative to the viewport
    const cellRect = htmlCell.getBoundingClientRect();
    const cellCenterX = cellRect.left + cellRect.width / 2;
    const cellCenterY = cellRect.top + cellRect.height / 2;

    // Convert to Pixi.js coordinate space
    explosionContainer.x = cellCenterX;
    explosionContainer.y = cellCenterY;

    const emitterLifetimeInSec = 0.2;

    const particleConfig: EmitterConfigV3 = {
        lifetime: {
            min: 0.5,
            max: 0.5
        },
        frequency: 0.0001,
        emitterLifetime: emitterLifetimeInSec,
        maxParticles: 30,
        addAtBack: false,
        pos: {
            x: 0,
            y: 0
        },
        behaviors: [
            {
                type: "alpha",
                config: {
                    alpha: {
                        // Let them fade out over time
                        list: [
                            { time: 0, value: 0.8 },
                            { time: 1, value: 0.1 }
                        ]
                    }
                }
            },
            {
                type: "moveSpeed",
                config: {
                    speed: {
                        // Let them get slower over time
                        list: [
                            { time: 0, value: 200 },
                            { time: 1, value: 100 }
                        ]
                    }
                }
            },
            {
                type: "scale",
                config: {
                    scale: {
                        // Let them shrink over time
                        list: [
                            { time: 0, value: 0.02 },
                            { time: 1, value: 0.01 }
                        ]
                    },
                    minMult: 1
                }
            },
            {
                type: "color",
                config: {
                    color: {
                        list: [
                            { time: 0, value: "fb1010" },
                            { time: 1, value: "f5b830" }
                        ]
                    }
                }
            },
            {
                type: "rotationStatic",
                config: {
                    min: 0,
                    max: 360
                }
            },
            {
                type: "textureSingle",
                config: {
                    texture: Texture.from(sparkImage)
                }
            },
            {
                type: "spawnShape",
                config: {
                    type: "torus",
                    data: {
                        x: 0,
                        y: 0,
                        radius: 10,
                        innerRadius: 0,
                        affectRotation: false
                    }
                }
            }
        ]
    };

    const emitter = new Emitter(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        explosionContainer as any,
        particleConfig
    );

    startEmitting(emitter);

    // Clean up
    setTimeout(() => {
        emitter.destroy();
        explosionContainer.destroy();
    }, emitterLifetimeInSec * 1000 + 200);

}
