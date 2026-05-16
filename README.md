# Bangalore Air Quality Analysis and Dashboard

A 25-year analysis of urban air pollution in Bangalore, India, combining
ground-station sensor data, NASA satellite reanalysis, government monitoring
reports, and vehicle registration data.

The project now includes an interactive Streamlit dashboard for exploring
pollutant trends, data coverage, policy milestones, and vehicle-growth
relationships.

## Dashboard

Run the dashboard locally:

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

The dashboard uses `data/bangalore_master.csv` by default. You can also upload
a newer `bangalore_master.csv` from Colab using the sidebar uploader.

## Project Files

| File | Purpose |
| --- | --- |
| `dashboard.py` | Interactive Streamlit dashboard |
| `data/bangalore_master.csv` | Master annual dataset used by the dashboard |
| `01_openaq_fetch.ipynb` | Fetches and cleans OpenAQ station data |
| `02_merra2_fetch.ipynb` | Fetches MERRA-2 data and builds the master dataset |
| `03_analysis.ipynb` | Runs trend, forecasting, vehicle, and policy analysis |
| `05_summary_figure.png` | Static summary figure from the analysis notebook |

## Key Findings

- PM2.5 declines from the 2018 peak but remains above the WHO annual guideline.
- PM10 falls sharply after the BS-VI fuel-policy period.
- Vehicle registrations rise strongly while PM10 falls, suggesting cleaner
  emissions partly offset vehicle growth.
- PM2.5 has a strong seasonal pattern, with higher values before monsoon and
  lower values during monsoon.
- SO2 is useful descriptively, but cross-source consistency is limited before
  OpenAQ coverage.

## Data Sources

| Source | Coverage | Pollutants / Variables | Access |
| --- | --- | --- | --- |
| OpenAQ API / CPCB stations | 2018-2025 | PM2.5, PM10, NO2, SO2, O3, CO | Free API |
| NASA MERRA-2 | 2000-2025 | SO2 proxy | Earthdata account |
| KSPCB annual reports | 2012-2017 | PM10, NO2, SO2 | PDF extraction / manual entry |
| VAHAN registry | 2005-2024 | Registered vehicles | Portal download / manual entry |

## Known Limitations

- 2023-2024 CPCB/OpenAQ gaps are interpolated for PM2.5 and flagged in the
  dataset.
- 2018 PM10 is interpolated and flagged in the dataset.
- MERRA-2 PM2.5 was rejected as unreliable for Bangalore in the notebook
  analysis.
- SO2 comes from multiple sources and should not be treated as perfectly
  comparable across the full 2000-2025 period.

## Method Summary

- OpenAQ hourly readings are cleaned and resampled to annual means.
- MERRA-2 aerosol data is extracted for a Bangalore bounding box.
- KSPCB annual-report values are manually consolidated for pre-OpenAQ years.
- Vehicle-registration data is merged by year.
- Analysis includes trend tests, correlation, policy-event comparison, and
  PM2.5 forecasting.

## Summary Figure

![Summary](05_summary_figure.png)
