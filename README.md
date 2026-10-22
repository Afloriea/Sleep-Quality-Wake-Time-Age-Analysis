# Sleep Quality vs Wake-Up Time and Age

A Tableau analysis of whether the time people wake up, and their age, relate to how well they sleep, built on a 5,000-row sleep and productivity dataset. After building the dashboard, I checked the patterns statistically in Python and found they don't hold up. The data turned out to be synthetic, and the write-up explains how to tell.

**Skills shown:** Tableau (calculated fields, heatmaps, box plots, highlight actions) · exploratory data analysis · binning and segmentation · Python (pandas, matplotlib) · permutation testing · sanity-checking a dataset before drawing conclusions

---

## 📌 At a glance

| | |
|---|---|
| **Question** | Does wake-up time affect sleep quality, and does that differ by age group? |
| **Data** | 5,000 sleep records for 3,858 people across 2024, 15 columns ([`data/`](data/)) |
| **Tools** | Tableau for the dashboard, Python for the statistical check |
| **Result** | The dashboard shows gaps of up to one point between groups, but none of them is statistically significant, and sleep quality has no correlation (\|r\| < 0.02) with any other column |
| **Context** | Course final project: dashboard built in Tableau, statistical check added afterwards in Python |

![Mean sleep quality by age group and wake-up time](docs/heatmap_age_wake.png)

---

## ❓ Question and approach

The project looks at how sleep habits relate to productivity and well-being. This part asks: **do people who wake up at different times sleep better or worse, and is that the same for every age?**

In Tableau I created two calculated fields to segment the data:

```
// Formatted Sleep End Time
IF [Sleep End Time] < 4 THEN "Before 4 AM"
ELSEIF [Sleep End Time] < 6 THEN "4-6 AM"
ELSEIF [Sleep End Time] < 8 THEN "6-8 AM"
ELSEIF [Sleep End Time] < 10 THEN "8-10 AM"
ELSE "After 10 AM" END

// Age Group: 18-19, 20-29, 30-39, 40-49, 50+
```

and built four linked views on one dashboard:

| View | What it shows |
|---|---|
| Line chart | Mean sleep quality by wake-up time, one line per age group |
| Heatmap | Age group × wake-up time, coloured by sleep quality |
| Box plot | Distribution of sleep quality within each age group |
| Bar chart | How wake-up times are distributed in each age group |

Selecting a mark in one view highlights the same age group and wake-up time in the others (a dashboard highlight action).

---

## 📊 What the dashboard shows

The two charts below are recreated in Python from the dashboard's line chart and box plot, with the same bins and layout.

![Average sleep quality by wake-up time, one line per age group](docs/line_wake_quality.png)

- **Waking between 4 and 8 AM** goes with the highest average sleep quality (≈ 5.6 out of 10). Waking **before 4 AM** (5.43) or **after 8 AM** (5.26) is lower.

![Box plot of sleep quality by age group, with one dot per score shaded by number of people](docs/box_age_quality.png)

- **Age groups look almost the same** overall, from 5.39 (18-19) to 5.58 (20-29). The boxes overlap almost completely, and every score from 1 to 10 is about equally common in every group.
- **The largest gaps are in small cells.** For example, 18-19 year olds waking at 8-10 AM average 4.86, but that cell holds only 21 people.

---

## 🔍 Do the patterns hold up?

Before turning these into recommendations, I checked them in Python ([`analysis/check_patterns.py`](analysis/check_patterns.py)) using the same bins as the Tableau fields.

![Distribution of sleep quality scores and mean by wake-up time](docs/reality_check.png)

| Check | Result | What it means |
|---|---|---|
| Permutation test, wake-up time (5,000 shuffles) | p = 0.12 | Gaps this size appear often by chance |
| Permutation test, age group | p = 0.81 | No age effect |
| Correlation of sleep quality with every other column | all \|r\| < 0.02 | Not even total sleep hours or stress relate to it |
| Distribution of sleep quality | 480–521 rows for each score from 1 to 10 | Almost perfectly uniform, unlike real survey data |

The line chart above uses the dashboard's zoomed-in y-axis (4.7 to 5.9), which makes gaps of a few tenths look steep. On the full 1–10 scale (right panel) the same means are almost flat.

**Conclusion:** the dataset is almost certainly synthetic, with sleep quality generated independently of the other columns. The patterns in the dashboard are noise, so they shouldn't drive any recommendation. With real data, the same dashboard and checks would show whether the 4–8 AM pattern is genuine.

**What I'd take from this:** a clean-looking chart isn't evidence by itself. Checking sample sizes per cell, testing gaps against chance and looking at the raw distribution should come before drawing a conclusion.

---

## 📚 The full project workbook

This analysis is one chapter of a larger Tableau story on sleep and productivity, included as [`tableau/sleep-cycle-and-productivity-full-story.twbx`](tableau/sleep-cycle-and-productivity-full-story.twbx). Its cover page lists all contributors. Using the same dataset, the story also covers:

- Sleep quality vs sleep hours by age group and gender
- Screen time before bed vs sleep quality and productivity
- Exercise duration and its link to sleep quality and productivity by age group
- Stress and work hours vs sleep quality

The same caveat applies to every chapter: sleep quality isn't correlated with any of these columns in this dataset.

---

## 🗂 Repository

```
data/
└── sleep_cycle_productivity.csv                 source data (5,000 rows)
tableau/
├── sleep-quality-vs-wake-time-and-age.twbx      this analysis, data packaged in
└── sleep-cycle-and-productivity-full-story.twbx the full Tableau story
analysis/
└── check_patterns.py                            statistical check and README figures
docs/
├── box_age_quality.png
├── heatmap_age_wake.png
├── line_wake_quality.png
└── reality_check.png
```

## ▶️ How to explore it

- **Tableau dashboard:** open `tableau/sleep-quality-vs-wake-time-and-age.twbx` in Tableau Desktop or the free [Tableau Public](https://public.tableau.com/app/learn/how-to-videos) app. The data is packaged inside the workbook. Open `sleep-cycle-and-productivity-full-story.twbx` and go to the *Final Story* tab for the full project.
- **Statistical check:**

  ```bash
  pip install -r requirements.txt
  python analysis/check_patterns.py
  ```

  It prints the tables and test results above and regenerates the figures in `docs/`.

## 🧭 Limitations

- The data appears to be synthetic, so no real-world conclusion can be drawn from it.
- Wake-up times run from 12:30 AM to 9:30 AM, so the "After 10 AM" bin is empty. Very early wake-ups reflect sleep start times between 8 PM and midnight.
- The figures in this README are recreated in Python from the same data and bins as the Tableau views.

## 💻 Tech stack

Tableau · Python · pandas · NumPy · matplotlib
