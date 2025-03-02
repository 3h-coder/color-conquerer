import { Application } from "pixi.js";

let app: Application | undefined;

/** Returns the single pixi application instance used for advanced animations */
export async function getPixiApp() {
    if (!app) {
        app = await createPixiApp();
    }

    return app;
}

async function createPixiApp() {
    const app = new Application({
        resizeTo: window,
        backgroundAlpha: 0,
        resolution: window.devicePixelRatio || 1,
    });

    const div = document.createElement("div");
    div.classList.add("pixi-overlay");
    div.appendChild(app.view);
    document.getElementById("pixi-root")?.appendChild(div);

    return app;
}
