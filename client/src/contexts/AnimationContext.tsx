/* eslint-disable react-refresh/only-export-components */
import { createContext, ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";
import { pixiApp } from "../env";
import { developmentLog } from "../utils/loggingUtils";

interface AnimationContextObject {
    getAnimationOngoing: () => boolean;
    signalAnimationStart: (startPixi?: boolean) => void;
    signalAnimationEnd: (stopPixi?: boolean) => void;
    addEndOfAnimationCallback: (callback: () => void | Promise<void>) => void;
}

export const AnimationContext = createContext<AnimationContextObject>({
    getAnimationOngoing: () => false,
    signalAnimationStart: () => { },
    signalAnimationEnd: () => { },
    addEndOfAnimationCallback: () => { }
});

interface AnimationContextProviderProps {
    children?: ReactNode;
}

export default function AnimationContextProvider({ children }: AnimationContextProviderProps) {
    // Use a ref for the actual value, and state only to trigger re-renders
    const animationOngoingRef = useRef(false);
    const [, forceRender] = useState(0); // dummy state to force re-render
    const [callbacks, setCallbacks] = useState<(() => void | Promise<void>)[]>([]);
    const prevAnimationOngoing = useRef(animationOngoingRef.current);

    const signalAnimationStart = useCallback((startPixi: boolean = false) => {
        if (startPixi)
            pixiApp.start();
        animationOngoingRef.current = true;
        forceRender(n => n + 1);
    }, []);

    const signalAnimationEnd = useCallback((stopPixi: boolean = false) => {
        if (stopPixi)
            pixiApp.stop();
        animationOngoingRef.current = false;
        forceRender(n => n + 1);
    }, []);

    const addEndOfAnimationCallback = useCallback((callback: () => void | Promise<void>) => {
        developmentLog("Adding end of animation callback", callback);
        setCallbacks(prev => [...prev, callback]);
    }, []);

    useEffect(() => {
        // Only process callbacks when animationOngoing transitions from true to false
        if (prevAnimationOngoing.current && !animationOngoingRef.current) {
            processCallbacks();
        }
        prevAnimationOngoing.current = animationOngoingRef.current;
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [animationOngoingRef.current]); // triggers when forceRender is called

    const contextValue: AnimationContextObject = {
        getAnimationOngoing: () => animationOngoingRef.current,
        signalAnimationStart,
        signalAnimationEnd,
        addEndOfAnimationCallback
    };

    async function processCallbacks() {
        if (callbacks.length > 0) {
            for (const callback of callbacks) {
                await callback();
            }
            setCallbacks([]);
        }
    }

    return (
        <AnimationContext.Provider value={contextValue}>
            {children}
        </AnimationContext.Provider>
    );
}

export function useAnimationContext() {
    return useContext(AnimationContext);
}