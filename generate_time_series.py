#!/usr/bin/env python3

import pandas as pd
from datetime import date

def main():
    lrta_df = pd.read_csv('results_lrta.csv')
    sa_df   = pd.read_csv('results_sa.csv')

    today = date.today().isoformat()

    lrta_ts = lrta_df[['Test', 'avg_time_s']].copy()
    lrta_ts['Algorithm'] = 'LRTA*'

    sa_ts = sa_df[['Test', 'avg_time_s']].copy()
    sa_ts['Algorithm'] = 'SA'

    combined = pd.concat([lrta_ts, sa_ts], ignore_index=True)
    combined['Date'] = today

    combined = combined.rename(columns={'avg_time_s': 'Time'})
    combined = combined[['Date', 'Algorithm', 'Test', 'Time']]

    combined.to_csv('time_series.csv', index=False)
    print("✅ Fișierul `time_series.csv` a fost generat cu succes!")

if __name__ == '__main__':
    main()
