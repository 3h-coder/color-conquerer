import { Application } from "pixi.js";
import { HTMLElements } from "../env";

let app: Application | undefined;

/** Returns the single pixi application instance used for advanced animations */
export function getPixiApp() {
    if (!app) {
        app = createPixiApp();
    }

    return app;
}

function createPixiApp() {
    const app = new Application({
        resizeTo: window,
        backgroundAlpha: 0,
        resolution: window.devicePixelRatio || 1,
    });

    createPixiOverlay(app);
    return app;
}

/** Sets up the pixi canvas element into the page */
function createPixiOverlay(app: Application) {
    const pixiOverlay = document.createElement(HTMLElements.div);
    pixiOverlay.classList.add("pixi-overlay");
    pixiOverlay.appendChild(app.view);
    document.getElementById("pixi-root")?.appendChild(pixiOverlay);
}

