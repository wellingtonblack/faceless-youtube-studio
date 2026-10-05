# FILE #001 — Keyframe Prompts

Version: 1.0

These prompts are production inputs for the approved FILE #001 storyboard. They
must not generate readable text, phone interfaces, real brands, or emergency
alert imagery; those elements are composed separately.

## scene-06 — Moon reveal reference frame

**Purpose:** Visual continuity anchor for scenes 04, 06, and 07.

**Prompt:**

```text
Vertical 9:16 cinematic mystery film still. Interior of a modest generic
apartment at night, viewed from behind a lone adult man standing perfectly
still at a window; he is only a dark, unidentifiable silhouette. Outside the
window, an anatomically recognizable full Moon is impossibly close, filling
most of the night sky while retaining believable lunar craters and surface
detail. The Moon is the single dominant focal point. Cold moonlight outlines
the silhouette and window frame; restrained deep shadows, high contrast,
photorealistic but slightly stylized, cinematic 35 mm framing, subtle film
grain, clean composition designed for a mobile vertical Short. No text, no
logos, no flags, no landmarks, no phone screen, no app interface, no alert
graphics, no horror gore, no extra people.
```

**Generation settings:** Runway `gen4_image`, 720×1280 vertical, one output.

## scene-04 — Normal Moon reference frame

**Purpose:** Match the approved scene-06 room and window composition before the anomaly escalates.

**Prompt:**

```text
Use @moonReveal only as a composition and lighting reference. Vertical 9:16
cinematic mystery film still in the same generic apartment at night, from
behind the same anonymous adult man standing at the window. The window, room
layout, cool moonlight and restrained silhouette should closely match the
reference. Outside, the full Moon is normal and distant: small in the natural
night sky, fully visible above the horizon, with realistic scale and familiar
lunar surface detail. It must not be enlarged or close to the window. One
clear focal point, photorealistic but slightly stylized, high contrast, clean
vertical composition. No text, no logos, no flags, no landmarks, no phone
screen, no app interface, no alert graphics, no horror gore, no extra people.
```

**Generation settings:** Runway `gen4_image`, 720×1280 vertical, one output,
using `scene-06-moon-reveal-keyframe-v1` as `@moonReveal`.
