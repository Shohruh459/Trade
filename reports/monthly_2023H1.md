# Oylik hisobot: EUR/USD H1

Ma'lumot: 2023-01-01 00:00:00+00:00 … 2023-07-07 23:00:00+00:00, 4416 ta shamdan. Boshlang'ich balans $10,000, risk 1%, spred 0.8 pip, slippage 0.2 pip/tomon, komissiya $7.0/lot.

Standart parametrlar, hech narsa optimallashtirilmagan. Daromad realizatsiya qilingan bitimlar bo'yicha, oyga bitim yopilgan sanasi bo'yicha.


## Umumiy taqqoslash

| strategiya   |   trades |   win_rate |   profit_factor |   net_pct |   max_dd_pct |   avg_r | dd_bilan_to'xtagan   |
|:-------------|---------:|-----------:|----------------:|----------:|-------------:|--------:|:---------------------|
| A            |       25 |      0.2   |            0.45 |     -11.1 |         11.1 |  -0.463 | False                |
| B            |       38 |      0.211 |            0.45 |     -15.6 |         15.6 |  -0.438 | True                 |

## Strategiya A

| oy      |   bitimlar |   yutuq |   zarar |   foyda_$ |   o'rtacha_R |   eng_yaxshi_$ |   eng_yomon_$ |
|:--------|-----------:|--------:|--------:|----------:|-------------:|---------------:|--------------:|
| 2023-01 |          7 |       1 |       6 |   -436.2  |        -0.63 |         181.73 |       -107.92 |
| 2023-02 |          3 |       1 |       2 |    -22.6  |        -0.07 |         181.45 |       -105.19 |
| 2023-03 |          3 |       1 |       2 |    -14.08 |        -0.04 |         182.49 |        -98.76 |
| 2023-04 |          6 |       2 |       4 |    -44.74 |        -0.07 |         186.25 |       -105.4  |
| 2023-05 |          2 |       0 |       2 |   -203.55 |        -1.08 |         -98.6  |       -104.96 |
| 2023-06 |          1 |       0 |       1 |    -97.55 |        -1.05 |         -97.55 |        -97.55 |
| 2023-07 |          3 |       0 |       3 |   -292.21 |        -1.07 |         -94.54 |        -99.7  |

Jami: 25 bitim, yutuq ulushi 20%, profit factor 0.45, sof natija -11.1%, maksimal drawdown 11.1%, o'rtacha R -0.463.


## Strategiya B

| oy      |   bitimlar |   yutuq |   zarar |   foyda_$ |   o'rtacha_R |   eng_yaxshi_$ |   eng_yomon_$ |
|:--------|-----------:|--------:|--------:|----------:|-------------:|---------------:|--------------:|
| 2023-01 |          7 |       0 |       7 |   -704.2  |        -1.04 |         -97.65 |       -104.86 |
| 2023-02 |         11 |       3 |       8 |   -342.65 |        -0.33 |         186.12 |       -103.31 |
| 2023-03 |         11 |       4 |       7 |     53.13 |         0.06 |         177.26 |        -94.47 |
| 2023-04 |          8 |       1 |       7 |   -476.03 |        -0.67 |         176.45 |        -96.6  |
| 2023-05 |          1 |       0 |       1 |    -89.76 |        -1.05 |         -89.76 |        -89.76 |

Jami: 38 bitim, yutuq ulushi 21%, profit factor 0.45, sof natija -15.6%, maksimal drawdown 15.6%, o'rtacha R -0.438.
