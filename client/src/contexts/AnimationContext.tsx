import { createContext, ReactNode } from "react";

interface AnimationContextObject {
    animationOngoing: boolean;
    setAnimationOngoing: (animationOngoing: boolean) => void;
    addEndOfAnimationCallback: (callback: () => void) => void;
}

export const AnimationContext = createContext<AnimationContextObject>({
    animationOngoing: false,
    setAnimationOngoing: () => { },
    addEndOfAnimationCallback: () => { }
});

interface AnimationContextProviderProps {
    children?: ReactNode;
}

export default function AnimationContextProvider(props: AnimationContextProviderProps) {

}