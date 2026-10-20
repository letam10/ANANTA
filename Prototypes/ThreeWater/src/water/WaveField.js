const TAU = Math.PI * 2;
const MIN_WAVELENGTH = 1e-6;
const DEFAULT_DIRECTION = [1, 0];
const DEFAULT_WAVELENGTH = 12;
const DEFAULT_AMPLITUDE = 0;
const DEFAULT_SPEED = 0;
const DEFAULT_PHASE_OFFSET = 0;
const DEFAULT_STEEPNESS = 0.22;

export const GEOMETRIC_STEEPNESS = Object.freeze([0.38, 0.31, 0.22, 0.14]);

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

function sanitizeWave(wave, index = 0) {
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
    const steepness = Math.max(
        0,
        Math.min(
            0.95,
            finiteOr(source.steepness, GEOMETRIC_STEEPNESS[index] ?? DEFAULT_STEEPNESS),
        ),
    );

    return {
        direction,
        wavelength,
        amplitude,
        speed,
        phaseOffset,
        steepness,
    };
}

function sanitizeWaves(waves) {
    const source = Array.isArray(waves) ? waves : LOW_WAVE_PRESET;
    return source.map((wave, index) => sanitizeWave(wave, index));
}

function copyWaves(waves) {
    return waves.map((wave) => ({
        direction: [...wave.direction],
        wavelength: wave.wavelength,
        amplitude: wave.amplitude,
        speed: wave.speed,
        phaseOffset: wave.phaseOffset,
        steepness: wave.steepness,
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

    sampleGerstnerPositionAndNormal(horizontalX, horizontalZ, timeSeconds, profile = {}) {
        const x = finiteOr(horizontalX, 0);
        const z = finiteOr(horizontalZ, 0);
        const time = finiteOr(timeSeconds, 0);
        const visualProfile = profile && typeof profile === "object" ? profile : {};
        const amplitudeScale = Math.max(finiteOr(visualProfile.amplitudeScale, 1), 0);
        const speedScale = Math.max(finiteOr(visualProfile.speedScale, 1), 0);
        const steepnessScale = Math.max(finiteOr(visualProfile.steepnessScale, 1), 0);
        let positionX = x;
        let positionZ = z;
        let height = 0;
        let tangentX = { x: 1, y: 0, z: 0 };
        let tangentZ = { x: 0, y: 0, z: 1 };
        const waveCount = Math.max(this._waves.length, 1);

        for (const wave of this._waves) {
            const directionX = wave.direction[0];
            const directionZ = wave.direction[1];
            const amplitude = wave.amplitude * amplitudeScale;
            const wavelength = Math.max(wave.wavelength, MIN_WAVELENGTH);
            const frequency = TAU / wavelength;
            const speed = wave.speed * speedScale;
            const steepness = Math.min(0.95, wave.steepness * steepnessScale);
            const phase = TAU * (
                (directionX * x + directionZ * z) / wavelength
                - speed * time / wavelength
            ) + wave.phaseOffset;
            const sine = Math.sin(phase);
            const cosine = Math.cos(phase);
            const q = steepness / Math.max(
                frequency * Math.max(Math.abs(amplitude), MIN_WAVELENGTH) * waveCount,
                MIN_WAVELENGTH,
            );
            const lateral = q * amplitude * cosine;
            const slope = amplitude * frequency * cosine;
            const crest = q * amplitude * frequency * sine;

            positionX += directionX * lateral;
            positionZ += directionZ * lateral;
            height += amplitude * sine;
            tangentX = {
                x: tangentX.x - directionX * directionX * crest,
                y: tangentX.y + directionX * slope,
                z: tangentX.z - directionX * directionZ * crest,
            };
            tangentZ = {
                x: tangentZ.x - directionX * directionZ * crest,
                y: tangentZ.y + directionZ * slope,
                z: tangentZ.z - directionZ * directionZ * crest,
            };
        }

        const normalX = tangentZ.y * tangentX.z - tangentZ.z * tangentX.y;
        const normalY = tangentZ.z * tangentX.x - tangentZ.x * tangentX.z;
        const normalZ = tangentZ.x * tangentX.y - tangentZ.y * tangentX.x;
        const normalLength = Math.hypot(normalX, normalY, normalZ);
        const safeLength = Number.isFinite(normalLength) && normalLength > 0
            ? normalLength
            : 1;

        return {
            position: {
                x: finiteOr(positionX, x),
                y: finiteOr(height, 0),
                z: finiteOr(positionZ, z),
            },
            normal: {
                x: normalX / safeLength,
                y: normalY / safeLength,
                z: normalZ / safeLength,
            },
        };
    }

    getShaderWaveData() {
        return copyWaves(this._waves);
    }
}
