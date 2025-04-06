export function throttle<T extends (...args: unknown[]) => unknown>(
    func: T,
    limit: number
): (...args: Parameters<T>) => void {
    let inThrottle = false;

    return function (this: unknown, ...args: Parameters<T>) {
        if (inThrottle)
            return;

        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => {
            inThrottle = false;
        }, limit);

    };
}