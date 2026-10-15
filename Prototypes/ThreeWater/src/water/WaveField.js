const TAU = Math.PI * 2;
const MIN_WAVELENGTH = 1e-6;
const DEFAULT_DIRECTION = [1, 0];
const DEFAULT_WAVELENGTH = 12;
const DEFAULT_AMPLITUDE = 0;
const DEFAULT_SPEED = 0;
const DEFAULT_PHASE_OFFSET = 0;

export const LOW_WAVE_PRESET = Object.freeze([
    Object.freeze({
        direction: Object.freeze([1, 0.25]),
        wavelength: 28,
        amplitude: 0.2,
        speed: 1.6,
        phaseOffset: 0
    }),
    Object.freeze({
        direction: Object.freeze([-0.7, 1]),
        wavelength: 45,
        amplitude: 0.12,
        speed: 1.1,
        phaseOffset: 1.4
    }),
    Object.freeze({
        direction: Object.freeze([0.35, 0.94]),
        wavelength: 72,
        amplitude: 0.06,
        speed: 0.75,
        phaseOffset: 2.2
    }),
    Object.freeze({
        direction: Object.freeze([-1, -0.2]),
        wavelength: 120,
        amplitude: 0.03,
        speed: 0.45,
        phaseOffset: 3.1
    })
]);

function finiteOr(value, fallback) {
    return Number.isFinite(value) ? value : fallback;
}
function normalizeDirection(direction) {
    const directionX = finiteOr(direction[0], DEFAULT_DIRECTION[0]);
    const directionZ = finiteOr(direction[1], DEFAULT_DIRECTION[1]);
    const magnitude = Math.hypot(directionX, directionZ);

    if (!Number.isFinite(magnitude) || magnitude < Number.EPSILON) {
        return [...DEFAULT_DIRECTION];
    }

    return [directionX / magnitude, directionZ / magnitude];
}

function sanitizeWave(wave) {
    const source = wave && typeof wave === "object" ? wave : {};
    const sourceDirection = Array.isArray(source.direction)
        ? source.direction
        : DEFAULT_DIRECTION;
    const direction = normalizeDirection(sourceDirection);
    const rawWavelength = finiteOr(source.wavelength, DEFAULT_WAVELENGTH);
    const wavelength = Math.max(MIN_WAVELENGTH, rawWavelength);
    const amplitude = finiteOr(source.amplitude, DEFAULT_AMPLITUDE);
    const speed = finiteOr(source.speed, DEFAULT_SPEED);
    const phaseOffset = finiteOr(source.phaseOffset, DEFAULT_PHASE_OFFSET);

    return {
        direction,
        wavelength,
        amplitude,
        speed,
        phaseOffset
    };
}

function sanitizeWaves(waves) {
    const source = Array.isArray(waves) ? waves : LOW_WAVE_PRESET;
    return source.map(sanitizeWave);
}

function copyWaves(waves) {
    return waves.map((wave) => ({
        direction: [...wave.direction],
        wavelength: wave.wavelength,
        amplitude: wave.amplitude,
        speed: wave.speed,
        phaseOffset: wave.phaseOffset
    }));
}

export class WaveField {
    constructor(waves = LOW_WAVE_PRESET) {
        this._waves = sanitizeWaves(waves);
    }

    get waves() {
        return copyWaves(this._waves);
    }

    sampleHeightAndNormal(horizontalX, horizontalZ, timeSeconds) {
        const x = finiteOr(horizontalX, 0);
        const z = finiteOr(horizontalZ, 0);
        const time = finiteOr(timeSeconds, 0);
        let height = 0;
        let derivativeX = 0;
        let derivativeZ = 0;

        // Mặt nước dùng Y-up; tọa độ ngang XZ đi trực tiếp vào tích vô hướng.
        for (const wave of this._waves) {
            const dot = wave.direction[0] * x + wave.direction[1] * z;
            const phaseArgument = dot / wave.wavelength
                - wave.speed * time / wave.wavelength;
            const phase = TAU * phaseArgument + wave.phaseOffset;
            const safePhase = finiteOr(phase, 0);
            const sine = Math.sin(safePhase);
            const cosine = Math.cos(safePhase);
            const heightContribution = wave.amplitude * sine;
            const derivativeScale = wave.amplitude * TAU * cosine / wave.wavelength;

            if (Number.isFinite(heightContribution)) {
                height += heightContribution;
            }

            if (Number.isFinite(derivativeScale)) {
                derivativeX += derivativeScale * wave.direction[0];
                derivativeZ += derivativeScale * wave.direction[1];
            }
        }

        height = finiteOr(height, 0);
        derivativeX = finiteOr(derivativeX, 0);
        derivativeZ = finiteOr(derivativeZ, 0);

        const normalLength = Math.hypot(derivativeX, 1, derivativeZ);
        const safeNormalLength = Number.isFinite(normalLength) && normalLength > 0
            ? normalLength
            : 1;

        return {
            height,
            normal: {
                x: -derivativeX / safeNormalLength,
                y: 1 / safeNormalLength,
                z: -derivativeZ / safeNormalLength
            }
        };
    }

    getShaderWaveData() {
        return copyWaves(this._waves);
    }
}
