import { WaveField } from "../water/WaveField.js";
import { CoastBoundary } from "../water/CoastBoundary.js";
import { SCENE_PRESETS, applyScenePreset, getScenePreset } from "./ScenePresets.js";

const DIFFERENCE_EPSILON = 1e-3;
const NORMAL_TOLERANCE = 1e-5;
const HEIGHT_TOLERANCE = 1e-12;
const BOUNDARY_TOLERANCE = 1e-9;
const REQUIRED_SCENES = ["coast", "beach_boat", "offshore"];

function assert(condition, message) {
    if (!condition) {
        throw new Error(message);
    }
}

function equalArray(actual, expected, label) {
    assert(Array.isArray(actual), `${label}: expected an array`);
    assert(actual.length === expected.length, `${label}: length ${actual.length} !== ${expected.length}`);
    actual.forEach((value, index) => {
        assert(value === expected[index], `${label}[${index}]: ${value} !== ${expected[index]}`);
    });
}

function near(actual, expected, tolerance, label) {
    assert(Number.isFinite(actual), `${label}: non-finite result ${actual}`);
    assert(Math.abs(actual - expected) <= tolerance,
        `${label}: ${actual} differs from ${expected}, tolerance ${tolerance}`);
}

function vectorRecorder() {
    return {
        values: null,
        set(x, y, z) {
            this.values = [x, y, z];
        },
    };
}

