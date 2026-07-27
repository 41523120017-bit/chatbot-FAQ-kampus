# Streamlit Chat-First Redesign Specification

Date: 2026-07-27  
Project: SIAKAD Assist — Universitas Mercu Buana

## 1. Problem and Root Cause

The current interface mixes Streamlit's dark-theme foreground colors with a custom light background. `.stApp` receives a light canvas but retains Streamlit's light foreground color, so chat text is rendered as `rgb(250, 250, 250)` on white cards. The measured contrast is approximately 1.04:1, making the primary conversation unreadable.

Secondary usability problems are an oversized hero, a dark chat-input region that conflicts with the light interface, duplicated navigation between the sidebar and a non-interactive service index, and technical model information competing with the student's primary task.

## 2. Goal

Create a high-contrast, chat-first academic help desk that keeps the UMB navy-and-gold identity while making conversation, quick questions, current dialog state, and recovery actions immediately understandable.

The redesign changes only the Streamlit presentation layer. NLP behavior, dialog states, logging, CLI behavior, dataset, and evaluation artifacts remain unchanged.

## 3. Visual Direction

### Palette

- `--navy: #0B1F3A` — brand anchor and assistant emphasis
- `--blue: #0F5CBD` — primary interaction and focus state
- `--gold: #F4B942` — restrained UMB accent
- `--canvas: #F6F8FB` — page background
- `--surface: #FFFFFF` — cards and input surfaces
- `--ink: #182230` — primary readable text
- `--muted: #526071` — secondary text, still WCAG-readable
- `--line: #D6DEE8` — borders and separators
- `--success: #16794E` — ready/success status with text, never color alone
- `--danger: #B42318` — error and destructive states

### Typography

- Display: Georgia only for the compact `SIAKAD Assist` wordmark.
- Body/UI: system sans-serif (`Segoe UI`, Arial, sans-serif).
- Utility/status: system monospace only for small confidence or state metadata.
- Minimum body size: 16 px with at least 1.5 line-height.

### Signature Element

A narrow navy-and-gold academic service rail containing real quick-action controls. It references a campus service counter without becoming a decorative, non-interactive navigation bar.

## 4. Information Architecture

Desktop:

```text
┌────────────────────┬─────────────────────────────────────────────┐
│ UMB service panel  │ Compact identity + short purpose statement  │
│                    ├─────────────────────────────────────────────┤
│ Model ready        │ Quick actions: KRS / UKT / Ujian / Beasiswa │
│ Help and demo data ├─────────────────────────────────────────────┤
│                    │ Human-readable dialog status                │
│ Reset / log        ├─────────────────────────────────────────────┤
│                    │ Conversation                                │
│                    │ assistant: white / user: pale blue          │
└────────────────────┴─────────────────────────────────────────────┘
                      Fixed light input with clear focus state
```

Mobile:

- Sidebar collapses according to Streamlit behavior.
- Header uses a smaller wordmark and one-sentence description.
- Quick actions wrap into two columns.
- Conversation occupies the full content width.
- Chat input remains light, readable, and reachable without horizontal scrolling.

## 5. Component Decisions

### Header

- Replace the oversized hero with a compact header.
- Retain UMB identity and one plain-language purpose sentence.
- Remove decorative spacing that delays access to the chat.

### Quick Actions

- Remove the non-interactive five-column service index.
- Render four actual Streamlit buttons in the main area: KRS, jadwal ujian, pembayaran UKT, and beasiswa.
- Use one consistent button pattern with visible hover and keyboard focus.

### Dialog Status

- Change the label from technical `Status dialog` to `Status layanan`.
- Keep a concise user-facing value such as `Siap membantu`, `Menunggu NIM`, or `Periksa dan konfirmasi KRS`.
- Use both text and an icon/dot, not color alone.

### Conversation

- Assistant message: white surface, navy left marker, dark text.
- User message: pale-blue surface, blue border, dark text.
- Explicitly style nested Markdown elements (`p`, `li`, `strong`, `code`) so they cannot inherit unreadable Streamlit theme colors.
- Use consistent 16 px body text and readable line-height.
- Replace mixed emoji avatars with Streamlit's built-in Material Symbols: `:material/school:` for the assistant and `:material/person:` for the user.

### Chat Input

- Use a light surface matching the rest of the application.
- Dark input text and readable placeholder.
- Blue focus border plus gold focus ring.
- Keep the send control visually distinct in enabled and disabled states.

### Sidebar

- Reduce visual weight and remove duplicated quick prompts.
- Retain model-ready status, demo disclosure, reset, and CSV download because they support the UAS demonstration.
- Place technical model details below user-facing help, with secondary visual weight.

## 6. Accessibility and Usability Requirements

- Normal text contrast must be at least 4.5:1.
- Large text and non-text UI boundaries must meet at least 3:1 where applicable.
- All buttons must have a visible `:focus-visible` state and a minimum 44 px target height.
- Status must not rely on color alone.
- Layout must not horizontally overflow at 1280 px desktop or 390 px mobile width.
- `prefers-reduced-motion` disables decorative transitions.
- Error responses remain readable and provide a recovery action.

## 7. Behavior and Data Flow

The existing flow remains:

1. A typed message or quick action creates a user message.
2. `DialogManager.process_message()` returns the assistant response and updates the state.
3. The interaction is written to the CSV log with NIM masking.
4. Streamlit reruns and renders the new state and conversation.

No model retraining or dialog-manager changes are part of this redesign.

## 8. Verification

Automated regression checks will verify:

- `.stApp` and chat Markdown receive explicit readable foreground colors.
- Assistant and user messages use distinct surfaces.
- The obsolete non-interactive service index is removed.
- Main quick actions are present and continue to invoke the dialog manager.
- Existing Streamlit smoke and logging tests continue to pass.

Browser verification will cover:

- Computed chat text/background colors and contrast ratio.
- Initial desktop view and a completed FAQ interaction.
- KRS multi-turn state changes.
- Mobile layout, wrapping, and horizontal overflow.
- Console errors and full Python test suite.

## 9. Out of Scope

- Changes to the dataset, intent model, evaluation results, CLI, report, or slide deck.
- Connection to the production SIAKAD service.
- External fonts, icon CDNs, or remote visual dependencies.
