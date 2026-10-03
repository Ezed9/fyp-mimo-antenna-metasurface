# Windows Setup: Automating the CST Models with Claude Code

Follow these steps on the **Windows PC that has CST Studio Suite installed**. At the end, Claude Code writes
Python scripts that build every CST model automatically (see `CST_GUIDE.md` for what the models are).

> **Written for CST Studio Suite 2019.** CST 2019 doesn't have the `cst.interface` Python library (it arrived in
> CST 2020). So the scripts control CST in one of two ways, and Claude tests which one works on your PC:
> 1. **Python → COM:** Python starts CST through Windows COM (`pywin32`) and sends it VBA commands. Fully automatic.
> 2. **Python → `.bas` macro:** Python writes a VBA macro file and you run it in CST with one click.
>
> Both put every modelling step into CST's History List, so the models stay editable.

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

You don't need to install Python yourself. uv downloads it, and Claude adds `pywin32` (the COM library) to the project.

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

1. Open CST Studio Suite and go to **File → Help → About** (or the **?** icon at the top right).
   Check that it says **2019** and note the service pack if one is shown (for example `SP 5`).
2. Find the install folder. Right-click the CST desktop shortcut → **Open file location**. It's usually one of these:
   - `C:\Program Files (x86)\CST STUDIO SUITE 2019`
   - `C:\Program Files\CST STUDIO SUITE 2019`
3. Check that CST's main program is in that folder (change the path to match yours):

   ```powershell
   dir "C:\Program Files (x86)\CST STUDIO SUITE 2019\CST DESIGN ENVIRONMENT.exe"
   ```

   If you get "cannot find path", try the other path from step 2.

Write down the full install folder path. You'll need it in Step 8.

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

Copy everything in the box below into Notepad first. Replace the **one placeholder** with what you wrote down in Step 5:

- `<CST install dir>` → for example `C:\Program Files (x86)\CST STUDIO SUITE 2019`

Then paste the whole thing into Claude Code and press Enter.

```text
I'm doing a final-year project: a UWB 4-port MIMO antenna with an AMC metasurface, simulated in CST Studio Suite 2019 on this Windows machine, installed at "<CST install dir>". This repo is the project. Read CST_GUIDE.md first: it is the source of truth for every model, parameter, sweep, monitor and export filename (its menu names are from CST 2020–2024, so they can differ slightly in 2019). Also read analysis/make_figures.py to see the exact export formats it expects, and existing_single_history.txt (the CST History List of my current single antenna — use its dimensions as the nominal values).

GOAL: build every CST model from Python scripts, so nobody builds anything by hand. CST 2019 has NO cst.interface Python library (that started in CST 2020), so do not use it. Instead, Python generates the VBA for each modelling step and adds it to CST's History List with AddToHistory, so every step appears in the History List and stays editable. Two ways to deliver that VBA, sharing the same generator code:
- Primary: Python drives CST over Windows COM with pywin32 (win32com.client.Dispatch("CSTStudio.Application"), NewMWS / OpenFile, AddToHistory, Solver, SaveAs). CST's COM objects have no type info, so methods may need _FlagAsMethod or late-bound Invoke.
- Fallback: Python writes a plain .bas VBA macro that I run via Macros → Run Macro in CST.
Before building anything, write a tiny COM smoke test (start CST, new project, add one brick via AddToHistory, save, close) and tell me whether COM works. If it doesn't, use the .bas route for everything.

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
1. cst/common.py: VBA generators for units, frequency, materials, background/boundaries, mesh presets, parameters, ports and monitors, plus the COM connect/new/open/save helpers and a function that writes the same steps to a .bas file.
2. One script per model: build_single.py, build_unitcell.py, build_single_reflector.py (--variant none|pec|amc), build_mimo.py (--ms). Each one builds over COM and saves a .cst into cst/models/, or with --macro writes cst/macros/<model>.bas instead.
3. cst/run_and_export.py: runs a model or a parameter sweep (Lg, R, h, wc, as in CST_GUIDE.md) and exports results into exports/ with EXACTLY the filenames and formats CST_GUIDE.md §9 and make_figures.py expect (ASCII with #Parameters headers for sweeps, mimo_*.s4p Touchstone, far-field ASCII with Theta/Phi/Abs/Phase columns at 5° steps into exports/ff/). Use CST 2019 VBA for exports (e.g. SelectTreeItem + ASCIIExport, the TOUCHSTONE object, FarfieldPlot ASCII export). If COM doesn't work, write this as .bas macros too.

HOW TO WORK:
- First confirm the CST 2019 install path and run the COM smoke test. Set up a uv environment in cst/ with pywin32 (any current Python works, since COM doesn't depend on CST's Python).
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
- **If COM doesn't work (the `.bas` route):** Claude writes macro files into `cst\macros\`. To run one:
  1. In CST, make a new empty project: **File → New and Recent → New Project** (any template; the macro sets everything).
  2. Go to **Home → Macros → Run Macro…** (or type `Macro` in the ribbon search box).
  3. Pick the `.bas` file from `C:\FYP\fyp-mimo-antenna-metasurface\cst\macros\` and click **Open**.
  4. Check that the History List fills with steps and the model appears. Save with **File → Save As** into `cst\models\`.
  5. If CST shows an error, copy its message (or take a screenshot) and paste it into the Claude chat.
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
| COM test fails ("Invalid class string" or CST never opens) | Run CST once normally so it registers itself, then retry. If it still fails, tell Claude to use the `.bas` route. |
| A `.bas` macro stops with a VBA error | Copy the error text and the line number into the Claude chat. |
| CST says the license is in use or not found | Close every other CST window and check that the license server or dongle is reachable, then try again. |
| A simulation never finishes | In CST, click **Stop** on the solver. Tell Claude and ask for a coarser mesh or a shorter frequency range for the test run. |
| `git push` is rejected | Run `git pull`, then `git push` again. |
