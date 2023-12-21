# unisg skills programming group project

Skills: Programming 2023

## Project

-   This project is designed as a simple stock portfolio analysis tool
    -   Portfolio analyses can be round for any desired constituents,
        constituent weights, benchmarks, or time horizons
    -   Analyses include:
        -   Various portfolio performance metrics and comparisons vs. benchmark
        -   Various constituents info and performance and risk metrics
        -   Various outputs, such as plots as well as an Excel overview

## Get started

-   Clone the project
-   install all requirements in requirements.txt
-   Set up your own portfolio in Input/portfolio.xlsx
-   See PortfolioAnalyser.ipynb for concrete examples

## Data Sourcing

-   All data is sourced through the yfinance library
-   All requests are simplified through functions in Utils/Sourcing/Yahoo.py

## Project structure

<pre>

.
├── Input
│   ├── portfolio.xlsx
│   └── template.xlsx
├── Output
│   └── portfolio_overview.xlsx
├── PortfolioAnalyser.ipynb
├── README.md
├── Utils
│   ├── Portfolio
│   │   ├── Formatting.py
│   │   ├── Portfolio.py
│   │   ├── Stats.py
│   │   ├── __init__.py
│   └── Sourcing
│       ├── Yahoo.py
│       ├── __init__.py
└── requirements.txt

<pre>
