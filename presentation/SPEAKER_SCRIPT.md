# Speaker Script and Viva Notes

**Wideband MIMO Antenna with Metasurface** · Mid-semester presentation, Checkpoint 1 · Dept. of ECE, NIT Silchar · October 2026

---

## Before you start

**Time target:** about 14 minutes for the talk, then questions. At a calm pace this script takes about 14 minutes.

### Who presents what

| Presenter | Slides | Topic | Time |
|---|---|---|---|
| Anushka Dam | 1–4 | Title, antenna basics, problem | about 3 min 15 s |
| Nishit Baishya | 5–8 | Our antenna, our idea, objectives, literature | about 3 min 50 s |
| Chanswarang Boro | 9–12 | Method, initial antenna, optimisation, optimised antenna | about 3 min 35 s |
| Sanjana | 13–16 | Metasurface S11 and directivity, challenges, future work, conclusion | about 3 min 35 s |

### Tips

- Look at the examiners, not at the screen. Turn to the slide only to point.
- When you say a number, point at it on the plot.
- Speak slowly. Use short sentences. Pause for a moment when the slide changes.
- Say "GHz" as "gigahertz", "dB" as "dee-bee", "dBi" as "dee-bee-eye", "S11" as "S-one-one", and "φ = 0°" as "phi equals zero degrees".
- Hand over by name, for example: "Now Nishit will show our antenna."
- **Call the new result "directivity", not "gain".** Say: "The metasurface makes the antenna more directive. The peak directivity rises from 3.7 to 8.8 dBi." If asked about gain, say: "Directivity is the gain before losses. Realized gain over the whole band is our next step."
- Quote the fair numbers: the peak, 3.7 → 8.8 dBi, and "higher over 78 % of 2–6 GHz". Do not use the +7 dB at 5.9 GHz as a headline (Q44).
- If you do not know an answer, say so. Then say how you would find out.
- Practise with a timer at least twice. If you run late, shorten slides 2 and 3, not the results.

**How to use this file:** the bullets are the points to remember. The grey quote block is what to say.

---

## Slide 1 — Title

**Presenter:** Anushka · **Time:** ~30 s

**Key points to remember**
- Say the project title and that this is checkpoint 1.
- Introduce all four members, then the guide and the co-guide.

> Good morning, respected professors. Our project is called "Wideband MIMO Antenna with Metasurface". This is our first checkpoint. I am Anushka Dam. With me are Chanswarang Boro, Nishit Baishya and Sanjana. Our guide is Dr. Ujjal Chakraborty, and our co-guide is Mr. Sovan Bhattacharya. We thank them both for their support.

*Transition:* "Let us start with a simple question: what is an antenna?"

---

## Slide 2 — What is an antenna?

**Presenter:** Anushka · **Time:** ~50 s

**Key points to remember**
- An antenna is a bridge between a cable and open space. It works both ways: transmit and receive.
- Everyday examples: phone, Wi-Fi router, GPS.
- Size is linked to wavelength. Higher frequency means a smaller antenna.

> An antenna is a bridge between a cable and open space. When we transmit, it takes the electrical signal from the cable and sends it out as a radio wave. When we receive, it does the opposite. It catches the radio wave and turns it back into an electrical signal. Antennas are all around us. Your phone has several. So does your Wi-Fi router, and so does a GPS receiver. One simple rule sets the size of an antenna. Its size is linked to the wavelength. A higher frequency has a shorter wavelength, so the antenna can be smaller. That is why a phone antenna is tiny, and a radio tower is huge.

*Transition:* "So how do we decide if an antenna is good?"

---

## Slide 3 — How we judge an antenna

**Presenter:** Anushka · **Time:** ~60 s

**Key points to remember**
- S11 shows how much power bounces back. Below −10 dB, less than 10 % comes back.
- Bandwidth is the frequency range where S11 stays below −10 dB.
- Gain and radiation pattern show how strongly, and in which direction, the antenna sends power. Gain is in dBi.
- Point at both sketches: the S11 curve with its −10 dB line, then the two patterns.

> We mainly check two things. The first is matching, shown by S11. It tells us how much power bounces back from the antenna instead of going in. Lower is better. Below minus 10 dB, less than 10 percent of the power comes back. The range of frequencies where S11 stays below minus 10 dB is called the bandwidth. You can see this in the left sketch. The second thing is gain and radiation pattern. They tell us how strongly the antenna sends power, and in which direction. We give gain in dBi. That means compared with an ideal antenna that sends power equally in all directions. On the right, a plain monopole sends power both to the front and to the back. With a reflector behind it, most of the power goes forward.

*Transition:* "With these two ideas, let us look at our problem."

---

## Slide 4 — Introduction & problem statement

**Presenter:** Anushka · **Time:** ~55 s

**Key points to remember**
- Wideband: one antenna for many services, about 2–15 GHz.
- MIMO: several antennas, more data, a more reliable link.
- Problem: a printed monopole sends power front and back, so its gain is low. A plain metal sheet would have to sit far away, which makes the antenna thick.
- End with the question: how do we raise gain while staying thin and wideband?

