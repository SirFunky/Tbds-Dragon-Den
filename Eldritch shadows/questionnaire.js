"use strict";

(() => {
  const form = document.getElementById("questionnaire");
  const status = document.getElementById("save-status");
  const storageKey = "eldritch-shadows-questionnaire-v1";
  const conditional = [...form.querySelectorAll("[data-when]")];
  const threatOptions = document.getElementById("q16-options");
  const reaction = form.querySelector(".reaction");
  let storageReadable = true;

  function selected(name) {
    return [...form.querySelectorAll(`input[name="${name}"]:checked`)].map(input => input.value);
  }

  function values() {
    const result = {};
    for (const field of form.querySelectorAll("[name]")) {
      if (field.disabled) continue;
      if (field.type === "checkbox" || field.type === "radio") {
        if (!result[field.name]) result[field.name] = [];
        if (field.checked) result[field.name].push(field.value);
      } else result[field.name] = field.value;
    }
    return result;
  }

  function resize() {
    for (const field of form.querySelectorAll("textarea")) {
      if (field.disabled) continue;
      field.style.height = "auto";
      field.style.height = `${field.scrollHeight + 2}px`;
    }
  }

  function update() {
    for (const box of conditional) {
      const visible = selected(box.dataset.when).includes(box.dataset.value);
      box.hidden = !visible;
      for (const field of box.querySelectorAll("textarea")) field.disabled = !visible;
    }
    const previous = selected("q16")[0];
    const classifications = selected("q15");
    const currentOptions = [...threatOptions.querySelectorAll("input")].map(input => input.value);
    const changed = JSON.stringify(classifications) !== JSON.stringify(currentOptions);
    if (changed) threatOptions.replaceChildren();
    for (const value of changed ? classifications : []) {
      const label = document.createElement("label");
      label.className = "choice";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = "q16";
      input.value = value;
      input.checked = previous === value;
      const span = document.createElement("span");
      span.textContent = value;
      label.append(input, span);
      threatOptions.append(label);
    }
    const none = threatOptions.childElementCount === 0;
    document.getElementById("q16-help").hidden = !none;
    reaction.disabled = none;
    if (none) for (const field of reaction.querySelectorAll("input")) field.checked = false;
    resize();
  }

  function apply(data) {
    if (!data || typeof data !== "object" || Array.isArray(data)) throw Error("Invalid saved answers");
    for (const value of Object.values(data)) {
      if (typeof value !== "string" && !(Array.isArray(value) && value.every(item => typeof item === "string"))) {
        throw Error("Invalid saved answer");
      }
    }
    const restore = () => {
      for (const field of form.querySelectorAll("[name]")) {
        const value = data[field.name];
        if (field.type === "checkbox" || field.type === "radio") field.checked = Array.isArray(value) && value.includes(field.value);
        else field.value = typeof value === "string" ? value : "";
      }
    };
    restore();
    update();
    restore(); // Q16 exists only after Q15's options have been restored.
    update();
  }

  function save() {
    if (!storageReadable) return;
    try {
      localStorage.setItem(storageKey, JSON.stringify(values()));
      status.textContent = "Answers saved in this browser. Download a copy to keep them outside this device.";
    } catch {
      status.textContent = "Browser saving is unavailable. Download your answers before leaving this page.";
    }
  }

  try {
    const saved = localStorage.getItem(storageKey);
    if (saved) apply(JSON.parse(saved));
    status.textContent = saved ? "Saved answers restored from this browser." : "Answers save automatically in this browser as you write.";
  } catch {
    storageReadable = false;
    status.textContent = "Saved answers could not be loaded. Existing browser data is unchanged; download your answers before leaving.";
  }
  update();
  form.addEventListener("submit", event => event.preventDefault());
  form.addEventListener("input", () => { resize(); save(); });
  form.addEventListener("change", () => { update(); save(); });
  window.addEventListener("resize", resize);
  window.addEventListener("beforeprint", resize);
  document.getElementById("print-answers").disabled = false;
  document.getElementById("print-answers").addEventListener("click", () => { resize(); window.print(); });
  document.getElementById("download-answers").disabled = false;
  document.getElementById("download-answers").addEventListener("click", () => {
    const data = values();
    const lines = ["ELDRITCH SHADOWS — GDA QUESTIONNAIRE", `Agent / character: ${data.agent_name || ""}`, `Campaign: ${data.campaign || ""}`, ""];
    for (const section of form.querySelectorAll("section")) {
      lines.push(section.querySelector("h2").textContent, "");
      for (const question of section.querySelectorAll(".question")) {
        lines.push(question.querySelector("legend").textContent.trim());
        const name = `q${question.id.split("-")[1]}`;
        const answer = data[name];
        lines.push((Array.isArray(answer) ? answer.join("; ") : answer) || "(Unanswered)");
        for (const suffix of ["_other", "_detail", "_reaction"]) {
          const detail = data[name + suffix];
          if (detail && (!Array.isArray(detail) || detail.length)) {
            const label = suffix === "_reaction" ? "Reaction" : suffix === "_other" ? "Other" : "Detail";
            lines.push(`${label}: ${Array.isArray(detail) ? detail.join("; ") : detail}`);
          }
        }
        lines.push("");
      }
    }
    const url = URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "eldritch-shadows-gda-answers.txt";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
})();
