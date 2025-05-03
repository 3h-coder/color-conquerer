/* eslint-disable react-refresh/only-export-components */
import { createContext, ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";

interface AnimationContextObject {
    animationOngoing: boolean;
    signalAnimationStart: () => void;
    signalAnimationEnd: () => void;
    addEndOfAnimationCallback: (callback: () => void) => void;
}

export const AnimationContext = createContext<AnimationContextObject>({
    animationOngoing: false,
    signalAnimationStart: () => { },
    signalAnimationEnd: () => { },
    addEndOfAnimationCallback: () => { }
});

interface AnimationContextProviderProps {
    children?: ReactNode;
}

export default function AnimationContextProvider({ children }: AnimationContextProviderProps) {
    const [animationOngoing, setAnimationOngoing] = useState(false);
    const [callbacks, setCallbacks] = useState<(() => void)[]>([]);
    const prevAnimationOngoing = useRef(animationOngoing);

    const signalAnimationStart = useCallback(() => {
        setAnimationOngoing(true);
    }, []);

    const signalAnimationEnd = useCallback(() => {
        setAnimationOngoing(false);
    }, []);

    const addEndOfAnimationCallback = useCallback((callback: () => void) => {
        setCallbacks(prev => [...prev, callback]);
    }, []);

    useEffect(() => {
        // Only process callbacks when animationOngoing transitions from true to false
        if (prevAnimationOngoing.current && !animationOngoing) {
            processCallbacks();
        }
        prevAnimationOngoing.current = animationOngoing;
    }, [animationOngoing]);

    const contextValue: AnimationContextObject = {
        animationOngoing,
        signalAnimationStart,
        signalAnimationEnd,
        addEndOfAnimationCallback
    };

    function processCallbacks() {
        if (callbacks.length > 0) {
            callbacks.forEach(callback => callback());
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