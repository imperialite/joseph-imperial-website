"use strict";

(() => {
  const sections = [
    { id: "profile", title: "Profile", description: "Update your name, contact details, research summary, and current appointments." },
    { id: "about", title: "About Me", description: "Edit your introduction one paragraph at a time. Keep paragraphs in the order you want them to appear." },
    { id: "news", title: "News", description: "Add updates and arrange them with the most recent news first." },
    { id: "publications", title: "Selected Publications", description: "Edit publication details and author lists. Use the arrows to arrange papers. Papers appear together by year." },
    { id: "experience", title: "Experience", description: "Update your research appointments and professional experience." },
    { id: "education", title: "Education", description: "Update your qualifications, institutions, and supporting details." },
    { id: "awards", title: "Awards & Recognition", description: "Add awards, fellowships, and other academic recognition." },
    { id: "media", title: "Media Presence", description: "Update interviews, articles, and coverage of your research." },
    { id: "socials", title: "Socials", description: "Manage links to your academic profiles, social accounts, and CV." }
  ];
  const byId = (id) => document.getElementById(id);
  const form = byId("section-form");
  const fields = byId("section-fields");
  const saveButton = byId("save-button");
  const publishButton = byId("publish-button");
  let model = null;
  let active = "profile";
  let dirty = false;
  let busy = false;
  let changeVersion = 0;
  let publishStatus = null;
  let fieldSerial = 0;
  let linkTarget = null;
  const openCards = new Map();
  const removals = [];

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function action(label, className, handler) {
    const button = element("button", className, label);
    button.type = "button";
    button.addEventListener("click", handler);
    return button;
  }

  function sectionItems(id) {
    return id === "publications" ? model.publications : model.content[id];
  }

  function markDirty() {
    dirty = true;
    changeVersion += 1;
    updateSaveState();
  }

  function updateSaveState() {
    const state = byId("save-state");
    state.textContent = busy ? "Saving…" : dirty ? "You have unsaved changes" : "All changes saved locally";
    state.classList.toggle("unsaved", dirty && !busy);
    byId("footer-state").textContent = dirty ? "Save changes to update your preview." : "Your preview includes all saved changes.";
    saveButton.disabled = !model || busy || !dirty;
    publishButton.disabled = !model || busy || !publishStatus?.publish_available;
    saveButton.textContent = busy ? "Saving…" : "Save changes";
    form.inert = busy;
    byId("undo-button").disabled = busy;
  }

  function message(text, kind = "success") {
    const box = byId("message");
    box.className = `message ${kind}`;
    box.setAttribute("role", kind === "error" ? "alert" : "status");
    byId("message-text").textContent = text;
    box.hidden = false;
  }

  async function request(path, options = {}) {
    const response = await fetch(path, { credentials: "same-origin", cache: "no-store", ...options });
    let data;
    try { data = await response.json(); }
    catch { throw new Error(response.ok ? "The editor received an unexpected response. Please restart it and try again." : `Request failed (${response.status}). Please restart the editor and try again.`); }
    if (!response.ok || data.ok === false) throw new Error(data.message || data.error || `Request failed (${response.status}).`);
    return data;
  }

  function richToolbar(input) {
    const toolbar = element("div", "field-toolbar");
    toolbar.append(element("p", "field-hint", "Links use [link text](https://example.com)."));
    toolbar.append(action("Add a link", "text-button", () => {
      linkTarget = { input, start: input.selectionStart ?? input.value.length, end: input.selectionEnd ?? input.value.length };
      byId("link-label").value = input.value.slice(linkTarget.start, linkTarget.end);
      byId("link-url").value = "";
      byId("link-dialog").showModal();
      (byId("link-label").value ? byId("link-url") : byId("link-label")).focus();
    }));
    return toolbar;
  }

  function field(labelText, value, setValue, options = {}) {
    const wrapper = element("div", `field${options.full ? " full-width" : ""}`);
    const id = `field-${++fieldSerial}`;
    const label = element("label", "", labelText);
    label.htmlFor = id;
    const input = element(options.multiline ? "textarea" : options.choices ? "select" : "input");
    input.id = id;
    if (options.multiline) {
      input.rows = options.rows || 3;
      if (options.rows === 2) input.classList.add("short-text");
    } else if (options.choices) {
      for (const choice of options.choices) {
        const option = element("option", "", choice.label);
        option.value = choice.value;
        input.append(option);
      }
      if (!options.choices.some((choice) => choice.value === value) && value) {
        const retained = element("option", "", value);
        retained.value = value;
        input.append(retained);
      }
    } else input.type = options.type || "text";
    input.value = value ?? "";
    if (options.placeholder) input.placeholder = options.placeholder;
    input.addEventListener(options.choices ? "change" : "input", () => {
      setValue(input.value);
      markDirty();
    });
    wrapper.append(label, input);
    if (options.hint) {
      const hint = element("p", "field-hint", options.hint);
      hint.id = `${id}-hint`;
      input.setAttribute("aria-describedby", hint.id);
      wrapper.append(hint);
    }
    if (options.rich) wrapper.append(richToolbar(input));
    return wrapper;
  }

  function checkbox(labelText, value, setValue, hint) {
    const wrapper = element("div", "field full-width");
    const label = element("label", "checkbox-label");
    const input = element("input");
    input.type = "checkbox";
    input.checked = Boolean(value);
    input.addEventListener("change", () => { setValue(input.checked); markDirty(); });
    label.append(input, document.createTextNode(labelText));
    wrapper.append(label);
    if (hint) wrapper.append(element("p", "field-hint", hint));
    return wrapper;
  }

  function renderNavigation() {
    const nav = byId("section-nav");
    nav.replaceChildren();
    for (const section of sections) {
      const button = action("", "nav-button", () => {
        active = section.id;
        render();
      });
      button.append(element("span", "", section.title));
      const count = sectionItems(section.id)?.length;
      if (Number.isInteger(count)) button.append(element("span", "nav-count", String(count)));
      if (active === section.id) button.setAttribute("aria-current", "page");
      nav.append(button);
    }
  }

  function listTools(array, index, label) {
    const tools = element("div", "record-actions");
    for (const [symbol, delta, direction] of [["↑", -1, "up"], ["↓", 1, "down"]]) {
      const button = action(symbol, "icon-button", () => {
        const next = index + delta;
        [array[index], array[next]] = [array[next], array[index]];
        openCards.set(active, new Set([next]));
        markDirty();
        render();
        fields.querySelector(`[data-record-index="${next}"] .record-toggle, [data-record-index="${next}"] textarea, [data-record-index="${next}"] input`)?.focus();
      });
      button.disabled = index + delta < 0 || index + delta >= array.length;
      button.setAttribute("aria-label", `Move ${label} ${index + 1} ${direction}`);
      button.title = `Move ${direction}`;
      tools.append(button);
    }
    const remove = action("Remove", "icon-button remove-button", () => {
      const [item] = array.splice(index, 1);
      removals.push({ array, index, item, section: active, label });
      markDirty();
      render();
      updateUndo();
      byId("undo-button").focus();
    });
    remove.setAttribute("aria-label", `Remove ${label} ${index + 1}`);
    tools.append(remove);
    return tools;
  }

  function updateUndo() {
    byId("undo-notice").hidden = removals.length === 0;
    if (removals.length) byId("undo-text").textContent = `Removed ${removals.at(-1).label}.`;
  }

  function list(container, array, label, makeDefault, renderFields, titleFor, options = {}) {
    const records = element("div", "records");
    if (!array.length) records.append(element("p", "empty-state", `No ${options.plural || `${label}s`} yet. Use the button below to add one.`));
    if (!openCards.has(active)) openCards.set(active, new Set([0]));
    array.forEach((item, index) => {
      const card = element("article", `record${options.text ? " text-record" : ""}`);
      card.dataset.recordIndex = String(index);
      const header = element("div", "record-header");
      const title = element("div", "record-title");
      const number = element("span", "record-index", String(index + 1).padStart(2, "0"));
      const titleText = element("span", "record-title-text", titleFor(item, index));
      const panel = element("div", "record-body");
      panel.id = `record-panel-${++fieldSerial}`;
      if (options.text) title.append(number, titleText);
      else {
        const toggle = action("", "record-toggle", () => {
          panel.hidden = !panel.hidden;
          toggle.setAttribute("aria-expanded", String(!panel.hidden));
          if (panel.hidden) openCards.get(active).delete(index);
          else openCards.get(active).add(index);
        });
        panel.hidden = !openCards.get(active).has(index);
        toggle.setAttribute("aria-expanded", String(!panel.hidden));
        toggle.setAttribute("aria-controls", panel.id);
        toggle.append(element("span", "chevron", "▶"), number, titleText);
        title.append(toggle);
      }
      header.append(title, listTools(array, index, label));
      renderFields(panel, item, index, () => { titleText.textContent = titleFor(array[index], index); });
      card.append(header, panel);
      records.append(card);
    });
    container.append(records);
    container.append(action(`+ Add ${label}`, "add-button", () => {
      array.push(makeDefault());
      openCards.set(active, new Set([array.length - 1]));
      markDirty();
      render();
      const newCard = fields.querySelector(`[data-record-index="${array.length - 1}"]`);
      newCard?.querySelector("textarea, input, select")?.focus();
    }));
  }

  function textList(container, key, label) {
    list(container, model.content[key], label, () => "", (panel, item, index) => {
      panel.append(field(label === "appointment" ? "Appointment" : "Text", item, (value) => { model.content[key][index] = value; }, { multiline: true, full: true, rich: true, rows: key === "about" ? 4 : 3 }));
    }, (_item, index) => `${label.charAt(0).toUpperCase()}${label.slice(1)} ${index + 1}`, { text: true });
  }

  function renderProfile() {
    const site = model.content.site;
    const panel = element("section", "form-panel");
    panel.append(element("h3", "panel-heading", "Your details"));
    const grid = element("div", "field-grid");
    for (const [key, label, options] of [
      ["name", "Full name", {}], ["email", "Email address", { type: "email" }],
      ["description", "Research summary", { multiline: true, full: true, rows: 3, hint: "A short plain-text description of your research." }],
      ["scholar_url", "Google Scholar link", { type: "url" }], ["cv_url", "CV link", { type: "url" }],
      ["github_url", "GitHub link", { type: "url" }], ["anthology_url", "ACL Anthology link", { type: "url" }]
    ]) grid.append(field(label, site[key], (value) => { site[key] = value; }, options));
    panel.append(grid);
    fields.append(panel);
    const heading = element("div", "list-heading");
    heading.append(element("h3", "", "Current appointments"));
    fields.append(heading, element("p", "list-help", "These appear beneath your name and portrait."));
    textList(fields, "profile", "appointment");
  }

  function renderPublications() {
    const panel = element("div", "form-panel");
    panel.append(field("Publication introduction", model.content.publication_note, (value) => { model.content.publication_note = value; }, { multiline: true, rows: 2, rich: true }));
    fields.append(panel);
    list(fields, model.publications, "publication", () => ({ year: String(new Date().getFullYear()), title: "", authors: "", venue: "", topic: "governance", url: "", link_label: "Read paper", featured: false }), (body, item, index, updateTitle) => {
      const grid = element("div", "field-grid");
      const set = (key) => (value) => { item[key] = value; if (key === "title" || key === "year") updateTitle(); };
      grid.append(field("Title", item.title, set("title"), { full: true, multiline: true, rows: 2 }));
      grid.append(field("Year", item.year, set("year"), { placeholder: "2026" }));
      grid.append(field("Venue", item.venue, set("venue"), { placeholder: "Conference or journal" }));
      grid.append(field("Authors", item.authors, set("authors"), { full: true, multiline: true, rows: 3, hint: "Keep the full author list in the order used by the publication." }));
      grid.append(field("Publication or project URL", item.url, set("url"), { type: "url", hint: "Leave blank while the preprint is forthcoming." }));
      grid.append(field("Link type", item.link_label, set("link_label"), { choices: [{ value: "Read paper", label: "Paper" }, { value: "View project", label: "Project page" }, { value: "Preprint forthcoming", label: "Preprint forthcoming" }] }));
      grid.append(checkbox("Highlight this publication", item.featured, (value) => { item.featured = value; }, "Uses the charcoal background and blue rule in your website."));
      body.append(grid);
    }, (item) => `${item.year ? `${item.year} · ` : ""}${item.title || "Untitled publication"}`);
  }

  function renderTimeline(key) {
    const singular = key === "awards" ? "award" : key === "education" ? "qualification" : "position";
    list(fields, model.content[key], singular, () => ({ title: "", institution: "", date: "", note: "", paragraphs: [] }), (body, item, _index, updateTitle) => {
      const grid = element("div", "field-grid");
      const set = (name) => (value) => { item[name] = value; if (name === "title") updateTitle(); };
      grid.append(field(key === "education" ? "Qualification" : key === "awards" ? "Award" : "Position", item.title, set("title"), { full: true }));
      grid.append(field("Institution or organisation", item.institution, set("institution"), { full: true }));
      grid.append(field("Dates", item.date, set("date"), { placeholder: "2022–2026" }));
      grid.append(field("Date note", item.note, set("note"), { placeholder: "Optional, e.g. expected or ongoing" }));
      grid.append(field("Description", (item.paragraphs || []).join("\n\n"), (value) => { item.paragraphs = value === "" ? [] : value.split(/\r?\n\s*\r?\n/); }, { full: true, multiline: true, rows: 5, rich: true, hint: "Separate paragraphs with a blank line. This field is optional." }));
      body.append(grid);
    }, (item) => item.title || `Untitled ${singular}`);
  }

  function renderMedia() {
    list(fields, model.content.media, "media entry", () => ({ outlet: "", html: "" }), (body, item, _index, updateTitle) => {
      const grid = element("div", "field-grid");
      grid.append(field("Publication or outlet", item.outlet, (value) => { item.outlet = value; updateTitle(); }, { full: true }));
      grid.append(field("Description", item.html, (value) => { item.html = value; }, { full: true, multiline: true, rows: 4, rich: true }));
      body.append(grid);
    }, (item) => item.outlet || "Untitled media entry", { plural: "media entries" });
  }

  function renderSocials() {
    list(fields, model.content.socials, "link", () => ({ label: "", url: "" }), (body, item, _index, updateTitle) => {
      const grid = element("div", "field-grid");
      grid.append(field("Label", item.label, (value) => { item.label = value; updateTitle(); }));
      grid.append(field("Web address", item.url, (value) => { item.url = value; }, { type: "url", placeholder: "https://" }));
      body.append(grid);
    }, (item) => item.label || "Untitled link");
  }

  function render() {
    if (!model) return;
    const section = sections.find((item) => item.id === active);
    renderNavigation();
    byId("section-title").textContent = section.title;
    byId("section-description").textContent = section.description;
    fields.replaceChildren();
    if (active === "profile") renderProfile();
    else if (active === "about") textList(fields, "about", "paragraph");
    else if (active === "news") textList(fields, "news", "news item");
    else if (active === "publications") renderPublications();
    else if (["experience", "education", "awards"].includes(active)) renderTimeline(active);
    else if (active === "media") renderMedia();
    else if (active === "socials") renderSocials();
    updateSaveState();
  }

  async function saveChanges(showSuccess = true) {
    if (!model) return false;
    const savedVersion = changeVersion;
    const payload = JSON.stringify({ content: model.content, publications: model.publications, revision: model.revision });
    const response = await request("/api/save", { method: "POST", headers: { "Content-Type": "application/json" }, body: payload });
    if (response.revision === undefined) throw new Error("Changes were saved, but the editor could not confirm the latest version. Reload the editor before saving again.");
    model.revision = response.revision;
    if (savedVersion === changeVersion) {
      dirty = false;
      // The server keeps header links and Socials in sync. Read that result back.
      try {
        const refreshed = await request("/api/content");
        if (!refreshed.content || !Array.isArray(refreshed.publications)) throw new Error("Unexpected content format.");
        model = refreshed;
        removals.length = 0;
        updateUndo();
        render();
      } catch {
        throw new Error("Your changes were saved, but the editor could not refresh the updated content. Reload this page before making further changes.");
      }
    }
    if (showSuccess) message(response.message || "Changes saved. Your local website preview is ready.");
    return true;
  }

  async function saveAction() {
    if (busy) return;
    busy = true;
    updateSaveState();
    try { await saveChanges(); }
    catch (error) { message(error.message, "error"); }
    finally { busy = false; updateSaveState(); }
  }

  async function publishAction() {
    if (busy || !publishStatus?.publish_available) return;
    busy = true;
    updateSaveState();
    const publicPublish = publishStatus.publish_label === "Publish website";
    publishButton.textContent = publicPublish ? "Publishing…" : "Saving to GitHub…";
    try {
      if (dirty) await saveChanges(false);
      const response = await request("/api/publish", { method: "POST" });
      message(response.message || (publicPublish ? "Your website has been published." : "Your saved website files are now on GitHub."));
    } catch (error) { message(error.message, "error"); }
    finally {
      busy = false;
      publishButton.textContent = publicPublish ? "Publish website" : "Save to GitHub";
      updateSaveState();
    }
  }

  function applyPublishStatus(status) {
    publishStatus = status;
    publishButton.hidden = !status.publish_available;
    const publicPublish = status.publish_label === "Publish website";
    publishButton.textContent = publicPublish ? "Publish website" : "Save to GitHub";
    byId("publish-help").textContent = status.message || (status.publish_available ? publicPublish ? "Publish website saves your changes and updates the public website." : "Save to GitHub saves your latest changes to the repository." : "GitHub saving is unavailable. You can still edit and save your website locally.");
    updateSaveState();
  }

  async function load() {
    const [contentResult, statusResult] = await Promise.allSettled([request("/api/content"), request("/api/status")]);
    if (contentResult.status === "rejected") {
      byId("loading-state").textContent = "Your content could not be loaded. Restart the editor or reload this page to try again.";
      byId("save-state").textContent = "Unable to load content";
      message(contentResult.reason.message, "error");
      return;
    }
    const incoming = contentResult.value;
    if (!incoming.content || !Array.isArray(incoming.publications)) {
      byId("loading-state").textContent = "The website content has an unexpected format. Check the local editor's output before trying again.";
      byId("save-state").textContent = "Unable to load content";
      message("The content response is missing the website sections or publication list.", "error");
      return;
    }
    model = incoming;
    // Preserve every supplied field, including fields that have no visible editor.
    model.content.site ??= {};
    for (const section of sections) if (section.id !== "publications") model.content[section.id] ??= [];
    model.content.publication_note ??= "";
    byId("loading-state").hidden = true;
    form.hidden = false;
    byId("editor-footer").hidden = false;
    render();
    if (statusResult.status === "fulfilled") applyPublishStatus(statusResult.value);
    else applyPublishStatus({ publish_available: false, message: "The GitHub connection could not be checked. You can still edit and save locally." });
  }

  form.addEventListener("submit", (event) => { event.preventDefault(); if (dirty) saveAction(); });
  saveButton.addEventListener("click", saveAction);
  publishButton.addEventListener("click", publishAction);
  byId("message").querySelector("button").addEventListener("click", () => { byId("message").hidden = true; });
  byId("undo-button").addEventListener("click", () => {
    const removal = removals.pop();
    if (!removal) return;
    removal.array.splice(Math.min(removal.index, removal.array.length), 0, removal.item);
    active = removal.section;
    openCards.set(active, new Set([removal.index]));
    markDirty();
    render();
    updateUndo();
  });
  byId("link-cancel").addEventListener("click", () => byId("link-dialog").close());
  byId("link-form").addEventListener("submit", (event) => {
    event.preventDefault();
    if (!linkTarget) return;
    const label = byId("link-label").value.trim();
    const url = byId("link-url").value.trim();
    if (!label || !/^https?:\/\//i.test(url)) {
      byId("link-url").setCustomValidity("Enter a complete http:// or https:// address.");
      byId("link-url").reportValidity();
      return;
    }
    const { input, start, end } = linkTarget;
    const insertion = `[${label}](${url})`;
    input.value = input.value.slice(0, start) + insertion + input.value.slice(end);
    input.dispatchEvent(new Event("input", { bubbles: true }));
    byId("link-dialog").close();
    input.focus();
    input.setSelectionRange(start + insertion.length, start + insertion.length);
    linkTarget = null;
  });
  byId("link-url").addEventListener("input", () => byId("link-url").setCustomValidity(""));
  window.addEventListener("beforeunload", (event) => { if (dirty) { event.preventDefault(); event.returnValue = ""; } });
  document.addEventListener("keydown", (event) => { if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") { event.preventDefault(); if (dirty && !busy && !byId("link-dialog").open) saveAction(); } });
  load();
})();
