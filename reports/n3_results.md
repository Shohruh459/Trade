# N3: oltin M1 swing-trend, ATR kun filtri, kunlik ±10% (STRATEGY_N3.md)

Savdoli kunlar ulushi / ATR filtri o'tkazib yuborgan kunlar: gate o'tgan 46.3% kun (jami 1849 kun).

## Asosiy qoida (xarajat $0.30, risk 1%)
| davr          |    N |   meanR |   win_pct |    PF |   p_one |   maxlev |   ret_pct |   maxDD_pct |   pos_months_pct |   worst_month_pct |   max_loss_streak_m |   days_hit_up |   days_hit_dn |   traded_days |   days |
|:--------------|-----:|--------:|----------:|------:|--------:|---------:|----------:|------------:|-----------------:|------------------:|--------------------:|--------------:|--------------:|--------------:|-------:|
| Dev 2018-21   | 3968 | -0.2355 |      38.9 | 0.618 |       1 |       48 |    -100   |       100   |              4.2 |             -51.7 |                  26 |             0 |             5 |           448 |   1033 |
| Val 2022-23   | 2202 | -0.1496 |      40.9 | 0.74  |       1 |       38 |     -96.9 |        96.9 |              8.3 |             -41.2 |                  15 |             0 |             1 |           246 |    515 |
| Final 2024-25 | 1528 | -0.1538 |      39.8 | 0.723 |       1 |       37 |     -91.4 |        91.7 |              7.1 |             -30.4 |                  12 |             0 |             3 |           163 |    301 |
| Qaror 2022-25 | 3730 | -0.1513 |      40.5 | 0.733 |       1 |       38 |     -99.7 |        99.7 |              7.9 |             -41.2 |                  15 |             0 |             4 |           409 |    816 |

## Stress ($0.50), qaror davri: meanR -0.2418, p 1.0, maxDD 100.0%

## Tasodifiy kirish nazorati (1000): real meanR -0.1513; tasodifiy o'rtacha -0.1331 (5–95%: -0.1596 … -0.1060); p = 0.855

## Mezonlar
- C1 meanR>0, p<=0.10, N>=200: YO`Q
- C2 stress meanR>0: YO`Q
- C3 Val va Final alohida meanR>0: YO`Q
- C4 Dev ishonchli manfiy emas: YO`Q
- C5 random control p<=0.10: YO`Q
- C6 maxDD<=30% (qaror): YO`Q

**Xulosa: FAIL**

## Sezgirlik (qaror davri, faqat ma'lumot)
| variant           |    N |   meanR |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |   days_hit_up |   days_hit_dn |
|:------------------|-----:|--------:|--------:|----------:|------------:|-----------------:|--------------:|--------------:|
| ATR filtrisiz     | 7242 | -0.1778 |       1 |    -100   |       100   |              0   |             0 |             6 |
| risk 0.5%         | 3732 | -0.1513 |       1 |     -94.5 |        94.4 |              7.9 |             0 |             0 |
| risk 2%           | 3656 | -0.1451 |       1 |    -100   |       100   |              7.9 |             0 |            81 |
| TP 1.0R           | 4268 | -0.1353 |       1 |     -99.8 |        99.8 |              5.3 |             0 |             3 |
| TP 2.0R           | 3523 | -0.1387 |       1 |     -99.4 |        99.4 |             21.1 |             0 |             4 |
| fractal k=3       | 5466 | -0.1941 |       1 |    -100   |       100   |              2.6 |             0 |            27 |
| fractal k=8       | 2607 | -0.0968 |       1 |     -93.1 |        93.3 |             31.6 |             0 |             0 |
| faqat long        | 1991 | -0.1971 |       1 |     -98.3 |        98.2 |              7.9 |             0 |             0 |
| faqat short       | 1866 | -0.127  |       1 |     -91.7 |        92.1 |             28.9 |             0 |             0 |
| kunlik chegarasiz | 3732 | -0.1513 |       1 |     -99.7 |        99.7 |              7.9 |             0 |             0 |

## Yillar bo'yicha (qaror davri)
|   date |   count |    mean |
|-------:|--------:|--------:|
|   2022 |    1186 | -0.1575 |
|   2023 |    1016 | -0.1403 |
|   2024 |    1289 | -0.1524 |
|   2025 |     239 | -0.1616 |
