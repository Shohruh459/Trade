# MTF2 natijalari (reja: STRATEGY_MTF2.md, commit 1bce2b0)

Qoida bitta, parametrlar rejadagidek, sozlanmagan. Final va FX bu qoida bilan birinchi marta sinaldi.


## Asosiy qoida: natijalar

| set                                   |   N |   win_pct |   mean_netR |     t |   p_one_sided |   PF |   maxDD_pct |   net_pct_at_0p5_risk |   median_hold_h |
|:--------------------------------------|----:|----------:|------------:|------:|--------------:|-----:|------------:|----------------------:|----------------:|
| Final oltin 2023-01…2025-02 (QAROR)   |  42 |      38.1 |       0.032 |  0.18 |        0.43   | 1.08 |         2.8 |                   0.6 |             7.4 |
| Final, stress ($0.50, 5%)             |  42 |      38.1 |       0.003 |  0.02 |        0.4931 | 1.01 |         3.1 |                   0   |             7.4 |
| FX 3 juft birlashgan (QAROR)          | 437 |      36.2 |      -0.019 | -0.41 |        0.6586 | 0.95 |         8.2 |                  -4.5 |             9.8 |
| FX, stress (1.5 pip)                  | 437 |      35.5 |      -0.036 | -0.79 |        0.7838 | 0.9  |        10.2 |                  -8.1 |             9.8 |
| Dev oltin 2018-01…2022-12 (izchillik) | 116 |      37.1 |      -0     | -0    |        0.5009 | 1    |         4.3 |                  -0.2 |             5.5 |


FX juftlar bo'yicha:

|         |   N |   win_pct |   mean_netR |     t |   p_one_sided |   PF |   maxDD_pct |   net_pct_at_0p5_risk |   median_hold_h |
|:--------|----:|----------:|------------:|------:|--------------:|-----:|------------:|----------------------:|----------------:|
| eur_usd | 146 |      31.5 |      -0.101 | -1.35 |        0.912  | 0.75 |         8   |                  -7.3 |             7.4 |
| gbp_usd | 157 |      41.4 |       0.044 |  0.56 |        0.2886 | 1.13 |         5   |                   3.3 |             9.8 |
| aud_usd | 134 |      35.1 |      -0.002 | -0.03 |        0.511  | 0.99 |         5.2 |                  -0.3 |            10.6 |


Tasodifiy kirish nazorati (Final, shu chiqish qoidasi, 2000 marta): nazorat o'rtacha net R = -0.052; p (nazorat ≥ haqiqiy) = 0.2414


## Oldindan belgilangan mezonlar

|                                                  |   bajarildi |
|:-------------------------------------------------|------------:|
| C1 Final: o'rtacha net R>0, p<=0.10, N>=25       |           0 |
| C2 Final stress: o'rtacha net R>0                |           1 |
| C3 FX: o'rtacha net R>0, p<=0.10, N>=60          |           0 |
| C4 Dev: ishonchli manfiy emas                    |           1 |
| C5 Final: o'rtacha net R>=0.10, PF>=1.2, DD<=15% |           0 |
| C6 Final: tasodifiy kirish nazoratida p<=0.10    |           0 |


**Qaror: FAIL**


## Sezgirlik (faqat ma'lumot uchun, qarorga ta'sir qilmaydi)

| variant                       |   N |   win_pct |   mean_netR |     t |   p_one_sided |   PF |   maxDD_pct |   net_pct_at_0p5_risk |   median_hold_h |
|:------------------------------|----:|----------:|------------:|------:|--------------:|-----:|------------:|----------------------:|----------------:|
| Final: filtrsiz F1            | 157 |      38.9 |       0.052 |  0.59 |        0.2764 | 1.13 |         7.1 |                   3.9 |             5.8 |
| Final: faqat Lfull            | 104 |      40.4 |       0.07  |  0.62 |        0.2674 | 1.18 |         5.7 |                   3.5 |             6.9 |
| Final: faqat T                |  59 |      35.6 |      -0.064 | -0.48 |        0.6851 | 0.85 |         4.5 |                  -1.9 |            12   |
| Final: Lfull+T+H4ok           |  13 |      46.2 |       0.256 |  0.72 |        0.2346 | 1.77 |         1.2 |                   1.7 |            13.5 |
| Final: asosiy, trailing 3 ATR |  42 |      33.3 |      -0.208 | -1.13 |        0.8703 | 0.64 |         6.3 |                  -4.4 |            19.4 |
| Final: asosiy, long           |  21 |      57.1 |       0.348 |  1.24 |        0.1082 | 2.1  |         1.5 |                   3.7 |             8   |
| Final: asosiy, short          |  21 |      19   |      -0.284 | -1.52 |        0.9361 | 0.4  |         4.5 |                  -3   |             6.8 |


Final: yillar bo'yicha (bitimlar soni, o'rtacha net R):

|    t |   count |   mean |
|-----:|--------:|-------:|
| 2023 |      17 | -0.046 |
| 2024 |      22 |  0.163 |
| 2025 |       3 | -0.496 |


Chiqish turlari (Final): {'stop': 39, 'stop_gap': 2, 'flip': 1}; o'rtacha ushlab turish 19 soat.
