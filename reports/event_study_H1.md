# H1 hodisa tadqiqoti: 12–16 UTC dagi o'ta katta 1 daqiqalik shamdan keyin oltin (XAUUSD tick, Dukascopy)

Reja: `STRATEGY_GOLD.md` (natijadan oldin commit qilingan). $ / uns hisobida; `gross` = o'rta narxdan o'rta narxga, `net` = real bid/ask bilan, `t_net` = kun bo'yicha klasterlangan t. Cont = hodisa yo'nalishida, fade = teskari.


## Discovery (15 fayl, 106 kun, 144 hodisa)

|              |   N |   gross |    net |   net_stress |   t_net |   win_pct |   spread_in | yrs_pos   |
|:-------------|----:|--------:|-------:|-------------:|--------:|----------:|------------:|:----------|
| ('cont', 3)  | 144 |   0.233 | -0.194 |       -0.294 |   -0.75 |      41   |        0.45 | 3/6       |
| ('cont', 5)  | 144 |   0.506 |  0.067 |       -0.033 |    0.17 |      44.4 |        0.45 | 3/6       |
| ('cont', 10) | 144 |   0.535 |  0.109 |        0.009 |    0.21 |      41.7 |        0.45 | 2/6       |
| ('fade', 3)  | 144 |  -0.233 | -0.659 |       -0.759 |   -2.39 |      35.4 |        0.45 | 1/6       |
| ('fade', 5)  | 144 |  -0.506 | -0.945 |       -1.045 |   -2.32 |      39.6 |        0.45 | 2/6       |
| ('fade', 10) | 144 |  -0.535 | -0.961 |       -1.061 |   -1.74 |      44.4 |        0.45 | 2/6       |


## Confirmation (13 fayl, 110 kun, 159 hodisa)

|              |   N |   gross |    net |   net_stress |   t_net |   win_pct |   spread_in | yrs_pos   |
|:-------------|----:|--------:|-------:|-------------:|--------:|----------:|------------:|:----------|
| ('cont', 3)  | 159 |  -0.119 | -0.501 |       -0.601 |   -2.68 |      36.5 |         0.4 | 1/6       |
| ('cont', 5)  | 159 |  -0.239 | -0.615 |       -0.715 |   -2.81 |      36.5 |         0.4 | 0/6       |
| ('cont', 10) | 159 |  -0.301 | -0.677 |       -0.777 |   -2.47 |      35.2 |         0.4 | 2/6       |
| ('fade', 3)  | 159 |   0.119 | -0.263 |       -0.363 |   -1.43 |      39   |         0.4 | 2/6       |
| ('fade', 5)  | 159 |   0.239 | -0.138 |       -0.238 |   -0.63 |      41.5 |         0.4 | 2/6       |
| ('fade', 10) | 159 |   0.301 | -0.074 |       -0.174 |   -0.27 |      49.1 |         0.4 | 2/6       |


## Oldindan belgilangan mezon bo'yicha qaror

| cell       | disc_ok   | conf_ok   | stress_ok   | years_ok   | PASS   |
|:-----------|:----------|:----------|:------------|:-----------|:-------|
| cont 3min  | False     | False     | False       | False      | False  |
| cont 5min  | False     | False     | False       | False      | False  |
| cont 10min | False     | False     | False       | False      | False  |
| fade 3min  | False     | False     | False       | False      | False  |
| fade 5min  | False     | False     | False       | False      | False  |
| fade 10min | False     | False     | False       | False      | False  |


## Sezgirlik (faqat ma'lumot uchun; discovery+confirmation birga, net $/uns, t)

|                         |   N |   gross |    net |   t_net |
|:------------------------|----:|--------:|-------:|--------:|
| k=3 cont 5min           | 794 |  -0.075 | -0.507 |   -5.1  |
| k=3 fade 5min           | 794 |   0.075 | -0.357 |   -3.68 |
| k=4 cont 5min           | 303 |   0.115 | -0.291 |   -1.35 |
| k=4 fade 5min           | 303 |  -0.115 | -0.521 |   -2.31 |
| k=5 cont 5min           | 151 |   0.267 | -0.132 |   -0.39 |
| k=5 fade 5min           | 151 |  -0.267 | -0.665 |   -1.88 |
| k=6 cont 5min           |  93 |  -0.082 | -0.46  |   -1.14 |
| k=6 fade 5min           |  93 |   0.082 | -0.297 |   -0.72 |
| 07-10 UTC k=4 cont 5min | 174 |  -0.185 | -0.675 |   -4.46 |
| 07-10 UTC k=4 fade 5min | 174 |   0.185 | -0.305 |   -2.34 |


Kontekst: hodisada o'rtacha kirish spredi $0.42 (oddiy paytda ~$0.3–0.5), 5 daqiqada o'rtacha |harakat| $2.12, hodisa shamining o'rtacha diapazoni $4.49.


## Natijaning ma'nosi (hisobotga keyin qo'shildi)

- **Pre-registered mezon bo'yicha H1 o'tmadi.** Qo'shimcha: discovery'da hodisalar soni 144 (< 300), ya'ni mezonning N talabi ham bajarilmadi (namuna kichik).
- **Gross effekt bir namunadan boshqasiga ishorasini o'zgartirdi:** discovery'da continuation +$0.23…+0.53, confirmation'da −$0.12…−0.30. Bu barqaror ustunlik emas.
- **Xarajat:** hodisa paytida o'rtacha spred ~$0.40–0.45, ya'ni bitim boshiga ~$0.43 yo'qotish.
- **Kuch tahlili (pooled N≈303, k=4, 5 daqiqa):** continuation gross o'rtachasining 95% ishonch oralig'i quyida jadvalda. Xarajatdan keyin foyda uchun gross ≥ ~$0.43 kerak; undan kichik ustunlik amalda ahamiyatsiz.
- **Sezgirlik:** k=3 (N=794) da net aniq manfiy (t=−5.1). 07–10 UTC da gross ≈ ±$0.19 (kichik, fade tomonga), net manfiy.

Xulosa: bu hodisa turida (o'ta katta 1 daqiqalik portlashdan keyingi 3–10 daqiqa) sinalgan namunada tradable edge yo'q.
Pooled (discovery+confirmation), k=4, 12-16 UTC. Gross $/oz = move in the event direction (cont); fade = -cont.
|   h_min |   N |   days |   gross_cont |   ci95_lo |   ci95_hi |   avg_round_trip_cost |   needed_gross_for_net_0 |   excluded_if_ci_hi_below |
|--------:|----:|-------:|-------------:|----------:|----------:|----------------------:|-------------------------:|--------------------------:|
|       3 | 303 |    216 |        0.048 |     -0.26 |      0.36 |                  0.4  |                     0.4  |                      0.4  |
|       5 | 303 |    216 |        0.115 |     -0.31 |      0.55 |                  0.41 |                     0.41 |                      0.41 |
|      10 | 303 |    216 |        0.096 |     -0.48 |      0.67 |                  0.4  |                     0.4  |                      0.4  |

std of 5-min gross move per event ($/oz): 3.86