> Today one device uses many wireless services. Instead of one antenna for each service, a wideband antenna can cover them all. Our target is roughly 2 to 15 GHz. Next, MIMO. MIMO means several antennas on one device. Together they carry more data, and they keep the link reliable. Now the problem. We use a printed monopole. It is wideband, but it sends power both to the front and to the back, so its gain is low. The usual fix is a metal sheet behind it. But that sheet must sit about a quarter of a wavelength away. At our lowest frequencies that is a few centimetres, so the antenna becomes thick. So our question is simple. How can we raise the gain, and still stay thin and wideband?

*Transition:* "Now Nishit will show you our antenna."

---

## Slide 5 — Our antenna: CPW-fed printed monopole

**Presenter:** Nishit · **Time:** ~60 s

**Key points to remember**
- FR-4 board, 50 × 50 mm, 1.6 mm thick: cheap, common, easy to make. Drawback: some loss at high frequency.
- Decagon patch: ten sides, close to a circle, so the current flows smoothly. This helps wideband operation.
- CPW feed: the signal strip and both grounds are on the same side. One metal layer, no vias, easy connector.
- The back of the board is bare. This leaves room for the reflector.

> Here is our antenna. It is printed on an FR-4 board, 50 by 50 millimetres, and 1.6 millimetres thick. We chose FR-4 because it is cheap, common and easy to fabricate. Its drawback is some loss at high frequencies. The radiating part is a decagon, a ten-sided shape. It is very close to a circle. A rounded shape lets the current flow smoothly, which helps the antenna work over a wide band. We feed it with a coplanar waveguide, or CPW. A signal strip runs between two ground planes, all on the same side. So we need only one metal layer and no vias, and a connector fits easily at the edge. The back of the board is bare. That leaves room for a reflector behind it.

*Transition:* "So which reflector do we use? That is our main idea."

---

## Slide 6 — Our idea: a metasurface reflector

**Presenter:** Nishit · **Time:** ~60 s

**Key points to remember**
- A metasurface is a thin board with a repeating pattern of small metal cells. Each cell is much smaller than the wavelength. Together they control how a wave reflects.
- Ours has 6 × 5 cells, two split rings in each, on FR-4 with copper on the back. It sits 2 mm behind the antenna.
- A plain metal sheet this close would weaken the forward wave over much of the band.
- The split rings are *meant* to make the reflected wave add to the forward wave. **Our CST result supports the goal:** more of the power now goes forward, and the peak directivity rises from 3.7 to 8.8 dBi (slide 14).

> A metasurface is a thin board printed with a repeating pattern of small metal cells. Each cell is much smaller than the wavelength. Together, the cells control how a wave is reflected. Our metasurface has 6 by 5 cells. Each cell has two split rings. It is made on FR-4, with solid copper on the back. We place it only 2 millimetres behind the antenna. Why not a plain metal sheet? A metal sheet flips the wave when it reflects it. At such a small distance, the flipped wave comes back almost opposite to the forward wave, and weakens it over much of our band. The split rings are meant to change the reflection, so that the reflected wave adds to the forward wave instead. Our first CST result supports the goal: the peak directivity rises from 3.7 to 8.8 dBi.

*Transition:* "Let me now state our objectives clearly."

---

## Slide 7 — Objectives

**Presenter:** Nishit · **Time:** ~40 s

**Key points to remember**
- (1) Compact CPW-fed wideband antenna, about 2–15 GHz.
- (2) Optimise in CST: ground position first, then patch size.
- (3) Add the split-ring metasurface to raise gain while staying thin.
- (4) Phase II: MIMO, fabrication, measurement.

> We have four objectives. First, design a compact, CPW-fed wideband antenna that covers about 2 to 15 GHz. Second, optimise it in CST. We first find the best ground position, and then the best patch size. Third, add the split-ring metasurface to raise the gain, while keeping the antenna thin. Fourth, in Phase Two, we will extend the design to MIMO, and then fabricate and measure it. The first two objectives are complete. The third is in progress.

*Transition:* "Next, let us see what other researchers have done."

---

## Slide 8 — Literature review & research gap

**Presenter:** Nishit · **Time:** ~70 s

**Key points to remember**
- Three papers use a frequency selective surface (FSS) behind the antenna. The gain rises by roughly 4–6 dB, but the total height is 9–20 mm.
- Sen 2017: double split-ring metasurface, about +5.5 dB. Hasan 2022: 4-port MIMO with a split-ring metasurface, 12 mm.
- Gap: reflectors usually sit 9–20 mm away. A gap of only a few millimetres over 2–15 GHz is rarely reported.
- Last row, our work: peak **directivity** 3.7 → 8.8 dBi with the metasurface 2 mm away. The papers quote gain, so do not claim we beat them yet.
- Say "in the papers we reviewed". **Never say "first".**

> This table shows five papers close to our work. Three of them place a frequency selective surface behind the antenna. That is a printed pattern that reflects the wave. They raise the gain by roughly 4 to 6 dB. But the whole structure is 9 to 20 millimetres thick. Sen and colleagues used a double split-ring metasurface, like ours, and reported about 5.5 dB more gain. Hasan and colleagues used a split-ring metasurface with a four-port MIMO antenna, at 12 millimetres. So here is the gap. In the papers we reviewed, the reflector usually sits 9 to 20 millimetres away. A gap of only a few millimetres, over 2 to 15 GHz, is rarely reported. Ours is just 2 millimetres. The last row is our first result: the peak directivity rises from 3.7 to 8.8 dBi.

*Transition:* "Now Chanswarang will explain how we did the work."

