# Streamlit Chat-First Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the unreadable mixed-theme Streamlit interface with a simple, high-contrast, chat-first academic help desk.

**Architecture:** Keep the existing single-file Streamlit presentation layer and all dialog/model interfaces unchanged. Consolidate UI colors and spacing into CSS variables, explicitly style every Streamlit chat/input foreground and surface, and move quick actions from the sidebar into the main task flow.

**Tech Stack:** Python 3, Streamlit, Streamlit AppTest, pytest, browser-based computed-style and responsive verification.

## Global Constraints

- Normal text contrast must be at least 4.5:1.
- Layout must not horizontally overflow at 1280 px desktop or 390 px mobile width.
- Use no external fonts, icon CDNs, or remote visual dependencies.
- Preserve `DialogManager.process_message()`, CSV logging, session reset, and log download behavior.
- Do not change the dataset, model, evaluation results, CLI, report, or slide deck.
- Use built-in Material Symbols for assistant and user avatars.
- The workspace is not a Git repository; commit steps are intentionally omitted.

---

### Task 1: Add UI Regression Tests

**Files:**
- Modify: `tests/test_ui_app.py`
- Test: `tests/test_ui_app.py`

**Interfaces:**
- Consumes: `ui_app.py` source and Streamlit's `AppTest` representation.
- Produces: regression coverage for readable theme declarations, main quick actions, and removal of the obsolete service index.

- [ ] **Step 1: Write failing source-level contrast tests**

Add assertions requiring an explicit `.stApp` foreground, explicit chat Markdown foreground selectors, a light chat-input surface, and no `.service-index` markup:

```python
def test_ui_css_explicitly_controls_light_theme_contrast():
    source = (ROOT / "ui_app.py").read_text(encoding="utf-8")
    assert ".stApp" in source and "color: var(--ink)" in source
    assert '[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]' in source
    assert '[data-testid="stChatInput"]' in source
    assert "background: var(--surface)" in source


def test_ui_removes_decorative_service_index():
    source = (ROOT / "ui_app.py").read_text(encoding="utf-8")
    assert 'class="service-index"' not in source
```

- [ ] **Step 2: Write failing AppTest assertions for main quick actions**

Extend the startup test so labels `Tanya KRS`, `Jadwal ujian`, `Bayar UKT`, and `Syarat beasiswa` appear in the rendered button collection.

- [ ] **Step 3: Run focused tests and confirm RED**

Run: `python3 -m pytest tests/test_ui_app.py -q`

Expected: failure because the existing CSS does not set the `.stApp` foreground, chat Markdown is not explicitly styled, the service index still exists, and quick actions remain in the sidebar with old labels.

---

### Task 2: Implement the Chat-First Streamlit Layout

**Files:**
- Modify: `ui_app.py:30-340`
- Test: `tests/test_ui_app.py`

**Interfaces:**
- Consumes: `DialogManager`, `log_interaction()`, `st.session_state.messages`, and `selected_prompt`.
- Produces: the same `user_input = selected_prompt or typed_prompt` behavior through a clearer high-contrast layout.

- [ ] **Step 1: Replace CSS with a coherent token foundation**

Define `--navy`, `--blue`, `--gold`, `--canvas`, `--surface`, `--ink`, `--muted`, `--line`, `--success`, `--danger`, a 4/8/16/24/32 spacing scale, 10/16 px radii, and one 160 ms transition.

Set `.stApp { background: var(--canvas); color: var(--ink); }` and explicitly style nested Markdown in chat, sidebar, buttons, and the input so Streamlit dark-theme foregrounds cannot leak into light surfaces.

- [ ] **Step 2: Simplify the sidebar**

Keep the UMB mark, `Model siap digunakan`, the data-demo disclosure, `Reset sesi`, CSV download, and technical model caption. Remove sidebar quick-prompt buttons so task shortcuts exist in only one place.

- [ ] **Step 3: Build the compact main header and interactive action rail**

Render a compact `SIAKAD Assist` heading, a one-sentence description, and four main buttons using `st.columns(4)`:

```python
quick_prompts = {
    "Tanya KRS": "saya ingin mengisi krs",
    "Jadwal ujian": "jadwal uas dapat dilihat di mana",
    "Bayar UKT": "bagaimana cara bayar ukt",
    "Syarat beasiswa": "apa syarat mendaftar beasiswa",
}
columns = st.columns(4)
selected_prompt = None
for column, (label, prompt) in zip(columns, quick_prompts.items()):
    with column:
        if st.button(label, key=f"quick_{label}", use_container_width=True):
            selected_prompt = prompt
```

- [ ] **Step 4: Make status and conversation user-facing**

Rename `Status dialog` to `Status layanan`; map states to `Siap membantu`, `Masukkan NIM`, `Pilih mata kuliah`, and `Periksa dan konfirmasi KRS`. Use `:material/school:` and `:material/person:` avatars.

- [ ] **Step 5: Run focused tests and confirm GREEN**

Run: `python3 -m pytest tests/test_ui_app.py -q`

Expected: all UI tests pass.

---

### Task 3: Verify Visual Quality and Behavior

**Files:**
- Modify only if verification exposes a defect: `ui_app.py`, `tests/test_ui_app.py`
- Evidence: browser screenshots and computed-style output during the task

**Interfaces:**
- Consumes: running Streamlit application at a local URL.
- Produces: measured contrast, responsive layout evidence, and verified dialog behavior.

- [ ] **Step 1: Reload and inspect desktop initial state**

At 1280 px width, verify the compact header, four main quick actions, human-readable status, chat message, and light input are visible without horizontal overflow.

- [ ] **Step 2: Measure computed colors and contrast**

Read computed foreground/background colors for `.stApp`, assistant Markdown, user Markdown, and the textarea. Calculate WCAG contrast and require at least 4.5:1 for normal text.

- [ ] **Step 3: Exercise FAQ and KRS flows**

Submit `bagaimana cara bayar ukt`, then reset and run `saya ingin mengisi krs` → `41523120017` → `1, 2` → `ya`. Verify the status label and rendered conversation at each state.

- [ ] **Step 4: Inspect 390 px mobile rendering**

Verify no horizontal overflow, quick actions wrap or stack cleanly, the sidebar can collapse, and conversation/input remain readable.

- [ ] **Step 5: Run the complete regression suite**

Run: `python3 -m pytest -q`

Expected: all project tests pass with no failures.

