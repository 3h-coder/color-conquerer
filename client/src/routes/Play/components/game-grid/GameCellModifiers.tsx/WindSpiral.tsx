export function WindSpiral() {
    const trailCount = 50; // Number of trail elements
    const trailElements = Array.from({ length: trailCount }, (_, index) => {
        const delay = `${index * 0.006}s`; // Staggered animation delay
        const opacity = 1 - index * 0.1; // Gradually decrease opacity

        return (
            <div
                key={index}
                className="wind-spiral-trail"
                style={{
                    animationDelay: delay,
                    opacity: opacity,
                }}
            />
        );
    });

    return (
        <div className="wind-spiral">
            {trailElements}
        </div>
    );
}