---

## Slide 9 — Proposed methodology

**Presenter:** Chanswarang · **Time:** ~50 s

**Key points to remember**
- Eight steps. Steps 1–7 are done. Step 7 is directivity versus frequency, with and without the metasurface (slide 14). Step 8 is Phase II.
- Realized gain over the whole band and tuning still remain in this phase (slide 15).
- Tool: CST Studio Suite 2019, frequency-domain solver, 0–18 GHz. Materials: FR-4 and copper.
- Method: change one dimension at a time, and keep the value with the best S11.

> We follow eight steps. Step one, we built the initial antenna in CST. In steps two and three, we swept the ground position, and then the patch size. Step four gave the optimised antenna and its S11. In step five we designed the metasurface. In step six we simulated the antenna together with the metasurface. In step seven, we compared the directivity with and without the metasurface. These seven steps are done. Step eight is Phase Two: MIMO, fabrication and testing. We use CST Studio Suite 2019, with its frequency-domain solver, from 0 to 18 GHz. Our method is simple. We change one dimension at a time, and we keep the value that gives the best S11.

*Transition:* "Let us see where we started."

---

## Slide 10 — Work done: initial antenna

**Presenter:** Chanswarang · **Time:** ~45 s

**Key points to remember**
- Decagon radius 15 mm. The ground edge was far from the patch, at −20 mm.
- S11 stays above −10 dB from 2 to 7.7 GHz, so the match is poor there.
- Higher up there are only a few narrow dips. This told us the feed region was the problem.

> This is our starting design. The decagon has a radius of 15 millimetres. The ground edge was far away from the patch, at minus 20 millimetres. Now look at the S11 curve. From 2 GHz to about 7.7 GHz, it stays above the minus 10 dB line. So the antenna is poorly matched over that whole range. Higher up, there are only a few narrow dips below the line. This told us that the problem was in the feed region. The ground was simply too far from the patch.

*Transition:* "So the first thing we changed was the ground position."

---

## Slide 11 — Work done: optimisation

**Presenter:** Chanswarang · **Time:** ~70 s

**Key points to remember**
- Ground sweep: 10 positions from −20 to −7 mm. A closer ground gives stronger coupling and a better low-frequency match. −7 mm is the only position below −10 dB across the band.
- Patch sweep: 13 radius values from 4 to 15 mm. Small patches leave 3–12 GHz poorly matched. At 15 mm the resonances join into one band.
- A bigger patch also closes the gap to the ground.
- Both best values sit at the edge of the range, because the feed gap is now almost closed.

> On the left is the ground position sweep. We tried ten positions, from minus 20 to minus 7 millimetres. In a CPW antenna, the ground is part of the antenna. As we moved it closer to the patch, the coupling got stronger, and the low-frequency match got better. At minus 7 millimetres, S11 stays below minus 10 dB across the band. It was the only position that did this. On the right is the patch size sweep. We tried thirteen radius values, from 4 to 15 millimetres. Small patches leave the middle of the band poorly matched. At 15 millimetres, the resonances join into one band. A bigger patch also closes the gap to the ground. So both best values sit at the edge of our range.

*Transition:* "Here is the antenna we got."

---

## Slide 12 — Work done: optimised antenna

**Presenter:** Chanswarang · **Time:** ~50 s

**Key points to remember**
- S11 below −10 dB from 2.16 to 15.73 GHz: one band about 13.6 GHz wide. It covers the 2–15 GHz target.
- Four resonances: about 2.7, 4.8, 9.2 and 14.3 GHz. They overlap into one band.
- Be honest: the margin is thin near 6.5 and 12.2 GHz.

> This is our optimised antenna. S11 stays below minus 10 dB from about 2.2 GHz to about 15.7 GHz. That is one continuous band, about 13.6 GHz wide. It covers our target of 2 to 15 GHz. You can see four dips, at about 2.7, 4.8, 9.2 and 14.3 GHz. Each dip is a resonance. They sit close together, so they overlap and form one wide band. One honest point. Near 6.5 and 12.2 GHz, the curve only just stays below the line. So the margin there is thin.

*Transition:* "Now Sanjana will show what happened when we added the metasurface."

---

## Slide 13 — Work done: antenna + metasurface S11

**Presenter:** Sanjana · **Time:** ~55 s

**Key points to remember**
- The band now runs from about 2.0 GHz up to 18 GHz. 18 GHz is only where the simulation stops.
- Three narrow gaps above −10 dB: 3.0–3.4 GHz (worst −6.6 dB), 4.5–4.7 GHz (−9.7 dB), 5.1–5.6 GHz (−8.8 dB).
- Reason: so close, the metasurface changes the antenna's input match. It needs tuning.
- Talk only about the match here. The directivity result is on the next slide.

> On top is the antenna alone. Below is the same antenna with the metasurface 2 millimetres behind it. The band now starts a little lower, at about 2 GHz. It stays matched up to 18 GHz, which is where our simulation ends. But there are three narrow gaps where S11 rises above minus 10 dB. They are from 3.0 to 3.4 GHz, from 4.5 to 4.7 GHz, and from 5.1 to 5.6 GHz. The worst point is about minus 6.6 dB, near 3 GHz. Why does this happen? The metasurface is very close, so it changes the antenna's input match. We need to tune it.

