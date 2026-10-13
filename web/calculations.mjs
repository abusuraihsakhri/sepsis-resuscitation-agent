/**
 * Unit-explicit, educational calculations for synthetic adult examples.
 * These arithmetic helpers cannot assess sepsis, determine eligibility for
 * fluid therapy, prescribe a treatment, or establish bundle compliance.
 */
const CONTEXTS = new Set(["shock", "probable", "possible", "unspecified"]);

function finiteNumber(name, value, { min = 0, max = Infinity, positive = false } = {}) {
  if (typeof value !== "number" || !Number.isFinite(value) ||
      value < min || value > max || (positive && value === 0)) {
    throw new RangeError(`${name} must be a finite number within the permitted range.`);
  }
  return value;
}

export function evaluateSyntheticScenario(input) {
  const { context, weightKg, crystalloidMl, initialLactate, repeatLactate,
    mapMmHg, elapsedMinutes, antibioticMinutes = null } = input;
  if (!CONTEXTS.has(context)) throw new RangeError("Choose a valid scenario category.");
  finiteNumber("Weight (kg)", weightKg, { min: 1, max: 500 });
  finiteNumber("Crystalloid (mL)", crystalloidMl, { min: 0, max: 30000 });
  finiteNumber("Initial lactate (mmol/L)", initialLactate, { min: 0, max: 50, positive: true });
  finiteNumber("Repeat lactate (mmol/L)", repeatLactate, { min: 0, max: 50 });
  finiteNumber("MAP (mmHg)", mapMmHg, { min: 0, max: 250 });
  finiteNumber("Elapsed minutes", elapsedMinutes, { min: 0, max: 10080 });
  if (antibioticMinutes !== null) {
    finiteNumber("Antibiotic minutes", antibioticMinutes, { min: 0, max: 10080 });
    if (antibioticMinutes > elapsedMinutes) {
      throw new RangeError("Recorded antibiotic time cannot be later than the elapsed scenario time.");
    }
  }

  const fluidReferenceMl = weightKg * 30;
  const lactateChangePercent = ((initialLactate - repeatLactate) / initialLactate) * 100;
  // 2026 SSC guidance differs by clinical likelihood and presence of shock.
  // These are timing reference windows, NOT automated patient care decisions.
  const antimicrobialReferenceMinutes =
    context === "shock" || context === "probable" ? 60 :
    context === "possible" ? 180 : null;

  return {
    weightKg, crystalloidMl, initialLactate, repeatLactate, mapMmHg,
    elapsedMinutes, antibioticMinutes, context,
    fluidReferenceMl,
    fluidReferencePercent: (crystalloidMl / fluidReferenceMl) * 100,
    lactateChangePercent,
    antimicrobialReferenceMinutes,
    antimicrobialElapsedVsReferenceMinutes:
      antibioticMinutes === null || antimicrobialReferenceMinutes === null
        ? null : antibioticMinutes - antimicrobialReferenceMinutes,
    note: "Arithmetic only. Not a diagnosis, resuscitation recommendation, or clinical compliance verdict."
  };
}
