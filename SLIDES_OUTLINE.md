# Presentation Outline — Mid-Semester, Checkpoint 1 (15 slides, ~13 min)

Built by `presentation/deck/build_deck.js` (pptxgenjs) into `presentation/FYP_Presentation.pptx`.
The slides carry visuals and keywords; what to say, and the viva Q&A, are in `presentation/SPEAKER_SCRIPT.md`.

```bash
uv run presentation/deck/make_concepts.py          # concept sketches + metasurface cell close-up → figures/
cd presentation/deck && npm install && node build_deck.js
```

| # | Slide | Message | Visual |
|---|---|---|---|
| 1 | Title | Project, team, guides; checkpoint 1 | optimised antenna in front of the metasurface |
| 2 | What is an antenna? | Signal ↔ radio wave; size follows wavelength | transmitter → antenna → waves → antenna → receiver |
| 3 | How do we judge an antenna? | S11 below −10 dB = good match; gain and pattern | concept S11 sketch, concept pattern sketch |
| 4 | Introduction & problem | Wideband + MIMO; monopole radiates front and back → low gain; a metal sheet must be far away | three icon cards, problem and question panels |
| 5 | Our antenna | CPW-fed decagon on FR-4; why FR-4, why a decagon, why CPW | labelled antenna, CPW cross-section |
| 6 | Our idea: metasurface | 6 × 5 double split rings, copper back, 3.9 mm behind | array + one-cell close-up, side view |
| 7 | Objectives | Design, optimise, metasurface, MIMO and testing (Phase II) | four numbered cards |
| 8 | Literature review | Reflectors add gain but sit 9–20 mm away; research gap | table + gap bar chart |
| 9 | Methodology | Eight steps: six done, gain plots remaining, Phase II planned | status timeline, tool cards |
| 10 | Initial antenna | Ground far away (Lg = −20 mm) → poor match from 2 to 7.7 GHz | CST geometry + S11 with a red band |
| 11 | Optimisation | Ground position (best −7 mm), then patch size (best R = 15 mm) | both CST sweeps, best curve highlighted |
| 12 | Optimised antenna | S11 below −10 dB from 2.16 to 15.73 GHz | CST S11 with a green band, big stat |
| 13 | Antenna + metasurface | Wider band (≈ 2.0 → 18 GHz) but three narrow gaps (3.0–5.6 GHz) | aligned CST S11 plots with bands |
| 14 | Challenges & future work | Gain plots (alone, with metasurface), tuning; Phase II MIMO, ECC, fabrication | icon rows, two plan cards |
| 15 | Conclusion & references | What is done, what is next | three cards, references |

Remaining outputs (listed as future work, not shown as results): gain vs frequency of the antenna alone, and gain vs
frequency of the antenna + metasurface.
