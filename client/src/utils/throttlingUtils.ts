export function throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
): (...args: Parameters<T>) => void {
    let inThrottle = false;

    return function (this: any, ...args: Parameters<T>) {
        if (inThrottle)
            return;

        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => {
            inThrottle = false;
        }, limit);

    };
}