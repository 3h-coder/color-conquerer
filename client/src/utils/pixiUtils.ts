import { Emitter } from "@pixi/particle-emitter";

/**
 * Makes the emitter start emitting particles.
 * 
 * See https://github.com/pixijs-userland/particle-emitter
 */
export function startEmitting(emitter: Emitter) {
    let elapsed = Date.now();
    // Update function every frame
    function update() {

        // Update the next frame
        requestAnimationFrame(update);

        const now = Date.now();

        // The emitter requires the elapsed
        // number of seconds since the last update
        emitter.update((now - elapsed) * 0.001);
        elapsed = now;
    }

    // Start emitting
    emitter.emit = true;
    // Start the update
    update();
}