*Transition:* "So does the metasurface do its main job, and send more of the power forward? Let us look at the directivity."

---

## Slide 14 — Work done: the metasurface raises the directivity

**Presenter:** Sanjana · **Time:** ~55 s

**Key points to remember**
- The plot is CST directivity: at each frequency, the highest value in the φ = 0° plane. Copper solid line = with the metasurface, grey dashed line = antenna alone. The shading shows which one is higher.
- Say "directivity", not "gain". Directivity is the gain the antenna would have with no losses.
- Headlines: peak 3.7 dBi (near 4 GHz) → 8.8 dBi (at 5.9 GHz), +5.1 dB. Over 2–6 GHz, higher on 78 % of the band; mean 2.3 → 3.9 dBi (+1.6 dB).
- Caveats: lower at ≈ 2.9–3.1 GHz (worst −3.1 dB at 3.0 GHz, beside the 3.0–3.4 GHz S11 gap) and at ≈ 3.3–4.0 GHz (by up to ≈ 2.2 dB). Data only from 1 to 6 GHz.
- **Do not use the +7.3 dB at 5.9 GHz as the headline.** The antenna alone dips there because its beam leaves the φ = 0° plane (Q44).

> This slide shows directivity against frequency. Directivity is the gain the antenna would have with no losses. The grey dashed line is the antenna alone, and the copper line is with the metasurface. The peak rises from 3.7 dBi alone to 8.8 dBi with the metasurface. From 2 to 6 GHz, the copper line is higher over 78 percent of the band, and 1.6 dB higher on average. So the metasurface makes the antenna more directive. It sends more of its power forward, as we intended. Two honest points. It is lower in two narrow bands, near 3 GHz and from 3.3 to 4 GHz. And this result covers only 1 to 6 GHz.

*Transition:* "Realized gain over the whole band is our next step. Here are our challenges and the work ahead."

---

## Slide 15 — Challenges & future work

**Presenter:** Sanjana · **Time:** ~60 s

**Key points to remember**
- Challenges: long simulation time; sweep glitches near 4 and 6 GHz from too few frequency points (to be re-run); thin match margin; metasurface detuning (three S11 gaps, two directivity dips).
- Remaining in this phase: realized gain over the whole 2–15 GHz band, alone and with the metasurface; tune the metasurface to close the S11 gaps and the directivity dips; radiation patterns.
- Phase II: 4-port MIMO (elements turned 90°) with the metasurface; isolation and ECC; fabricate on FR-4; measure with a VNA and in an anechoic chamber.
- Expected outcomes: thin wideband antenna with higher gain, compact MIMO with good isolation, tested prototype.

> We faced four main challenges. Simulations take a long time. A few sweep curves show glitches near 4 and 6 GHz, because of too few frequency points. We will re-run them. The match margin is thin in two places. And the metasurface detunes the antenna, and the directivity dips in two narrow bands. To finish Phase One, we will simulate the realized gain from 2 to 15 GHz, tune the metasurface to close the gaps and the dips, and plot the radiation patterns. In Phase Two, we will build a four-port MIMO antenna, with each element turned by 90 degrees. We will check isolation and ECC. Then we will fabricate it and measure it. We expect a thin, higher-gain wideband antenna, a compact MIMO antenna, and a tested prototype.

*Transition:* "Let me sum up."

---

## Slide 16 — Conclusion & references

**Presenter:** Sanjana · **Time:** ~45 s

**Key points to remember**
- Antenna designed and optimised: matched from 2.16 to 15.73 GHz.
- Metasurface added at 2 mm: about 2–18 GHz, except three narrow gaps that need tuning. Peak directivity 3.7 → 8.8 dBi.
- Next: realized gain and tuning, then the MIMO antenna.
- Thank the panel and invite questions.

> To conclude. We designed a CPW-fed decagon antenna and optimised it in CST. It is matched from about 2.2 to 15.7 GHz. We then placed a split-ring metasurface 2 millimetres behind it. Now the match reaches from about 2 to 18 GHz, except for three narrow gaps that need tuning. And the peak directivity rises from 3.7 to 8.8 dBi. Next come the realized gain and the tuning, and then the MIMO antenna. Our main references are listed on this slide. Thank you for listening. We are happy to take your questions.

---

# Viva questions and simple answers

Keep answers short. Say the main idea first. If an examiner pushes further, give one extra detail, not five.

## Antenna basics

**Q1. What is an antenna?**
It is the part that changes a guided electrical signal in a cable into a radio wave in free space, and back again. The IEEE standard calls it "a means for radiating or receiving radio waves". The same antenna can transmit and receive.

**Q2. Why is antenna size linked to wavelength?**
An antenna works best when the current on it can form a standing pattern, which needs a length of about a quarter or half of a wavelength. A higher frequency has a shorter wavelength, so the antenna can be smaller. That is why our board is only a few centimetres across.

**Q3. What is S11?**
S11 is the reflection coefficient at the input port. It tells us how much of the power sent into the antenna comes back down the cable. We show it in dB. A more negative value means less power comes back, so the match is better.

**Q4. Why do you use −10 dB as the limit?**
At −10 dB, about 10 % of the power is reflected and about 90 % goes into the antenna. This is the same as a VSWR of about 2. It is the usual, widely accepted limit for defining an antenna's bandwidth, so it lets us compare fairly with other papers.

