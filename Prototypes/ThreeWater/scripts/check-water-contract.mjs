import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { runWaterContractChecks } from "../src/qa/WaterContractChecks.js";

const specUrl = new URL("../public/wave-spec.json", import.meta.url);
const spec = JSON.parse(await readFile(specUrl, "utf8"));
const result = runWaterContractChecks(spec);
console.log(JSON.stringify({
  passed: result.passed,
  checks: result.checks.length,
  errors: result.errors,
}, null, 2));
assert.equal(result.passed, true, result.errors.join("\n"));

// Kiểm tra phải phát hiện camera sai, không chỉ đi qua bộ dữ liệu đang hợp lệ.
const changedCamera = structuredClone(spec);
changedCamera.scenes[1].target[0] += 8;
const negative = runWaterContractChecks(changedCamera);
assert.equal(negative.passed, false);
assert.ok(negative.errors.some((error) => error.includes("scenes.beach_boat")));
console.log("WATER_CONTRACT_CHECKS_OK negativeCameraDetected=true");
