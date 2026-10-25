# STA 571 HW 2: Trends in Mining Volume

This exploration uses the `mining-production.csv` from the [world mining monitor](https://github.com/kadoa-org/world-mining-monitor) github. A CSV download is availiable [here](https://www.kadoa.com/mining/production). More details can be found in `data/raw/provenanance.txt`.

The data contains the weight mined of 58 commodities from 2019 to 2026. Preprocessing converts the 82 different time periods to quarterly splits, and homogenized the mining weights to all be in kilogrammes. Since there is a large magnitude order difference between values such as kilo-ounces (koz) used for gold measurement, kilotonnes used by larger volume commodities such as iron and coal, and kilo karats used in gemstone minig, commodity volumes over time are compared on a log scale.

## Findings

Commodity mining volumes have been largely level over the past 7 years, with gold showing a slight increase in the last three. More commonly known commodities such as copper, gold, silver, and zinc are mined by more companies than less commonly known commodities such as liquid sulphur dioxide or chromite ( as seen in `figures/fig_8_timeline_top_10_commodities.png`). This might be due to to limited desposits of these commodities, more involved refinement processess, or limitations in the scope of the dataset.

On average, each individual company mines 5 different commodities. However, this distribution is right-skewed (see `figures/fig_0_density.png`), indicating most companies mine fewer than 5.

## Project Structure

``` text
├── data/
│   ├── processed/
│   │   └── time_and_kg_homogenized.csv
│   └── raw/
│       ├── mining-production.csv
│       └── provenance.txt
├── figures/
│   ├── fig_1_hist.png
│   ├── fig_2_gold_box.png
│   ├── fig_3_box_all_log.png
│   ├── fig_3_box_all.png
│   ├── fig_5_box_all_log_ordered.png
│   ├── fig_6_box_top_5.png
│   ├── fig_7_top_5_by_year.png
│   └── fig_8_timeline_top_10_commodities.png
├── notebooks/
│   └── HW_2_csv.ipynb
├── README.md
└── src/
    ├── __init__.py
    ├── __pycache__/
    │   ├── __init__.cpython-312.pyc
    │   └── utils.cpython-312.pyc
    └── utils.py
```

`src/utils.py` contains functions to clean and harmonize the data, as well as for graphing particular subsets.

## How to run the analysis

1. Ensure all data, notebook, and src files are present in their subfolders of your working directory.
2. Each cell in `HW_2_csv.ipynb` should be run sequentially from top to bottom to reproduce results.