**Q5. What is bandwidth?**
It is the range of frequencies over which the antenna works well. For matching, it is the range where S11 stays below −10 dB. For our optimised antenna, that is about 2.2 to 15.7 GHz.

**Q6. What is a resonance?**
A resonance is a frequency where the antenna "fits" the wave naturally, like a swing pushed at its own rhythm. There, strong current builds up on the antenna, and the antenna accepts power easily. On the S11 plot, each resonance shows up as a dip.

**Q7. What is gain, and what does dBi mean?**
Gain tells us how strongly the antenna sends power in its best direction. We compare it with an imaginary "isotropic" antenna that sends power equally in all directions. dBi means "dB relative to isotropic". It includes the antenna's losses.

**Q8. What is the difference between gain and directivity?**
Directivity only describes the shape of the pattern: how much the antenna focuses power. Gain is directivity reduced by the antenna's own losses, such as loss in the copper and in the FR-4. So gain is always a little lower than directivity. Our slide-14 result is directivity, so it does not include these losses yet.

**Q9. What is a radiation pattern, and why does a printed monopole have low gain?**
A radiation pattern is a map of how strongly the antenna radiates in each direction. A printed monopole radiates almost the same to the front and to the back of the board, so its power is spread out. Spread-out power means low gain in any one direction.

**Q10. Why are printed monopoles wideband?**
A wide, flat shape supports several resonances at different frequencies. When these resonances sit close together, they overlap and form one continuous band. Rounded or many-sided shapes help, because the current can flow smoothly and the input changes gradually with frequency.

## Our antenna and the CPW feed

**Q11. Why a patch? Is this a microstrip patch antenna?**
No. We call the radiator a "patch" because it is a flat printed shape, but it works as a monopole. A microstrip patch antenna has a full ground on the back and is narrowband. Our back is bare, and the ground sits beside the patch, which is why it is wideband.

**Q12. Why a decagon, and not a rectangle or a circle?**
A rectangle has sharp corners where the current changes direction suddenly, which usually gives fewer and more separated resonances. A decagon is very close to a circle, so it keeps the smooth current flow of a disc. Its straight edges are easy to draw and mesh in CST, and one flat side faces the feed, so the gap to the ground is even. We have not compared it directly with a perfect circle. That could be a small extra study.

**Q13. What is a CPW feed?**
CPW means coplanar waveguide. A thin signal strip runs down the middle, with a ground plane on each side, and all three are on the same face of the board. Power travels along the slots between the strip and the grounds.

**Q14. Why CPW and not microstrip?**
CPW needs only one metal layer, so there are no vias and no need to line up front and back. An SMA connector fits easily at the board edge. CPW also works well over a wide band. Most important for us, it leaves the back of the board bare, so the metasurface can sit behind it.

**Q15. Why FR-4?**
FR-4 is cheap, easy to find, strong, and any PCB shop can etch it. Its drawbacks are loss that grows with frequency and a dielectric constant that varies a little from batch to batch. Low-loss boards such as Rogers are better, but cost much more. For a student prototype, FR-4 is a fair trade-off.

**Q16. Why 50 Ω?**
50 Ω is the standard impedance for RF cables, connectors and test equipment such as a VNA. It became the standard as a compromise between low loss and high power handling in coaxial cable. Matching to 50 Ω means our antenna connects directly to standard equipment.

**Q17. Why is the back of the board bare?**
In a CPW-fed monopole, the ground is on the front, beside the patch. A metal layer on the back would turn it into a different, narrowband antenna. The bare back also leaves room for the metasurface reflector.

## Optimisation

**Q18. Why does the ground position matter so much?**
In a CPW-fed monopole, the ground is part of the radiator. The patch and the ground work together, like the two arms of a dipole. The small gap between the ground edge and the patch acts like a coupling capacitor. It decides how smoothly power moves from the 50 Ω feed into the patch, especially at low frequencies. A large gap leaves a long, thin feed line, and the match is poor.

**Q19. What does "ground at −7 mm" mean physically?**
It is the position of the ground planes' top edge along the feed line, in our CST coordinates. Moving it from −20 to −7 mm brings the ground edge right up to the patch. At −7 mm the gap is well under a millimetre (worked out from the geometry).

**Q20. Why R = 15 mm?**
In our sweep, every patch size has its first dip near 2.3–2.7 GHz, so R does not move the lower edge much (the first dip even moves up slightly as R grows). What R changes is the middle of the band: small patches leave 3–12 GHz poorly matched, and at 15 mm the resonances join into one band. Also, the patch is centred at a fixed point, so a bigger patch reaches closer to the ground. At 15 mm the feed gap is almost closed. So both best values, ground at −7 mm and R = 15 mm, sit at the geometric limit. We call them "the best within our range", not a true optimum.

**Q21. Why change one dimension at a time?**
It is simple, and it shows clearly what each dimension does. The drawback is that the two dimensions affect each other, so we may miss a better combination. A joint optimisation in CST could be a later step.

**Q22. Which solver did you use, and why?**
We used the frequency-domain solver in CST Studio Suite 2019, from 0 to 18 GHz. It solves the fields at chosen frequencies and fills in the curve between them. It handles small details such as the narrow CPW slots well. The time-domain solver is a good cross-check for wideband runs, and we may use it.

