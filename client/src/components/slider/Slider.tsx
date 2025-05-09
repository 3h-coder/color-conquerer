import { useState } from "react";
import { ContainerProps } from "../containers";
import "./Slider.css";
import { SliderContext } from "./SliderContext";

interface SliderProps {
    slidesContent: JSX.Element[];
}

export default function Slider(props: SliderProps) {
    const { slidesContent } = props;
    const minIndex = 0;
    const maxIndex = Math.max(slidesContent.length - 1, minIndex);

    const [currentSlideIndex, setCurrentSlideIndex] = useState(minIndex);

    function nextSlide() {
        if (currentSlideIndex === maxIndex)
            return;
        setCurrentSlideIndex(currentSlideIndex + 1);
    }

    function previousSlide() {
        if (currentSlideIndex === minIndex)
            return;
        setCurrentSlideIndex(currentSlideIndex - 1);
    }

    const [goingNext, setGoingNext] = useState(true);
    function nextOrPreviousSlide() {
        if (goingNext) {
            if (currentSlideIndex < maxIndex)
                nextSlide();
            else {
                setGoingNext(false);
                previousSlide();
            }
        } else {
            if (currentSlideIndex > minIndex)
                previousSlide();
            else {
                setGoingNext(true);
                nextSlide();
            }
        }
    }

    const slideTransform = `translateX(-${currentSlideIndex * 100}%)`;

    return (
        <SliderContext.Provider value={{ nextOrPreviousSlide, currentSlideIndex }}>
            <OverflowWrapper>
                <SlidesContainer style={{ transform: slideTransform }}>
                    {slidesContent &&
                        slidesContent.map((slide, index) => (
                            <SlideContainer key={index}>
                                {slide}
                            </SlideContainer>
                        ))}
                </SlidesContainer>
            </OverflowWrapper>
        </SliderContext.Provider>
    );
}

function OverflowWrapper(props: ContainerProps) {
    return (
        <div className="slider-overflow-wrapper">
            {props.children}
        </div>
    );
}

function SlidesContainer(props: ContainerProps) {
    return (
        <div className="slider-slides-container" style={props.style}>
            {props.children}
        </div>
    );
}

function SlideContainer(props: ContainerProps) {
    return (
        <div className="slider-slide-container">
            {props.children}
        </div>
    );
}