export function runWaterContractChecks(spec) {
    const checks = [];
    const errors = [];
    function check(name, operation) {
        try {
            operation();
            checks.push({ name, passed: true });
        } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            checks.push({ name, passed: false, error: message });
            errors.push(`${name}: ${message}`);
        }
    }

    check("spec.structure", () => {
        assert(spec && typeof spec === "object", "spec must be an object");
        assert(spec.schema === "ananta.three-water.wave-spec.v2", `unsupported schema ${spec.schema}`);
        assert(spec.schemaVersion === "2.0.0", `unsupported schemaVersion ${spec.schemaVersion}`);
        assert(spec.units?.distance === "meters", "distance must use meters");
        assert(spec.units?.time === "seconds", "time must use seconds");
        assert(spec.units?.phase === "radians", "phase must use radians");
        assert(Array.isArray(spec.waves) && spec.waves.length === 4, "exactly four waves are required");
        assert(spec.presetQuality?.maxWaves === 4, "low preset maxWaves must equal four");
        assert(spec.presetQuality?.cpuMeshRebuild === false, "low preset must disable CPU mesh rebuilds");
        assert(Array.isArray(spec.scenes), "scenes must be an array");
        assert(spec.boundary && typeof spec.boundary === "object", "boundary is required");
    });
    if (!checks[0].passed) {
        return { passed: false, checks, errors };
    }

    check("waves.input-tuples", () => {
        spec.waves.forEach((wave, index) => {
            assert(Array.isArray(wave.direction) && wave.direction.length === 2,
                `wave ${index}: direction must contain two components`);
            assert(wave.direction.every(Number.isFinite), `wave ${index}: direction must be finite`);
            assert(Math.hypot(...wave.direction) > 0, `wave ${index}: direction cannot be zero`);
            ["wavelength", "amplitude", "speed", "phase"].forEach((key) => {
                assert(Number.isFinite(wave[key]), `wave ${index}: ${key} must be finite`);
            });
            assert(wave.wavelength > 0, `wave ${index}: wavelength must be positive`);
        });
    });
    if (checks[checks.length - 1].passed) {
        const waveField = new WaveField(spec.waves.map((wave) => ({
            direction: [...wave.direction],
            wavelength: wave.wavelength,
            amplitude: wave.amplitude,
            speed: wave.speed,
            phaseOffset: wave.phase,
        })));
        check("waves.cpu-and-shader-tuples", () => {
            const outputs = [waveField.waves, waveField.getShaderWaveData()];
            outputs.forEach((waves, outputIndex) => {
                assert(waves.length === spec.waves.length, `output ${outputIndex}: wave count changed`);
                waves.forEach((wave, index) => {
                    const source = spec.waves[index];
                    const length = Math.hypot(...source.direction);
                    equalArray(wave.direction, source.direction.map((value) => value / length),
                        `output ${outputIndex} wave ${index} normalized direction`);
                    ["wavelength", "amplitude", "speed"].forEach((key) => {
                        assert(wave[key] === source[key], `output ${outputIndex} wave ${index}: ${key} changed`);
                    });
                    assert(wave.phaseOffset === source.phase, `output ${outputIndex} wave ${index}: phase changed`);
                });
            });
        });

        const samples = [
            [0, 0, 0],
            [19.25, -37.5, 0.75],
            [-91.125, 41.75, 3.2],
            [-257.75, -143.25, 9.5],
            [612.4, 321.8, 20],
            [44.8, -301.6, -2.25],
            [-699.5, 399.5, 30.125],
        ];
        samples.forEach(([x, z, time], index) => {
            check(`waves.height-and-normal.${index}`, () => {
                const actual = waveField.sampleHeightAndNormal(x, z, time);
                let expectedHeight = 0;
                spec.waves.forEach((wave) => {
                    const length = Math.hypot(...wave.direction);
                    const dot = (wave.direction[0] * x + wave.direction[1] * z) / length;
                    const phase = 2 * Math.PI * (dot - wave.speed * time) / wave.wavelength + wave.phase;
                    expectedHeight += wave.amplitude * Math.sin(phase);
                });
                near(actual.height, expectedHeight, HEIGHT_TOLERANCE, "height from contract phase");
                // Sai phân trung tâm trên chính height CPU để bắt lỗi trục và dấu đạo hàm.
                const derivativeX = (waveField.sampleHeightAndNormal(x + DIFFERENCE_EPSILON, z, time).height
                    - waveField.sampleHeightAndNormal(x - DIFFERENCE_EPSILON, z, time).height)
                    / (2 * DIFFERENCE_EPSILON);
                const derivativeZ = (waveField.sampleHeightAndNormal(x, z + DIFFERENCE_EPSILON, time).height
                    - waveField.sampleHeightAndNormal(x, z - DIFFERENCE_EPSILON, time).height)
                    / (2 * DIFFERENCE_EPSILON);
                const length = Math.hypot(derivativeX, 1, derivativeZ);
                near(actual.normal.x, -derivativeX / length, NORMAL_TOLERANCE, "normal.x");
                near(actual.normal.y, 1 / length, NORMAL_TOLERANCE, "normal.y");
                near(actual.normal.z, -derivativeZ / length, NORMAL_TOLERANCE, "normal.z");
                near(Math.hypot(actual.normal.x, actual.normal.y, actual.normal.z), 1,
                    NORMAL_TOLERANCE, "unit normal length");
            });
        });
        check("waves.gerstner-visual-position-and-normal", () => {
            const sample = waveField.sampleGerstnerPositionAndNormal(19.25, -37.5, 0.75);
            [sample.position.x, sample.position.y, sample.position.z,
                sample.normal.x, sample.normal.y, sample.normal.z].forEach((value) => {
                assert(Number.isFinite(value), `Gerstner sample is non-finite: ${value}`);
            });
            near(Math.hypot(sample.normal.x, sample.normal.y, sample.normal.z), 1,
                NORMAL_TOLERANCE, "Gerstner normal length");
            assert(sample.position.x !== 19.25 || sample.position.z !== -37.5,
                "Gerstner sample did not provide lateral displacement");
        });
        check("waves.storm-profile-synchronizes", () => {
            const calm = waveField.sampleGerstnerPositionAndNormal(19.25, -37.5, 0.75);
            const storm = waveField.sampleGerstnerPositionAndNormal(19.25, -37.5, 0.75, {
                amplitudeScale: 3.4,
                steepnessScale: 1.18,
            });
            [storm.position.x, storm.position.y, storm.position.z,
                storm.normal.x, storm.normal.y, storm.normal.z].forEach((value) => {
                assert(Number.isFinite(value), `storm Gerstner sample is non-finite: ${value}`);
            });
            assert(Math.abs(storm.position.y - calm.position.y) > DIFFERENCE_EPSILON,
                "storm profile did not change vertical displacement");
            assert(storm.position.x !== calm.position.x || storm.position.z !== calm.position.z,
                "storm profile did not preserve synchronized lateral displacement");
            near(Math.hypot(storm.normal.x, storm.normal.y, storm.normal.z), 1,
                NORMAL_TOLERANCE, "storm Gerstner normal length");
        });
    }

    check("scenes.identity", () => {
        equalArray(spec.scenes.map((scene) => scene.id), REQUIRED_SCENES, "spec scene IDs");
        equalArray(Object.keys(SCENE_PRESETS), REQUIRED_SCENES, "exported scene IDs");
    });
    spec.scenes.forEach((scene) => {
        check(`scenes.${scene.id}.contract-and-application`, () => {
            const preset = getScenePreset(scene.id);
            assert(preset, `missing preset ${scene.id}`);
            assert(preset.id === scene.id, "preset ID differs from source");
            equalArray(preset.cameraPosition, scene.camera, "camera position");
            equalArray(preset.target, scene.target, "camera target");
            assert(scene.durationSeconds === 10, "each quick scene must last exactly 10 seconds");
            assert(preset.durationSeconds === scene.durationSeconds, "duration differs from source");
            let projectionUpdates = 0;
            let controlsUpdates = 0;
            const camera = {
                position: vectorRecorder(),
                lookTarget: null,
                lookAt(...values) {
                    this.lookTarget = values;
                },
                updateProjectionMatrix() {
                    projectionUpdates += 1;
                },
            };
            const controls = {
                target: vectorRecorder(),
                update() {
                    controlsUpdates += 1;
                },
            };
            const applied = applyScenePreset(camera, controls, scene.id);
            assert(applied === preset, "applyScenePreset returned another preset");
            equalArray(camera.position.values, scene.camera, "applied camera position");
            equalArray(camera.lookTarget, scene.target, "applied lookAt target");
            equalArray(controls.target.values, scene.target, "applied orbit target");
            assert(projectionUpdates === 1 && controlsUpdates === 1, "camera/controls were not updated once");
        });
    });

    check("boundary.input", () => {
        const boundary = spec.boundary;
        assert(boundary.type === "box", `this contract requires box, received ${boundary.type}`);
        ["minX", "maxX", "minZ", "maxZ", "cameraMargin", "boatMargin"].forEach((key) => {
            assert(Number.isFinite(boundary[key]), `${key} must be finite`);
        });
        assert(boundary.minX < boundary.maxX && boundary.minZ < boundary.maxZ, "bounds must be ordered");
        ["cameraMargin", "boatMargin"].forEach((key) => {
            assert(boundary[key] >= 0, `${key} must not be negative`);
            assert(2 * boundary[key] < Math.min(boundary.maxX - boundary.minX,
                boundary.maxZ - boundary.minZ), `${key} leaves no navigable area`);
        });
    });
    if (checks[checks.length - 1].passed) {
        const source = spec.boundary;
        const boundary = new CoastBoundary(source);
        check("boundary.bounds-readback", () => {
            ["minX", "maxX", "minZ", "maxZ"].forEach((key) => {
                assert(boundary.toJSON()[key] === source[key], `${key} differs from source`);
            });
        });
        const centerX = (source.minX + source.maxX) / 2;
        const centerZ = (source.minZ + source.maxZ) / 2;
        [0, source.cameraMargin, source.boatMargin].forEach((margin, marginIndex) => {
            const minX = source.minX + margin;
            const maxX = source.maxX - margin;
            const minZ = source.minZ + margin;
            const maxZ = source.maxZ - margin;
            const probes = [
                [centerX, centerZ],
                [minX, centerZ],
                [maxX, centerZ],
                [centerX, minZ],
                [centerX, maxZ],
                [minX, minZ],
                [minX, maxZ],
                [maxX, minZ],
                [maxX, maxZ],
                [source.minX - 20, centerZ],
                [source.maxX + 20, centerZ],
                [centerX, source.minZ - 20],
                [centerX, source.maxZ + 20],
                [source.minX - 20, source.minZ - 20],
                [source.minX - 20, source.maxZ + 20],
                [source.maxX + 20, source.minZ - 20],
                [source.maxX + 20, source.maxZ + 20],
            ];
            probes.forEach(([x, z], probeIndex) => {
                check(`boundary.margin-${marginIndex}.probe-${probeIndex}`, () => {
                    const expectedInside = x >= minX && x <= maxX && z >= minZ && z <= maxZ;
                    assert(boundary.contains(x, z, margin) === expectedInside, "contains disagrees with box inset");
                    const expectedX = Math.min(maxX, Math.max(minX, x));
                    const expectedZ = Math.min(maxZ, Math.max(minZ, z));
                    const clamped = boundary.clamp(x, z, margin);
                    near(clamped.x, expectedX, BOUNDARY_TOLERANCE, "clamp.x");
                    near(clamped.z, expectedZ, BOUNDARY_TOLERANCE, "clamp.z");
                    assert(boundary.contains(clamped.x, clamped.z, margin), "clamp result violates margin");
                    const point = { x, y: 23, z };
                    const camera = boundary.resolveCamera(point, margin);
                    const boat = boundary.resolveBoat(point, margin);
                    [camera, boat].forEach((resolved, index) => {
                        near(resolved.x, expectedX, BOUNDARY_TOLERANCE, `resolver ${index}.x`);
                        near(resolved.z, expectedZ, BOUNDARY_TOLERANCE, `resolver ${index}.z`);
                        assert(resolved.y === point.y, `resolver ${index}: changed vertical position`);
                    });
                    assert(point.x === x && point.y === 23 && point.z === z, "resolver mutated the input point");
                });
            });
        });
        check("boundary.boat-default-margin", () => {
            const boat = boundary.resolveBoat({ x: source.minX - 1, y: 2, z: centerZ });
            near(boat.x, source.minX + source.boatMargin, BOUNDARY_TOLERANCE, "default boat margin");
            assert(boundary.contains(boat.x, boat.z, source.boatMargin), "boat escaped its default margin");
        });
    }

    return { passed: errors.length === 0, checks, errors };
}
