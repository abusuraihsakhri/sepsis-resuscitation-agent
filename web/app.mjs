import { evaluateSyntheticScenario } from "./calculations.mjs";

const form = document.getElementById("scenario-form");
const output = document.getElementById("result-output");
const status = document.getElementById("status-message");
const download = document.getElementById("download-button");
let lastResult = null;

const n = (id) => {
  const element = document.getElementById(id);
  if (element.value.trim() === "") throw new RangeError(`Enter ${element.dataset.label}.`);
  return Number(element.value);
};
const optionalNumber = (id) => {
  const value = document.getElementById(id).value.trim();
  return value === "" ? null : Number(value);
};
const fmt = (value, digits = 1) => Number(value).toFixed(digits);

function showSummary(data) {
  const timing = data.antibioticMinutes === null ? "No antimicrobial administration time was supplied."
    : data.antimicrobialReferenceMinutes === null ? "No reference interval applies to the unspecified context."
    : `Recorded antimicrobial interval: ${fmt(data.antibioticMinutes, 0)} min; ${fmt(data.antimicrobialReferenceMinutes, 0)} min is the context-specific guideline reference. This comparison alone does not establish compliance.`;
  const map = data.context === "shock"
    ? "2026 SSC suggests an initial MAP target of 65 mmHg for adult septic shock; clinical context, including age, may change the appropriate range."
    : "An MAP value alone cannot determine shock or direct vasopressor treatment.";
  output.textContent = [
    "SYNTHETIC SCENARIO SUMMARY",
    "--------------------------",
    `Lactate change: ${fmt(data.lactateChangePercent)}% (positive indicates a decrease)`,
    `Reference 30 mL/kg volume: ${fmt(data.fluidReferenceMl, 0)} mL`,
    `Documented fluid / reference: ${fmt(data.fluidReferencePercent)}%`,
    `Recorded MAP: ${fmt(data.mapMmHg, 0)} mmHg`,
    `Time since assumed recognition: ${fmt(data.elapsedMinutes, 0)} min`,
    timing,
    map,
    "",
    "Reference volume applies only to adult sepsis-induced hypoperfusion / shock;",
    "it is conditional and requires repeated individualized reassessment.",
    "Lactate trends require clinical interpretation; normalization is not",
    "a stand-alone endpoint for more fluids.",
    "",
    data.note
  ].join("\n");
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  try {
    const result = evaluateSyntheticScenario({
      context: document.getElementById("context").value,
      weightKg: n("weight"),
      crystalloidMl: n("fluid"),
      initialLactate: n("lactate-initial"),
      repeatLactate: n("lactate-repeat"),
      mapMmHg: n("map"),
      elapsedMinutes: n("elapsed"),
      antibioticMinutes: optionalNumber("antibiotic")
    });
    lastResult = result;
    showSummary(result);
    status.textContent = "Calculated locally. No scenario information was uploaded.";
    download.disabled = false;
  } catch (error) {
    lastResult = null;
    download.disabled = true;
    output.textContent = "Unable to calculate: " + error.message;
    status.textContent = "Check the inputs and try again.";
  }
});

download.addEventListener("click", () => {
  if (!lastResult) return;
  const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "synthetic-sepsis-example.json";
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