**Q23. What are the glitches in some sweep curves?**
A few sweep curves show sudden jumps near 4 and 6 GHz. We believe they come from too few frequency points in those runs, so the solver filled in the curve badly. They are not physical. We base our conclusions on the final smooth runs, and we will re-run those sweeps with more points.

## Metasurface

**Q24. What is a metasurface?**
It is a thin, flat array of small metal cells, each much smaller than the wavelength. Together, the cells control how a wave reflects from the surface or passes through it. It is the flat, two-dimensional version of a metamaterial, so it is thinner and easier to make.

**Q25. What is a split-ring resonator?**
It is a small metal ring with a cut in it. The ring acts like a small coil, an inductance. The cut acts like a small capacitor. Together they make a resonant circuit, so the ring responds strongly at one frequency. Pendry and colleagues proposed it in 1999 as a building block for metamaterials.

**Q26. Why two rings in each cell?**
Each ring has its own resonance, so two rings of different sizes give two resonances. Close together, they help the cell work over a wider range. The two rings also couple to each other, which adds capacitance and lowers the resonance, so the cell can stay small.

**Q27. Why a metasurface and not a plain metal plate?**
A metal plate flips the wave when it reflects it. The wave also travels to the plate and back. If the plate is a quarter wavelength away, that trip makes up for the flip, and the two waves add. At only 2 mm, the trip is far too short across our whole band, so the reflected wave comes back almost opposite and cancels the forward wave. The split rings are meant to change the reflection so that it adds instead. Our first result supports this: with the metasurface, more of the power goes forward, and the peak directivity rises from 3.7 to 8.8 dBi. Realized gain, and a plate at the same gap, will show over which part of the band the forward signal really gets stronger.

**Q28. Why must a plain metal sheet be about a quarter wavelength away?**
The reflection flips the wave by half a cycle. Going to the sheet and back adds another half cycle when the sheet is a quarter wavelength away. Together that is one full cycle, so the reflected wave lines up with the forward wave and adds. At the low end of our band, a quarter wavelength is a few centimetres, which is too thick.

**Q29. Why copper on the back of the metasurface?**
With copper behind, almost all of the wave is reflected and nothing leaks through. The rings then only change the timing of the reflection. Without copper, a thin sheet of rings would let much of the wave pass, especially at low frequencies, and the reflection would be weak. Where the rings are not resonant, the surface behaves much like the copper sheet behind it.

**Q30. Why 2 mm?**
We set it as our target to keep the whole antenna thin. It is a small fraction of the wavelength at the low end of our band, and much smaller than the 9–20 mm used in the papers we reviewed. It is our starting value. We may adjust it slightly when we tune the metasurface.

**Q31. What is an FSS, and how is yours different?**
An FSS, or frequency selective surface, is a printed pattern that reflects some frequencies and lets others pass. Three of our reviewed papers place one behind the antenna. Ours has a full copper back, so it reflects at all frequencies, and the split rings shape how it reflects.

## Results and honesty points

**Q32. Why did the metasurface create the mismatch gaps, and how will you fix them?**
At 2 mm, the metasurface sits very close to the antenna, in its near field. It couples to the antenna and changes its input impedance, so the match changes at some frequencies. The rings' own resonances may also appear in that range. To fix this, we will tune the gap, the ring sizes and, if needed, the ground position again.

**Q33. Why does the band now go up to 18 GHz? What does that mean?**
18 GHz is simply where our simulation stops. The curve stays below −10 dB up to the last point we simulated, so we cannot say what happens above 18 GHz. Our target is 2–15 GHz, so the part above 15 GHz is a bonus, not a claim.

**Q34. Why does the band now start a little lower, at about 2 GHz?**
We believe the metasurface adds extra loading near the antenna, which pulls the lowest resonance down a little. This is a small shift, and the three gaps above it matter more right now.

**Q35. What does "thin margin near 6.5 and 12.2 GHz" mean?**
At those frequencies, S11 is only just below −10 dB. A small change in a real board, such as a slightly different FR-4 or a small etching error, could push it above the line. We want more margin before fabrication.

**Q36. What are the limitations of your work so far?**
Everything is simulation only, with no measurement yet. FR-4 is lossy, which will lower the gain and efficiency. The match margin is thin in two places, a few sweep curves have glitches that we must re-run, and the metasurface has created three mismatch gaps. Our directivity result is not realized gain, it covers only 1–6 GHz and one plane, and it dips in two narrow bands. Also, our optimisation was one dimension at a time, and both best values sit at the edge of the range.

**Q37. What is new in your work?**
In the papers we reviewed, the reflector usually sits 9–20 mm behind the antenna. We are trying to make it work at 2 mm across 2–15 GHz, and then use it with a MIMO antenna. Our first result is encouraging: at 2 mm, the peak directivity rises from 3.7 to 8.8 dBi. We do not claim to be the first. Our aim is this combination.

**Q38. Did you compare with a plain metal plate at the same gap?**
Not yet. It is a fair test: the same plate size at the same 2 mm gap. It matters even more now. A plain plate this close would probably also push the power to one side and raise the directivity. But it would also cancel much of the antenna's radiation and spoil the match. Directivity does not show that; realized gain does. So we will add the plate to the realized-gain runs, to show whether the metasurface really does better.

## The directivity result (slide 14)

