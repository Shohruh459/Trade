# grid-scalper-ea (Python port, Gold_Optimized.set): natijalar (STRATEGY_GRIDEA.md)

## Butun davr 2018-01 → 2025-02, balans $5,000, spred $0.30, swap 3%
| variant           |   final |   profit_pct |   maxdd_pct |   dd_stops |   blown |   max_oz |   pos_months_pct |   worst_month_pct |   longest_under_d |
|:------------------|--------:|-------------:|------------:|-----------:|--------:|---------:|-----------------:|------------------:|------------------:|
| Sell-only (.set)  |       0 |       -100   |       100   |          5 |       1 |       60 |             66.7 |            -100   |              1984 |
| Buy-only          |   19685 |        293.7 |        69.3 |         63 |       0 |       60 |             62.8 |             -33.1 |              1275 |
| Both (EA default) |       0 |       -100   |       100   |         68 |       1 |       80 |             52.9 |            -100   |              1472 |

## Yillik foyda ($, asosiy Sell-only)
| time                |   pnl |
|:--------------------|------:|
| 2018-12-31 00:00:00 |   565 |
| 2019-12-31 00:00:00 | -5565 |
| 2020-12-31 00:00:00 |     0 |
| 2021-12-31 00:00:00 |     0 |
| 2022-12-31 00:00:00 |     0 |
| 2023-12-31 00:00:00 |     0 |
| 2024-12-31 00:00:00 |     0 |
| 2025-12-31 00:00:00 |     0 |

## Stress ($0.50 / swap 5%), Sell-only: {'final': 0.0, 'profit_pct': np.float64(-100.0), 'maxdd_pct': 100.0, 'dd_stops': 18, 'blown': 1, 'max_oz': 60.0, 'pos_months_pct': 58.1, 'worst_month_pct': -100.0, 'longest_under_d': 1984}

## Balans $3,000, Sell-only: {'final': 0.0, 'profit_pct': np.float64(-100.0), 'maxdd_pct': 100.0, 'dd_stops': 4, 'blown': 1, 'max_oz': 60.0, 'pos_months_pct': 66.7, 'worst_month_pct': -100.0, 'longest_under_d': 1984}

## Yarmlar (Sell-only): 2018–2021: {'final': 0.0, 'profit_pct': np.float64(-100.0), 'maxdd_pct': 100.0, 'dd_stops': 5, 'blown': 1, 'max_oz': 60.0, 'pos_months_pct': 66.7, 'worst_month_pct': -100.0, 'longest_under_d': 1001}

2022–2025: {'final': 0.0, 'profit_pct': np.float64(-100.0), 'maxdd_pct': 100.0, 'dd_stops': 12, 'blown': 1, 'max_oz': 60.0, 'pos_months_pct': 38.5, 'worst_month_pct': -100.0, 'longest_under_d': 721}

## 12 oylik oynalar (har chorak boshlanishidan, $5,000 dan qayta)
| variant           |   oynalar |   foydali_pct |   eng_yomon |   median |   eng_yaxshi |   dd_stops_jami |
|:------------------|----------:|--------------:|------------:|---------:|-------------:|----------------:|
| Both (EA default) |        25 |            32 |        -100 |     -100 |        252.3 |             312 |
| Sell-only (.set)  |        25 |            28 |        -100 |     -100 |        115.8 |             154 |

## Mezonlar (asosiy Sell-only)
- G1 sof foyda>0: YO`Q
- G2 maxDD<=30%: YO`Q
- G3 DD-stop<=5 va bankrot yo'q: YO`Q
- G4 12 oylik: >=70% foydali va eng yomon>=-20%: YO`Q
- G5 stress foyda>0: YO`Q
- G6 ikki yarim foydali: YO`Q

**Xulosa: O'TMADI**
