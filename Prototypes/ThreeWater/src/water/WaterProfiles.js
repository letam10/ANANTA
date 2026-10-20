const LOW_PROFILE = Object.freeze({
  id: "low",
  label: "calm swell",
  amplitudeScale: 1.0,
  steepnessScale: 1.0,
  foamScale: 1.0,
  detailStrength: 0.3,
  detailScale: 0.09,
  detailSpeed: 0.42,
  fresnelPower: 5.0,
  reflectionStrength: 0.64,
  specularStrength: 0.42,
  horizonStrength: 0.32,
  subsurfaceStrength: 0.12,
  crestFoamStrength: 0.25,
  foldingFoamStrength: 0.36,
});

const STORM_PROFILE = Object.freeze({
  ...LOW_PROFILE,
  id: "storm",
  label: "storm swell",
  amplitudeScale: 3.4,
  steepnessScale: 1.18,
  foamScale: 1.55,
  detailStrength: 0.42,
  detailScale: 0.14,
  detailSpeed: 0.58,
  reflectionStrength: 0.72,
  specularStrength: 0.5,
  horizonStrength: 0.4,
  subsurfaceStrength: 0.18,
  crestFoamStrength: 0.42,
  foldingFoamStrength: 0.56,
});

export const WATER_PROFILES = Object.freeze({
  low: LOW_PROFILE,
  storm: STORM_PROFILE,
});

export function getWaterProfile(profileId = "low") {
  return WATER_PROFILES[profileId] || LOW_PROFILE;
}
