# NumPy-Day: 20-Notebook Learning Project

A structured NumPy learning path covering array fundamentals, indexing, vectorization, statistics, performance, and an end-to-end dataset analysis.

## Project structure

```text
NumPy-Day/
├── data/
│   └── processed/             # Created by capstone notebook
├── notebooks/                 # 20 learning notebooks
├── src/                       # Add reusable project modules here
├── benchmark.py               # Standalone loop vs vectorization benchmark
├── README.md
├── requirements.txt
└── .gitignore
```

## Keep dependencies minimal

The previous requirements file looks like a full Jupyter environment snapshot. It includes many transitive packages, web libraries, and visualization packages that are not direct requirements for this NumPy-focused project.

For this project, keep only direct dependencies:

- `numpy`: array computing, statistics, random generation, linear algebra.
- `jupyter`: run notebooks locally.
- `ipykernel`: register the Python environment as a notebook kernel.

Jupyter will install its own dependencies. Do not manually list every transitive dependency unless you are deliberately maintaining a fully locked environment. If you later add plotting, add `matplotlib`; if you add tabular data workflows, consider `pandas` separately.

## Windows PowerShell setup

Open PowerShell:

```powershell
Set-Location E:\NumPy-Day

# Create an isolated environment in the project folder
py -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# If PowerShell blocks activation, use this only for the current terminal:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name numpy-day --display-name "Python (NumPy-Day)"
```

If `py` is not available, use `python -m venv .venv` with your installed Python. Confirm the environment:

```powershell
python --version
python -m pip --version
python -c "import numpy as np; print(np.__version__)"
```

## Launch notebooks

```powershell
jupyter notebook
```

Open the `notebooks` folder in the browser, then work through notebooks `01` to `20` in order. Select the **Python (NumPy-Day)** kernel if prompted.

## Run the standalone benchmark

```powershell
python benchmark.py
```

The benchmark compares equivalent calculations, reports median runtime across multiple trials, and checks numerical agreement. Your speedup will depend on hardware, array size, NumPy build, and system load.

## Recommended workflow

1. Complete each notebook in order.
2. Run every code cell yourself; do not just read the outputs.
3. Complete each practice prompt in a new cell.
4. Add notes in Markdown cells explaining what each operation does and when you would use it.
5. Keep generated outputs out of Git unless they are intentionally part of the deliverable.
6. Commit the notebook source, README, requirements, and benchmark script.

## Notebook index

1. Setup and first array
2. Array creation
3. Attributes, dtypes, and memory
4. Indexing and slicing
5. Reshaping, flattening, and transposing
6. Element-wise math and ufuncs
7. Broadcasting
8. Aggregations and axis
9. Statistical calculations
10. Sorting, searching, and unique values
11. Boolean masks and `np.where`
12. Fancy indexing
13. Random numbers and reproducibility
14. Missing values and data cleaning
15. Linear algebra
16. Concatenating, stacking, and splitting
17. File I/O and a simple data pipeline
18. Vectorization vs. Python loops
19. Memory efficiency, views, and copies
20. Capstone statistical analysis pipeline

## Notes

- Notebooks 17 and 20 write generated files into `data/` paths relative to the notebook working directory. Launch Jupyter from the project root so these paths resolve correctly.
- The capstone dataset is synthetic and is intended for learning, not operational decision-making.
- Avoid using `allow_pickle=True` with untrusted NumPy files.
