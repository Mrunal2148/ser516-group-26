import '@testing-library/jest-dom';

class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
}
global.ResizeObserver = ResizeObserver;

HTMLCanvasElement.prototype.getContext = () => {
    return {
        fillRect: () => {},
        clearRect: () => {},
        getImageData: () => ({ data: [] }),
        putImageData: () => {},
        createImageData: () => [],
        setTransform: () => {},
        drawImage: () => {},
        save: () => {},
        fillText: () => {},
        restore: () => {},
        beginPath: () => {},
        moveTo: () => {},
        lineTo: () => {},
        closePath: () => {},
        stroke: () => {},
        translate: () => {},
        scale: () => {},
        rotate: () => {},
        arc: () => {},
        fill: () => {},
        measureText: () => ({ width: 0 }),
        transform: () => {},
        rect: () => {},
        clip: () => {},
    };
};