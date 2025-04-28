# Tema 1 – Sokoban  

> Acest fișier explică **instalarea**, **rularea minimă** cerută de fișa temei și opțiunile utile.

---

## 1 . Pre-rechizite rapide

```bash
python3 -m venv .venv
source .venv/bin/activate          # PowerShell: .venv\Scripts\Activate
pip install -r requirements.txt    # numpy, pandas, matplotlib, imageio, pyyaml …
```

---

## 2 . Rulare minimă (strict cerința PDF)

Algoritm + fișier YAML:

```bash
# LRTA*
python3 main.py lrta* tests/easy_map1.yaml

# Simulated Annealing
python3 main.py sa tests/easy_map1.yaml
```

La final veți vedea în terminal:

```
[lrta*] tests/easy_map1.yaml | h=base | time: 0.02s | steps: 157 | status: SOLVED
```

---

## 3 . Opțiuni utile (facultative)

| Flag              | Efect |
|-------------------|-------|
| `--heuristic enhanced` | folosește euristica cu componentă player |
| `--max-steps N`        | limitează bugetul de pași pentru LRTA* / Greedy |
| `--gif`                | salvează soluția ca GIF în `images/<hartă>.gif` |

Exemplu complet:

```bash
python3 main.py sa tests/hard_map1.yaml --heuristic base --gif
```

---

## 4 . Structura principală

```
.
├─ main.py                     # driver CLI
├─ search_methods/             # algoritmi + euristici
├─ sokoban/                    # librărie joc (cu modificările mele)
├─ tests/                      # fișiere .yaml
├─ images/                     # GIF-uri generate (la nevoie)
├─ plots/                      # PNG-uri grafice
├─ results_lrta.csv / results_sa.csv
├─ requirements.txt
└─ raport.pdf                  # documentul final
```

---

## 5 . Generarea graficelor din raport

```bash
python3 plot_results.py        # creează PNG-uri în plots/
```

---

## 6 . Notă reproducibilitate

* Toate valorile din raport sunt **media a 10 rulări** (seed-uri 0-9) per hartă.  
* Pentru Simulated Annealing seed-ul se setează cu `random.seed(seed+i)` la fiecare restart.

---