**Q39. Did the metasurface improve the gain?**
It made the antenna more directive, which is what it is meant to do. In CST, the peak directivity rose from 3.7 to 8.8 dBi. From 2 to 6 GHz, it was higher over 78 % of the band, and 1.6 dB higher on average. But this is directivity, not realized gain, it covers only 1–6 GHz, and it is lower in two narrow bands. So today we say "more directive". Realized gain over the whole band is our next step.

**Q40. Is this result gain or directivity?**
Directivity. It is the gain the antenna would have with no losses: it shows how strongly the antenna focuses its power in its best direction. Gain also subtracts the loss in the copper and the FR-4. Realized gain also subtracts the power reflected at the port, so it drops most where S11 is poor, as in the 3.0–3.4 GHz gap. Realized gain is what a real link sees, so it is our next result.

**Q41. Why the φ = 0° plane?**
That is how this CST plot was set up. At each frequency, it takes the highest directivity in one cut, the φ = 0° plane. This cut stands at right angles to the board, so it contains the direction straight out of the board, front and back. That makes it a sensible cut for a reflector. But it is only one plane. If the beam tilts out of it, the plot misses the true maximum, as it does for the antenna alone near 5.5 GHz. For realized gain, we will take the maximum over all directions.

**Q42. Why only 1–6 GHz?**
CST gives directivity only at frequencies that have a farfield monitor. The metasurface run had farfield monitors only from 1 to 6 GHz, every 0.1 GHz. The antenna-alone run had dense monitors from 1 to 6 GHz, plus only 9 and 18 GHz. So we compare the two over 2–6 GHz, where both runs have data and the antenna is matched. Above 6 GHz we do not know yet what the metasurface does.

**Q43. Why does the directivity drop near 3 GHz?**
We are not sure yet. The worst drop is at 3.0 GHz, where the metasurface curve is 3.1 dB below the antenna alone. That is right next to the 3.0–3.4 GHz S11 gap, so the metasurface interacts strongly with the antenna there. Two likely reasons: the reflected wave comes back out of step and cancels part of the forward wave, or the beam tilts out of the φ = 0° plane. The 3D pattern at 3 GHz will tell us which. A smaller dip, up to about 2.2 dB, runs from 3.3 to 4.0 GHz. We will tune the metasurface to close these dips and the S11 gaps.

**Q44. Why not quote the +7 dB at 5.9 GHz?**
Because it would not be fair. At 5.9 GHz the metasurface curve is 7.3 dB higher, but that number is inflated: the antenna alone dips there in this plane, because its beam points out of the φ = 0° plane. Our earlier 3D gain plot shows about 4.3 dBi for the antenna alone near 5.4 GHz, far more than this plane shows. So we quote fairer numbers: the peak rises from 3.7 to 8.8 dBi (+5.1 dB), and over 2–6 GHz the metasurface is higher on 78 % of the band, by 1.6 dB on average.

**Q45. How will you get realized gain?**
In CST, with the Farfield Result template: Post-Processing → Template Based Post-Processing → Farfield and Antenna Properties → Farfield Result. We choose Realized Gain, the maximum over all directions (not one plane), and all farfield monitors. That gives one realized-gain curve against frequency. For the whole band, we must first add farfield monitors from 2 to 15 GHz, ideally every 0.5 GHz, to both models, and re-run them with the same settings. The steps are in CST_GUIDE.md. Realized gain counts the FR-4 loss and the mismatch, so it is the fair test.

## MIMO and future work

**Q46. What is MIMO?**
MIMO means using several antennas at the transmitter and the receiver. It can send different data streams at the same time over the same band. That is called spatial multiplexing, and it gives more data. It can also send copies of the same data over different paths. That is called diversity, and it makes the link more reliable.

**Q47. What is isolation?**
Isolation tells us how little signal leaks from one antenna port into another on the same board. We read it from S21 and the other coupling curves. A more negative value is better. Many papers aim for better than about 15 dB.

**Q48. What is ECC?**
ECC is the envelope correlation coefficient. It tells us how similar the signals, or patterns, of two antennas are. 0 means fully independent, and 1 means identical. Lower is better. A value below 0.5 is usually accepted, and good designs reach much lower.

**Q49. Why turn the four elements by 90°?**
Each turned element points its fields in a different direction, so the elements "see" the space differently. This lowers the coupling between them and lowers the ECC. It also gives polarisation diversity.

**Q50. Will the metasurface affect the MIMO isolation?**
It can, because it is a shared surface behind all four elements. Some papers, such as Hasan 2022, report better isolation with a metasurface, but we must check our own design. We will compare isolation and ECC with and without it.

## Measurement

**Q51. How will you fabricate the antenna?**
We will etch the antenna and the metasurface on FR-4 boards with copper, using standard PCB methods. Then we will solder an SMA connector at the CPW feed edge.

**Q52. How will you measure S11?**
We will use a vector network analyser, or VNA. First we calibrate it with a standard calibration kit, so the cable effects are removed. Then we connect the antenna and record S11 across the band. For MIMO, we also record the coupling between ports.

**Q53. How will you measure gain and the radiation pattern?**
In an anechoic chamber, whose walls are covered with absorbers so that there are no reflections. We rotate the antenna and record the received power in each direction to get the pattern. For gain, we compare our antenna with a reference horn of known gain.

