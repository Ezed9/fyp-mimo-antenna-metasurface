# Windows Setup: Automating the CST Models with Claude Code

Follow these steps on the **Windows PC that has CST Studio Suite installed**. At the end, Claude Code writes
Python scripts that build every CST model automatically (see `CST_GUIDE.md` for what the models are).

Time needed: about 30 minutes of setup, then the Claude Code session itself.

All commands below go in **PowerShell** (Start menu → type `PowerShell` → open it).
Paste a command, press Enter, and wait for it to finish before you run the next one.

---

## Step 1: Install Git

```powershell
winget install --id Git.Git -e
```

Close PowerShell and open it again. Then check that Git works:

```powershell
git --version
```

You should see something like `git version 2.4x`. If `winget` isn't recognised, download Git from
<https://git-scm.com/download/win> and install it with the default options.

## Step 2: Install uv (the Python manager)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close PowerShell and open it again. Then check it:

```powershell
uv --version
```

You don't need to install Python yourself. uv downloads the version that CST needs.

## Step 3: Install Claude Code

Pick **one** of these:

- **Desktop app (easiest):** download the Claude app from <https://claude.ai/download>, install it,
  sign in, and open the **Code** tab.
- **Terminal version:** run the command below, then close and reopen PowerShell.

  ```powershell
  irm https://claude.ai/install.ps1 | iex
  ```

  Check it with `claude --version`.

## Step 4: Download the project

Choose a short folder path with no spaces. Long paths and paths with spaces can cause trouble with CST.

```powershell
mkdir C:\FYP
cd C:\FYP
git clone https://github.com/Ezed9/fyp-mimo-antenna-metasurface.git
cd fyp-mimo-antenna-metasurface
dir
```

You should see `CST_GUIDE.md`, `analysis`, `exports` and this file.

## Step 5: Find your CST version and install folder

1. Open CST Studio Suite and go to **Help → About**. Write down the version year (for example **2024**).
2. Find the install folder. It's usually one of these:
   - `C:\Program Files (x86)\CST Studio Suite 2024`
   - `C:\Program Files\CST Studio Suite 2024`
3. Check that the Python library folder exists (change the year/path to match yours):

   ```powershell
   dir "C:\Program Files (x86)\CST Studio Suite 2024\AMD64\python_cst_libraries"
   ```

   You should see a folder called `cst`. If you get "cannot find path", try the other path from step 2,
   or right-click the CST desktop shortcut → **Open file location** to find it.

Write down the full install folder path. You'll need it in Step 7.

## Step 6: Export the current single antenna's history

Claude reads this file to get the dimensions of your existing antenna.

