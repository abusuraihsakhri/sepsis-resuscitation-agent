import test from "node:test";
import assert from "node:assert/strict";
import { evaluateSyntheticScenario } from "./calculations.mjs";

const example = () => ({
  context: "shock", weightKg: 70, crystalloidMl: 1050,
  initialLactate: 4, repeatLactate: 3, mapMmHg: 64,
  elapsedMinutes: 100, antibioticMinutes: 55
});

test("computes lactate decrement and conditional reference volume", () => {
  const result = evaluateSyntheticScenario(example());
  assert.equal(result.lactateChangePercent, 25);
  assert.equal(result.fluidReferenceMl, 2100);
  assert.equal(result.fluidReferencePercent, 50);
  assert.equal(result.antimicrobialReferenceMinutes, 60);
  assert.equal(result.antimicrobialElapsedVsReferenceMinutes, -5);
});

test("changes context-specific timing reference", () => {
  assert.equal(evaluateSyntheticScenario({...example(), context: "possible"}).antimicrobialReferenceMinutes, 180);
  assert.equal(evaluateSyntheticScenario({...example(), context: "unspecified"}).antimicrobialReferenceMinutes, null);
  assert.equal(evaluateSyntheticScenario({...example(), antibioticMinutes: null}).antimicrobialElapsedVsReferenceMinutes, null);
});

test("preserves upward lactate change sign", () => {
  assert.equal(evaluateSyntheticScenario({...example(), initialLactate: 2, repeatLactate: 3}).lactateChangePercent, -50);
});

test("rejects missing, nonfinite and impossible synthetic measurements", () => {
  for (const change of [
    { initialLactate: 0 }, { weightKg: -1 }, { mapMmHg: Infinity },
    { crystalloidMl: NaN }, { antibioticMinutes: 101 }, { context: "unknown" }
  ]) {
    assert.throws(() => evaluateSyntheticScenario({...example(), ...change}), RangeError);
  }
});
