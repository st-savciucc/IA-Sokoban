#!/usr/bin/env python3
"""
plot_results.py – generează automat graficele cantitative cerute în Tema 1 Sokoban

 ► INPUT-uri standard:
     results_lrta.csv   – agregate din rulările LRTA*
     results_sa.csv     – agregate din rulările Simulated Annealing
     (opţional) results_lrta_enh.csv, results_sa_enh.csv … pentru alte euristici
 ► OUTPUT:
     /plots/*.png       – imagini gata de inserat în PDF
     raport.txt         – sumar textual cu statisticile principale

Autor: <numele tău> – <data>
"""

import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from textwrap import dedent

# =============== CONFIG ============================
OUT_DIR = Path("plots")
OUT_DIR.mkdir(exist_ok=True)
CSV_FILES = {
    "LRTA*-base": "results_lrta.csv",
    "SA-base":    "results_sa.csv",
}
BAR_COLOR_ORDER = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]  
ROT = 25  


def _read_data():
    frames = []
    for label, csv in CSV_FILES.items():
        df = pd.read_csv(csv)
        df["Alg"] = label
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def _annotate_bars(ax):
    """
    Scrie numeric valoarea fiecărui bar la capăt (pentru grafice compacte).
    """
    for bar in ax.patches:
        h = bar.get_height()
        ax.annotate(f"{h:.0f}",
                    (bar.get_x() + bar.get_width() / 2, h),
                    ha="center", va="bottom", fontsize=8)


def barplot_metric(df, metric, ylabel, fname, title):
    # 1) Pregateste datele pivot
    pv = df.pivot(index="Test", columns="Alg", values=metric).sort_index()
    x = np.arange(len(pv.index))
    width = 0.8 / len(pv.columns)         

    # 2) Desen
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for i, col in enumerate(pv.columns):
        bars = ax.bar(x + i * width - width * (len(pv.columns)-1) / 2,
                      pv[col], width,
                      label=col,
                      color=BAR_COLOR_ORDER[i % len(BAR_COLOR_ORDER)])
    _annotate_bars(ax)

    ax.set_ylabel(ylabel)
    ax.set_xlabel("Hartă")
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(pv.index, rotation=ROT, ha="right")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"{fname}.png", dpi=300)
    plt.close(fig)


def lineplot_time(df, alg_label, metric="avg_time_s"):
    sub = df.loc[df["Alg"] == alg_label].sort_values("Test")
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(sub["Test"], sub[metric], marker="o", linewidth=2)
    for x, y in zip(sub["Test"], sub[metric]):
        ax.annotate(f"{y:.2f}s", (x, y), textcoords="offset points", xytext=(0, 6),
                    ha="center", fontsize=8)
    ax.set_xlabel("Hartă")
    ax.set_ylabel("Timp (s)")
    ax.set_title(f"Evoluţia timpilor de rulare – {alg_label}")
    ax.set_xticklabels(sub["Test"], rotation=ROT, ha="right")
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"time_evolution_{alg_label.replace('*','star')}.png", dpi=300)
    plt.close(fig)


def scatter_time_vs_steps(df):
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    for alg, g in df.groupby("Alg"):
        ax.scatter(g["avg_time_s"], g["avg_steps"], s=60,
                   label=alg, alpha=0.8)
        z = np.polyfit(g["avg_time_s"], g["avg_steps"], 1)
        p = np.poly1d(z)
        xs = np.linspace(g["avg_time_s"].min(), g["avg_time_s"].max(), 50)
        ax.plot(xs, p(xs), linewidth=1)
    ax.set_xlabel("Timp mediu (s)")
    ax.set_ylabel("Paşi medii")
    ax.set_title("Corelaţie timp – paşi (toate rulările)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "scatter_time_vs_steps.png", dpi=300)
    plt.close(fig)


def generate_plots():
    """
    Rulează toate graficele necesare şi salvează un scurt raport text.
    """
    df = _read_data()

    barplot_metric(
        df, metric="avg_steps",
        ylabel="Paşi medii",
        fname="bar_states",
        title="Număr de stări (paşi) explorate – comparaţie algoritmi"
    )

    first_alg = next(iter(CSV_FILES))
    lineplot_time(df, first_alg)

    barplot_metric(
        df, metric="avg_time_s",
        ylabel="Timp mediu (s)",
        fname="bar_times",
        title="Comparaţie timp de rezolvare"
    )

    scatter_time_vs_steps(df)

    summary = dedent(f"""
    --------- REZUMAT STATISTICI (medii) ---------------
    # Hărţi analizate : {df['Test'].nunique()}
    # Config. algoritmi: {df['Alg'].nunique()}
    -----------------------------------------------------
    """).lstrip()
    for alg, g in df.groupby("Alg"):
        summary += (f"{alg:<12} |  medieTimp = {g['avg_time_s'].mean():.3f} s"
                    f"   mediePaşi = {g['avg_steps'].mean():.0f}\n")
    (OUT_DIR / "raport.txt").write_text(summary, encoding="utf8")
    print(summary)


if __name__ == "__main__":
    generate_plots()
