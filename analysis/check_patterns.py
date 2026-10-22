"""Check whether the patterns in the Tableau dashboard hold up statistically.

Uses the same bins as the workbook's calculated fields (Age Group, Formatted
Sleep End Time), then:
  1. prints mean sleep quality and row counts per bin and per cell,
  2. runs permutation tests on the gaps between groups,
  3. saves the figures used in the README to docs/.

Run from the repository root:  python analysis/check_patterns.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
QUALITY = "Sleep Quality"
WAKE_LABELS = ["Before 4 AM", "4-6 AM", "6-8 AM", "8-10 AM"]
AGE_LABELS = ["18-19", "20-29", "30-39", "40-49", "50+"]
N_PERMUTATIONS = 5000
rng = np.random.default_rng(543)


def load() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "sleep_cycle_productivity.csv")
    # Same cut points as the Tableau calculated fields. No row wakes after 10 AM.
    df["Wake Time"] = pd.cut(df["Sleep End Time"], [-np.inf, 4, 6, 8, 10],
                             right=False, labels=WAKE_LABELS)
    df["Age Group"] = pd.cut(df["Age"], [-np.inf, 20, 30, 40, 50, np.inf],
                             right=False, labels=AGE_LABELS)
    return df


def f_statistic(values: np.ndarray, groups: np.ndarray) -> float:
    """One-way ANOVA F statistic."""
    grand = values.mean()
    between, within = 0.0, 0.0
    labels = np.unique(groups)
    for g in labels:
        v = values[groups == g]
        between += len(v) * (v.mean() - grand) ** 2
        within += ((v - v.mean()) ** 2).sum()
    return (between / (len(labels) - 1)) / (within / (len(values) - len(labels)))


def permutation_p(df: pd.DataFrame, column: str) -> float:
    """Share of label shuffles that produce a between-group gap at least as large."""
    values = df[QUALITY].to_numpy(float)
    groups = df[column].astype(str).to_numpy()
    observed = f_statistic(values, groups)
    hits = sum(f_statistic(values, rng.permutation(groups)) >= observed
               for _ in range(N_PERMUTATIONS))
    return (hits + 1) / (N_PERMUTATIONS + 1)


def save_heatmap(df: pd.DataFrame) -> None:
    means = df.pivot_table(index="Age Group", columns="Wake Time", values=QUALITY,
                           aggfunc="mean", observed=False)
    counts = df.pivot_table(index="Age Group", columns="Wake Time", values=QUALITY,
                            aggfunc="count", observed=False)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    im = ax.imshow(means.to_numpy(), cmap="RdBu", vmin=4.5, vmax=6.5, aspect="auto")
    ax.set_xticks(range(len(WAKE_LABELS)), WAKE_LABELS)
    ax.set_yticks(range(len(AGE_LABELS)), AGE_LABELS)
    ax.set_xlabel("Wake-up time (Sleep End Time)")
    ax.set_ylabel("Age group")
    for i in range(len(AGE_LABELS)):
        for j in range(len(WAKE_LABELS)):
            ax.text(j, i, f"{means.iat[i, j]:.2f}\nn={counts.iat[i, j]}",
                    ha="center", va="center", fontsize=9)
    fig.colorbar(im, ax=ax, label="Mean sleep quality (1-10)")
    ax.set_title("Mean sleep quality by age group and wake-up time")
    fig.tight_layout()
    fig.savefig(DOCS / "heatmap_age_wake.png", dpi=150)
    plt.close(fig)


def save_line_chart(df: pd.DataFrame) -> None:
    """Recreates the Tableau line chart, including its zoomed-in y-axis."""
    means = df.pivot_table(index="Wake Time", columns="Age Group", values=QUALITY,
                           aggfunc="mean", observed=False)
    colors = ["#4e79a7", "#f28e2b", "#59a14f", "#76b7b2", "#edc948"]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for age, color in zip(AGE_LABELS, colors):
        ax.plot(range(len(WAKE_LABELS)), means[age], marker="o", markersize=4,
                linewidth=2, color=color, label=age)
    ax.set_xticks(range(len(WAKE_LABELS)), WAKE_LABELS)
    ax.set_ylim(4.7, 5.9)
    ax.set_xlabel("Wake-up time (Sleep End Time)")
    ax.set_ylabel("Average sleep quality")
    ax.grid(axis="y", color="#e6e6e6")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Age group", frameon=False, bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.set_title("How wake-up time affects sleep quality across age groups")
    fig.tight_layout()
    fig.savefig(DOCS / "line_wake_quality.png", dpi=150)
    plt.close(fig)


def save_box_dots(df: pd.DataFrame) -> None:
    """Recreates the Tableau box plot with one orange dot per score, shaded by row count."""
    fig, ax = plt.subplots(figsize=(8, 4.6))
    groups = [df.loc[df["Age Group"] == age, QUALITY] for age in AGE_LABELS]
    ax.boxplot(groups, positions=range(len(AGE_LABELS)), widths=0.45, patch_artist=True,
               showfliers=False, medianprops={"color": "#555555", "linewidth": 2},
               boxprops={"facecolor": "#d9d9d9", "edgecolor": "#9e9e9e"},
               whiskerprops={"color": "#555555"}, capprops={"color": "#555555"})
    most = max(g.value_counts().max() for g in groups)
    for x, g in enumerate(groups):
        for score, count in g.value_counts().items():
            ax.scatter(x, score, s=160, color="#f28e2b", alpha=0.25 + 0.6 * count / most,
                       edgecolors="none", zorder=3)
    ax.set_xticks(range(len(AGE_LABELS)), AGE_LABELS)
    ax.set_yticks(range(1, 11))
    ax.set_xlabel("Age group")
    ax.set_ylabel("Sleep quality (1-10)")
    ax.grid(axis="y", color="#e6e6e6")
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("How sleep quality varies across age groups")
    fig.tight_layout()
    fig.savefig(DOCS / "box_age_quality.png", dpi=150)
    plt.close(fig)


def save_reality_check(df: pd.DataFrame) -> None:
    fig, (left, right) = plt.subplots(1, 2, figsize=(10, 4))

    counts = df[QUALITY].value_counts().sort_index()
    left.bar(counts.index, counts.to_numpy(), color="#4e79a7")
    left.set_xticks(range(1, 11))
    left.set_xlabel("Sleep quality score")
    left.set_ylabel("Rows")
    left.set_title("Scores are spread evenly from 1 to 10")

    stats = df.groupby("Wake Time", observed=False)[QUALITY].agg(["mean", "std", "count"])
    ci = 1.96 * stats["std"] / np.sqrt(stats["count"])
    right.errorbar(range(len(stats)), stats["mean"], yerr=ci, fmt="o-",
                   color="#e15759", capsize=4)
    right.set_xticks(range(len(stats)), stats.index)
    right.set_ylim(1, 10)
    right.axhline(df[QUALITY].mean(), color="grey", linestyle="--", linewidth=1)
    right.set_xlabel("Wake-up time")
    right.set_ylabel("Mean sleep quality (95% CI)")
    right.set_title("On the full 1-10 scale the gaps are small")

    fig.tight_layout()
    fig.savefig(DOCS / "reality_check.png", dpi=150)
    plt.close(fig)


def main() -> None:
    df = load()
    print(f"{len(df)} rows, {df['Person_ID'].nunique()} people, "
          f"{df['Date'].min()} to {df['Date'].max()}\n")

    for column in ("Wake Time", "Age Group"):
        print(df.groupby(column, observed=False)[QUALITY]
              .agg(["mean", "median", "count"]).round(2), "\n")

    print("Mean sleep quality, age group x wake-up time:")
    print(df.pivot_table(index="Age Group", columns="Wake Time", values=QUALITY,
                         aggfunc="mean", observed=False).round(2), "\n")

    print("Correlation of sleep quality with every numeric column:")
    print(df.select_dtypes("number").corr()[QUALITY].drop(QUALITY).round(3), "\n")

    for column in ("Wake Time", "Age Group"):
        print(f"Permutation test, {column}: p = {permutation_p(df, column):.3f}")

    DOCS.mkdir(exist_ok=True)
    save_heatmap(df)
    save_line_chart(df)
    save_box_dots(df)
    save_reality_check(df)
    print(f"\nFigures saved to {DOCS.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
