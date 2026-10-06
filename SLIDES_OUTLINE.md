# Presentation Outline — Mid-Semester, Checkpoint 1 (16 slides, ~14 min)

Built by `presentation/deck/build_deck.js` (pptxgenjs) into `presentation/FYP_Presentation.pptx`.
The slides carry visuals and keywords; what to say, and the viva Q&A, are in `presentation/SPEAKER_SCRIPT.md`.

```bash
uv run analysis/plot_directivity.py                # directivity comparison (slide 14) → figures/
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
| 6 | Our idea: metasurface | 6 × 5 double split rings, copper back, 2 mm behind; the goal (send the backward wave forward) is confirmed by CST directivity, peak 3.7 → 8.8 dBi | array + one-cell close-up, side view |
| 7 | Objectives | Design, optimise, metasurface, MIMO and testing (Phase II) | four numbered cards |
| 8 | Literature review | Reflectors add gain but sit 9–20 mm away; research gap; this work: 3.7 → 8.8 dBi (directivity) at 2 mm | table + gap bar chart |
| 9 | Methodology | Eight steps — seven done (step 7: directivity vs frequency, with and without the metasurface); realized gain and tuning remain; Phase II next | status timeline, tool cards |
| 10 | Initial antenna | Ground far away (Lg = −20 mm) → poor match from 2 to 7.7 GHz | CST geometry + S11 with a red band |
| 11 | Optimisation | Ground position (best −7 mm), then patch size (best R = 15 mm) | both CST sweeps, best curve highlighted |
| 12 | Optimised antenna | S11 below −10 dB from 2.16 to 15.73 GHz | CST S11 with a green band, big stat |
| 13 | Antenna + metasurface | Wider band (≈ 2.0 → 18 GHz) but three narrow gaps (3.0–5.6 GHz); the gain result is on the next slide | aligned CST S11 plots with bands |
| 14 | Metasurface raises the directivity | Peak 3.7 → 8.8 dBi (+5.1 dB); higher over 78 % of 2–6 GHz (mean +1.6 dB); lower at ≈ 2.9–3.1 and 3.3–4.0 GHz. CST directivity (gain before losses), maximum in the φ = 0° plane, 1–6 GHz only | comparison plot (`figures/fig_directivity_compare_deck.png`), three stat cards |
| 15 | Challenges & future work | Realized gain over 2–15 GHz, tuning (S11 gaps and directivity dips), radiation patterns; Phase II MIMO, ECC, fabrication | icon rows, two plan cards |
| 16 | Conclusion & references | Done: antenna, metasurface, peak directivity 3.7 → 8.8 dBi; next: realized gain and tuning → MIMO antenna | three cards, references |

Remaining outputs (listed as future work, not shown as results): realized gain vs frequency over the whole 2–15 GHz
band, alone and with the metasurface; tuning the metasurface to close the S11 gaps and the directivity dips; radiation
patterns.
