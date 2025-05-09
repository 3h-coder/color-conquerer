import { createContext, useContext } from "react";

interface SliderContextType {
    nextOrPreviousSlide: () => void;
    currentSlideIndex: number;
}

export const SliderContext = createContext<SliderContextType>({
    nextOrPreviousSlide: () => { },
    currentSlideIndex: 0
});

export function useSliderContext() {
    return useContext(SliderContext);
}