**Q54. How will you hold the metasurface at 2 mm?**
With small spacers made of foam or plastic, which affect the wave very little. Foam is close to air, so it keeps the setup close to the simulation.

**Q55. Will measured results match the simulation?**
They should be close, but not identical. Real FR-4, etching errors, the SMA connector, the solder and the cable all add small changes. The thin-margin regions are the most likely to move, so we will watch them closely.

---

# Sources

Facts in this script were checked against the sources below. Most website fetches were blocked by the network proxy, so the online checks used search-result summaries of these pages. The two textbooks are standard references that we did not open online.

**Project data.** Every S11 and directivity number comes from the team's CST runs. The slide-14 curves were digitised from the CST plots (`figures/cst_single_final_directivity.png`, `figures/cst_single_ms_directivity.jpg`) to about ±0.05 dB, into `exports/single_final_directivity_digitized.csv` and `exports/single_ms_directivity_digitized.csv`. `analysis/plot_directivity.py` draws the comparison and computes the numbers.

**Main sources**

1. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley, 2016. Standard textbook. Used for the definition of an antenna (it quotes IEEE Std 145, "a means for radiating or receiving radio waves"), gain, directivity, dBi, radiation pattern, VSWR, and reflector spacing. Chapter 1 excerpt: <https://catalogimages.wiley.com/images/db/pdf/9781118642061.excerpt.pdf>
2. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012. Standard textbook. Used for the reflection coefficient, return loss, VSWR and the 50 Ω standard. (Not checked online.)
3. R. N. Simons, *Coplanar Waveguide Circuits, Components, and Systems*, Wiley-IEEE Press, 2001. Used for the CPW structure and its advantages. <https://onlinelibrary.wiley.com/doi/10.1002/0471224758.ch1>
4. J. Liang, C. C. Chiau, X. Chen and C. G. Parini, CPW-fed printed circular-disc monopole, *IEEE Trans. Antennas Propag.*, vol. 53, no. 11, 2005. Used for: a rounded printed monopole fed by a 50 Ω CPW gives a wide band. <https://doi.org/10.1109/TAP.2005.858598>
5. J. B. Pendry, A. J. Holden, D. J. Robbins and W. J. Stewart, "Magnetism from conductors and enhanced nonlinear phenomena," *IEEE Trans. Microw. Theory Tech.*, vol. 47, no. 11, pp. 2075–2084, 1999. Origin of the split-ring resonator: two concentric rings, each with a small gap. <https://doi.org/10.1109/22.798002>
6. C. L. Holloway et al., "An overview of the theory and applications of metasurfaces: The two-dimensional equivalents of metamaterials," *IEEE Antennas Propag. Mag.*, vol. 54, no. 2, pp. 10–35, 2012. Used for the definition of a metasurface. <https://scholars.duke.edu/publication/798858>
7. G. Sen, A. Banerjee, M. Kumar and S. Das, split-ring metasurface reflector behind a wideband monopole, *Microw. Opt. Technol. Lett.*, vol. 59, no. 6, pp. 1296–1300, 2017. Double split rings, about +5.5 dB gain. <https://onlinelibrary.wiley.com/doi/10.1002/mop.30527>
8. M. M. Hasan et al., "Gain and isolation enhancement of a wideband MIMO antenna using metasurface for 5G sub-6 GHz communication systems," *Sci. Rep.*, vol. 12, Art. 9433, 2022. Used for MIMO with a metasurface, isolation and ECC. <https://www.nature.com/articles/s41598-022-13522-5>

**Web pages used to cross-check single points**

- Return loss: −10 dB means about 10 % reflected and a VSWR of about 2. Ezurio, "Understanding Antenna Design": <https://www.ezurio.com/resources/white-papers/understanding-antenna-design>
- Gain, directivity, dBi and efficiency. MVG, "A Guide to Common Antenna Terms": <https://www.mvg-world.com/en/manual/antenna-measurement-101/a-guide-to-common-antenna-terms>
- CPW-fed antennas: uniplanar, no via holes, low dispersion. ISAP 2000 paper: <https://www.ieice.org/cs/isap/ISAP_Archives/2000/pdf/POSA1-6.pdf>
- Wideband operation from overlapping resonances. *Sci. Rep.* 2020: <https://www.nature.com/articles/s41598-020-73478-2>
- FR-4 loss at high frequency (loss tangent about 0.02). PMC article: <https://pmc.ncbi.nlm.nih.gov/articles/PMC8898327/>
- Why 50 Ω. Altium: <https://resources.altium.com/p/mysterious-50-ohm-impedance-where-it-came-and-why-we-use-it>
- ECC definition (0 to 1, lower is better). antenna-theory.com: <https://www.antenna-theory.com/definitions/envelope-correlation-coefficient-ecc.php>
- MIMO multiplexing and diversity. D. Tse, lecture slides: <https://www.winlab.rutgers.edu/~crose/dimacs03/david.pdf>

**Points we could not confirm online. These come from textbook reasoning, so state them in simple terms only:**

- The "smooth current path" argument for rounded or polygonal patches. Polygonal monopoles giving wide bands was confirmed, but not this specific explanation.
- "Two rings give two resonances, so the cell works over a wider range." Nested rings giving two resonances, and Sen 2017's broadband in-phase reflection, were confirmed. The general rule was not.
- Why the copper back is needed, and the ease of fitting an SMA connector to a CPW feed.