1. Open your current single-antenna `.cst` project in CST.
2. Open the **History List**. It's on the **Modeling** tab, or type `History List` into the search box at the top right of the ribbon.
3. Click the first entry, then **Shift + click** the last entry so they're all selected.
4. Click **Edit**. A text window opens with the VBA code for every step.
5. Press **Ctrl + A**, then **Ctrl + C**.
6. Open **Notepad**, press **Ctrl + V**, and leave it open.
7. Back in CST, open the **Parameter List** (the panel at the bottom; if it's hidden, use **View → Parameter List**).
   At the bottom of the Notepad file, add one line per parameter in the form `name = value`, for example:

   ```text
   ' ---- Parameter List ----
   Ws = 40
   Ls = 45
   R = 12
   ```

8. Choose **File → Save As**. Save into `C:\FYP\fyp-mimo-antenna-metasurface\` with the name
   **`existing_single_history.txt`**. Set *Save as type* to **All files** so Notepad doesn't add a second `.txt`.

Check that it's there:

```powershell
dir C:\FYP\fyp-mimo-antenna-metasurface\existing_single_history.txt
```

## Step 7: Open Claude Code in the project folder

- **Desktop app:** in the Code tab, start a new session and choose the folder
  `C:\FYP\fyp-mimo-antenna-metasurface`.
- **Terminal version:**

  ```powershell
  cd C:\FYP\fyp-mimo-antenna-metasurface
  claude
  ```

Keep CST **installed but closed** when you start. Claude opens it through Python.

## Step 8: Paste the prompt

Copy everything in the box below into Notepad first. Replace the **two placeholders** with what you wrote down in Step 5:

- `<VERSION>` → for example `2024`
- `<CST install dir>` → for example `C:\Program Files (x86)\CST Studio Suite 2024`

Then paste the whole thing into Claude Code and press Enter.

```text
I'm doing a final-year project: a UWB 4-port MIMO antenna with an AMC metasurface, simulated in CST Studio Suite <VERSION> on this Windows machine. This repo is the project. Read CST_GUIDE.md first: it is the source of truth for every model, parameter, sweep, monitor and export filename. Also read analysis/make_figures.py to see the exact export formats it expects, and existing_single_history.txt (the CST History List of my current single antenna — use its dimensions as the nominal values).

GOAL: build every CST model from Python scripts using the CST Python API (cst.interface / cst.results, from "<CST install dir>\AMD64\python_cst_libraries"), so nobody builds anything by hand. Generate geometry by sending VBA history blocks with model3d.add_to_history(), so every step appears in CST's History List and stays editable.

LOCKED DESIGN DECISIONS (do not change):
- Band: UWB 3.1–10.6 GHz; simulate 2–12 GHz. Units mm/GHz/ns.
- Substrate FR-4 (lossy), εr 4.3, tanδ 0.025, 1.6 mm; copper (annealed) 0.035 mm everywhere.
- Single element: CPW-fed regular octagon (cylinder, Segments = 8, circumradius R). Parameters: Ws, Ls, hs, t, R, Lg (CPW ground length), Wf (feed width), g (CPW gap), d (ground-to-patch gap). Everything parametric, no hard-coded numbers.
- Waveguide port sized for CPW (covers feed + both gaps + part of grounds, ~5–6×hs above and below); confirm ~50 Ω line impedance.
- AMC unit cell: square ring (outer b, width wr) + centred square patch (a) on FR-4 1.6 mm with full copper ground, period p. Starting values p = 10, b = 9.4, wr = 0.6, a = 6. Frequency-domain solver, unit-cell boundaries in x/y, Floquet port at Zmax de-embedded to the cell surface.
- Single + reflector: N×N AMC under the board, air gap h (from antenna substrate bottom to AMC top copper). Three variants share one script: none / PEC plate / AMC. The port's downward extension must stay ≤ h − 0.5 mm.
- MIMO: square board Wb×Wb centred at the origin. Element 1 is fed at the bottom edge, offset by `off`; rotate-copy 90° ×3 about the z-axis, ports included (numbered counter-clockwise). Common ground through a central plus-shaped strip of width wc, also rotate-copied. Must be exactly 4-fold symmetric.
- MIMO + AMC: same, with the AMC lattice centred on the board.
- Time-domain solver for antennas. Mesh 15 cells/λ for sweeps and 20–25 for final runs; accuracy −40 dB. Sweeps run with farfield monitors OFF. MIMO sweeps excite port 1 only (symmetry); final MIMO runs excite all ports.
- Monitors for final runs: farfield and surface current at 4, 7, 10 GHz, plus farfields every 0.5 GHz from 2 to 12 GHz for gain/efficiency vs frequency.

WHAT TO BUILD (in a new cst/ folder):
1. cst/common.py: connect/new project, set units, frequency, materials, background/boundaries, mesh presets, helpers for parameters, VBA history, ports and monitors.
2. One script per model: build_single.py, build_unitcell.py, build_single_reflector.py (--variant none|pec|amc), build_mimo.py (--ms), each saving a .cst into cst/models/.
3. cst/run_and_export.py: runs a model or a parameter sweep (Lg, R, h, wc, as in CST_GUIDE.md) and exports results into exports/ with EXACTLY the filenames and formats CST_GUIDE.md §9 and make_figures.py expect (ASCII with #Parameters headers for sweeps, mimo_*.s4p Touchstone, far-field ASCII with Theta/Phi/Abs/Phase columns at 5° steps into exports/ff/).
4. A fallback: each build script can also write a plain .bas VBA macro (cst/macros/) that I can run via Macros → Run Macro if the Python API gives trouble.

HOW TO WORK:
- First check the CST version, its bundled Python path, and which Python versions its API supports. Set up a uv environment that can import cst.
- Build and verify ONE model at a time, in order: single → unit cell → single + reflector → MIMO → MIMO + AMC. After each, open it in CST and confirm the geometry has no overlapping or leftover solids, the ports are correct, and (single) the port line impedance is ~50 Ω. Run a short coarse simulation to confirm it solves.
- Ask me before any run longer than ~15 minutes.
- Keep the code simple: functions, type hints, no class hierarchies. Don't commit; I'll review first.
- Finish by adding a short "Automated build" section to CST_GUIDE.md with the exact commands.
```

## Step 9: During the session

- **Permission prompts:** Claude asks before running commands or editing files. Read each one and click **Allow**
  if it matches what Claude said it would do.
- **CST will open by itself.** Don't close it while Claude is working. When Claude asks you to check a model,
  look at it in CST (rotate the 3D view, look at the History List and the ports) and answer in the chat.
- **Long runs:** Claude asks before starting any simulation longer than ~15 minutes. The sweeps and the final
  MIMO runs take hours on this PC, so start those in the evening and leave the PC on overnight.
- **If the Python API won't work:** ask Claude to use the `.bas` fallback. In CST go to
  **Home → Macros → Run Macro** (or search `Run Macro` in the ribbon) and pick the file from `cst\macros\`.
- **If the session gets long or confused:** start a new session and say
  *"Continue the CST automation. Read CST_GUIDE.md and the cst/ folder to see where we are."*

## Step 10: Make the figures

When the `exports\` folder has results in it:

```powershell
cd C:\FYP\fyp-mimo-antenna-metasurface\analysis
uv run python make_figures.py
```

The figures are written to `figures\` (`.png` for slides, `.pdf` for the paper), and the key numbers to
`figures\summary.txt`. Missing export files are skipped, so you can run this at any stage.

## Step 11: Save your work back to GitHub

Claude won't commit by itself. When you've checked the changes:

```powershell
cd C:\FYP\fyp-mimo-antenna-metasurface
git status
git add cst CST_GUIDE.md existing_single_history.txt exports
git commit -m "Add automated CST build scripts and results"
git push
```

The first push asks you to sign in to GitHub in a browser window.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `winget`, `uv` or `claude` "is not recognized" | Close and reopen PowerShell. If it still fails, restart the PC. |
| "running scripts is disabled on this system" | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer `Y`, and try again. |
| `No module named 'cst'` | The install path in the prompt is wrong. Repeat Step 5 and tell Claude the correct path. |
| CST says the license is in use or not found | Close every other CST window and check that the license server or dongle is reachable, then try again. |
| A simulation never finishes | In CST, click **Stop** on the solver. Tell Claude and ask for a coarser mesh or a shorter frequency range for the test run. |
| `git push` is rejected | Run `git pull`, then `git push` again. |
