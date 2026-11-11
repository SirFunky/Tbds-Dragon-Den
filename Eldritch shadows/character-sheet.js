"use strict";

(() => {
  const form = document.getElementById("character-sheet");
  const status = document.getElementById("save-status");
  const fields = Array.from(form.querySelectorAll("input[name], textarea[name]"));
  const characterId = form.dataset.characterId;
  const storageKey = characterId
    ? `eldritch-shadows-pregen-${characterId}-v1`
    : "eldritch-shadows-character-v1";
  const schema = "eldritch-shadows-character";
  const maxFileSize = 1024 * 1024;
  let saveTimer;

  function readValues() {
    return Object.fromEntries(fields.map(field => [field.name, field.type === "checkbox" ? field.checked : field.value]));
  }

  function resizeTextareas() {
    for (const field of fields) {
      if (field.tagName !== "TEXTAREA") continue;
      field.style.height = "auto";
      field.style.height = `${field.scrollHeight + 2}px`;
    }
  }

  function validateValues(values) {
    if (!values || typeof values !== "object" || Array.isArray(values)) throw new Error("Invalid fields");
    for (const field of fields) {
      if (!Object.prototype.hasOwnProperty.call(values, field.name)) continue;
      const value = values[field.name];
      if (field.type === "checkbox" ? typeof value !== "boolean" : typeof value !== "string" || value.length > 50000) {
        throw new Error("Invalid field value");
      }
    }
  }

  function applyValues(values) {
    validateValues(values);
    for (const field of fields) {
      if (field.type === "checkbox") field.checked = values[field.name] === true;
      else field.value = Object.prototype.hasOwnProperty.call(values, field.name) ? values[field.name] : "";
    }
    resizeTextareas();
  }

  function updatePregenDefaults(values) {
    if (!values || typeof values !== "object") return values;
    if (characterId === "emilia-olsson" && values.xp_earned === "0" && values.xp_spent === "0" &&
        values.attr_medicin_poang === "1" && values.attr_medicin_specialisering === "Triage" &&
        typeof values.campaign_notes === "string" && values.campaign_notes.includes("The printed Mage class grants 4 discipline points")) {
      values.attr_medicin_poang = "0";
      values.attr_medicin_specialisering = "";
      values.campaign_notes = values.campaign_notes.replace(
        "The printed Mage class grants 4 discipline points, while custom creation normally grants 3. This sheet preserves the prebuilt class.",
        "The author has corrected the Mage to 3 discipline points: Occult 2 (Magic) and Academia 1 (Chemistry). The extra Medicine 1 (Triage) entry has been removed."
      );
    }
    if (characterId === "emanuel-markusson" && values && typeof values.campaign_notes === "string") {
      values.campaign_notes = values.campaign_notes.replace(
        "The class lists an Upper Arm Blade with a Sharp Rune, but the weapon table gives that blade zero rune slots. The inherited class weapon is retained here; the GM needs to confirm that exception. Its damage is shown as 3 + 1 from the listed rune.",
        "The Upper Arm Blade has 2 rune slots. Its Sharp Rune uses both slots and adds +1 damage because the weapon already deals Slashing damage: 3 + 1 = 4. This equipment follows the listed rune rules."
      );
    }
    if (characterId !== "tizian-hokstorm" || !values || typeof values !== "object") return values;
    const previousSword = {
      weapon2_name_type: "Foldable Sword + Sharp Rune",
      attr_vapen2_traffa: "+1",
      attr_vapen2_skada: "3 Slashing",
      attr_vapen2_specialregler: "Base damage 2 + Sharp Rune 1. Concealable; Parry; Light; one-handed."
    };
    if (Object.entries(previousSword).every(([name, value]) => values[name] === value)) {
      for (const name of Object.keys(previousSword)) {
        values[name] = fields.find(field => field.name === name).defaultValue;
      }
    }
    // Update only the exact previous preset text, preserving player-written changes.
    const previous = {
      ability1_cost: "Nano Module required; CPU capacity 30%",
      ability1_effect: "Activate a program by making a Nanomancy roll and taking its CPU load. Ending a program frees its CPU immediately. A short rest can clear all active programs. Cannot be combined with Magical Ritual. See the beta notes for the roll, Mana cost and overload threshold.",
      ability2_cost: "Action; Nanomancy roll; 10% CPU; 30 m",
      ability2_effect: "Send nanites at one enemy within 30 m. Deal 2 damage, ignoring armor. No separate Mana amount or duration is stated in the program entry.",
      ability3_cost: "Nanomancy roll; 10% CPU",
      ability3_effect: "When using a discipline to heal someone, also heal 1 additional point in another attribute. This supplements the healing discipline check; it is not a replacement for that check. No separate Mana amount or duration is stated in the program entry."
    };
    previous.power1_cost = previous.ability2_cost;
    previous.power1_effect = previous.ability2_effect;
    previous.power2_cost = previous.ability3_cost;
    previous.power2_effect = previous.ability3_effect;
    for (const field of fields) {
      if (Object.prototype.hasOwnProperty.call(previous, field.name) && values[field.name] === previous[field.name]) {
        values[field.name] = field.defaultValue;
      }
    }
    const previousCpuText = "Activate a program by rolling Intelligence + Technology and taking its listed CPU load. Tizian's base pool is 3 + 1 = 4d6, doubled to 8d6 when his Programming specialization applies. Nanomancy has no Mana cost. Ending a program frees its CPU immediately. A short rest can clear all active programs. Cannot be combined with Magical Ritual. See the beta notes for the overload threshold.";
    if (values.ability1_effect === previousCpuText) {
      values.ability1_effect = fields.find(field => field.name === "ability1_effect").defaultValue;
    }
    if (typeof values.campaign_notes === "string") {
      const correctedSwordNote = "The author has corrected the class weapon to Short Sword + Sharp Rune: its 2 rune slots hold the rune, and damage is 3 + 1 = 4 Slashing.";
      for (const oldSwordNote of [
        "The class lists a Foldable Sword with a Sharp Rune, but its 1 rune slot cannot hold a 2-slot Sharp Rune. The intended sword is awaiting the author's clarification.",
        "The class gives a Foldable Sword with a Sharp Rune, but the sword has 1 rune slot and the rune uses 2. This is an inconsistency between the class loadout and the equipment table, not a confirmed exception. The listed class equipment is retained pending clarification.",
        "The class gives a Foldable Sword with a Sharp Rune, but the sword has 1 rune slot and the rune uses 2. Keep it as the class exception pending GM confirmation."
      ]) {
        values.campaign_notes = values.campaign_notes.replace(oldSwordNote, correctedSwordNote);
      }
      values.campaign_notes = values.campaign_notes.replace(
        "The Nanomancy roll and any Mana cost also need confirmation.",
        "Nanomancy uses Intelligence + Technology and has no Mana cost, as clarified by the game's author."
      );
      values.campaign_notes = values.campaign_notes.replace(
        "Keep it as the class exception pending GM confirmation.",
        "This is an inconsistency between the class loadout and the equipment table, not a confirmed exception. The listed class equipment is retained pending clarification."
      );
      for (const oldText of [
        "CPU capacity is Intelligence x 10% = 30%; the beta's separate reference to overload at 100% needs GM clarification.",
        "CPU capacity is Intelligence x 10% = 30%; the beta's separate reference to overload at 100% also needs clarification."
      ]) {
        values.campaign_notes = values.campaign_notes.replace(oldText,
          "CPU capacity is Intelligence x 10% = 30%. Three 10% programs fill 100% of Tizian's personal capacity. At full capacity, attempting another program requires a Nanomancy roll; failure causes 1 Wisdom damage and Paralyzed for 1 round.");
      }
    }
    return values;
  }

  function save() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(readValues()));
      status.textContent = "Saved in this browser. Download a character file to keep a backup.";
    } catch {
      status.textContent = "Browser saving is unavailable. Download a character file to keep your changes.";
    }
  }

  try {
    const saved = localStorage.getItem(storageKey);
    if (saved) {
      applyValues(updatePregenDefaults(JSON.parse(saved)));
      status.textContent = "Your last character was restored from this browser.";
    } else {
      status.textContent = characterId
        ? "Ready to play. Changes to this character are saved separately in this browser."
        : "Ready. Changes will be saved in this browser.";
    }
  } catch {
    status.textContent = "Stored data could not be loaded. Download a character file to keep your changes.";
  }

  form.addEventListener("submit", event => event.preventDefault());
  form.addEventListener("input", () => {
    resizeTextareas();
    clearTimeout(saveTimer);
    status.textContent = "Saving…";
    saveTimer = setTimeout(save, 250);
  });
  window.addEventListener("pagehide", () => {
    if (saveTimer) save();
  });

  document.getElementById("export-sheet").addEventListener("click", () => {
    const values = readValues();
    const data = { schema, version: 1, fields: values };
    const name = (values.character_name.trim() || "character").replace(/[^a-z0-9_-]+/gi, "-").slice(0, 60);
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `eldritch-shadows-${name}.json`;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    status.textContent = "Character file prepared for download. Keep it as your backup.";
  });

  document.getElementById("import-sheet").addEventListener("change", async event => {
    const file = event.target.files[0];
    if (!file) return;
    try {
      if (file.size > maxFileSize) throw new Error("File too large");
      const data = JSON.parse(await file.text());
      if (data.schema !== schema || data.version !== 1) throw new Error("Unrecognized file");
      validateValues(data.fields);
      clearTimeout(saveTimer);
      applyValues(updatePregenDefaults(data.fields));
      save();
    } catch {
      status.textContent = "Could not load this file. Choose a character JSON file downloaded from this sheet (up to 1 MB). Your current character has not been changed.";
    } finally {
      event.target.value = "";
    }
  });

  function preparePrint() {
    for (const field of fields) {
      if (field.type === "checkbox") continue;
      let mirror = field.nextElementSibling;
      if (!mirror || !mirror.classList.contains("print-value")) {
        mirror = document.createElement("span");
        mirror.className = "print-value";
        mirror.setAttribute("aria-hidden", "true");
        field.after(mirror);
      }
      mirror.textContent = field.value || "\u00a0";
      if (field.tagName === "TEXTAREA") {
        mirror.classList.add("multiline");
        mirror.style.setProperty("--rows", field.rows);
      }
    }
    form.classList.add("print-ready");
  }

  window.addEventListener("beforeprint", preparePrint);
  window.addEventListener("afterprint", () => form.classList.remove("print-ready"));
  document.getElementById("print-sheet").addEventListener("click", () => {
    preparePrint();
    window.print();
  });
  resizeTextareas();
})();
