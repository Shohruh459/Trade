# Yig'ma hisobot: EUR/USD va XAU/USD (oldindan belgilangan protokol)

Protokol: 8 strategiya × 5 chiqish = 40 variant, parametrlar sozlanmagan. Tanlov faqat in-sample bo'yicha (PF>1.1, ≥200 bitim, DD<15%, to'xtamagan). Tanlanganlar out-of-sample'da **bir marta** sinaldi. O'tish mezoni (OOS): PF>1.3, DD<15%, ≥200 bitim, xarajatdan keyin foyda, OOS PF ≥ 0.8×IS PF. Har bir davr $10 000 dan, risk 1%.


## EURUSD

Ma'lumot: data/EURUSD_H1_202004_202604.csv. In-sample 2020-04-01 → 2024-01-01, out-of-sample 2024-01-01 → 2026-04-07. Xarajat: spred 0.8 pip, slippage 0.2 pip, komissiya $7.0/lot.

40 variantdan in-sample mezonidan o'tgani: **0**. Mezondan o'tmaganlar OOS'da ko'rib chiqilmaydi (to'liq jadval: `reports/protocol_EURUSD_all40.csv`, shaffoflik uchun).

_In-sample'da tanlov mezonidan o'tgan variant yo'q._


## XAUUSD

Ma'lumot: data/XAUUSD_H1_2018_2025.csv. In-sample 2018-01-01 → 2023-01-01, out-of-sample 2023-01-01 → 2025-03-31. Xarajat: spred 25 pip, slippage 5 pip, komissiya $7.0/lot.

40 variantdan in-sample mezonidan o'tgani: **0**. Mezondan o'tmaganlar OOS'da ko'rib chiqilmaydi (to'liq jadval: `reports/protocol_XAUUSD_all40.csv`, shaffoflik uchun).

_In-sample'da tanlov mezonidan o'tgan variant yo'q._


## Xulosa

| Instrument | IS'dan o'tgan | OOS mezonidan o'tgan |
|---|---|---|
| EURUSD | 0 | 0 |
| XAUUSD | 0 | 0 |
## Qo'shimcha (post-hoc) tekshiruv: drawdown stop o'chirilgan

Bu tanlov uchun ishlatilmaydi. Maqsad: 15% to'xtash qoidasi namunani qisqartirib, foydali strategiyani yashirib qo'ymaganini tekshirish.


### EURUSD

- IS PF>1.1 va ≥200 bitim: **0** variant; IS PF>1.0: 1 / 40; OOS PF>1.0: 4 / 40; OOS PF>1.3: 0 / 40.

Eng yaxshi 5 ta (IS PF bo'yicha):

| variant   |   IS_tr |   IS_PF |   IS_net% |   IS_DD% |   OOS_tr |   OOS_PF |   OOS_net% |   OOS_DD% |
|:----------|--------:|--------:|----------:|---------:|---------:|---------:|-----------:|----------:|
| A fix 1:2 |     100 |    1.02 |       1   |     17   |       56 |     0.71 |      -12.1 |      18.4 |
| A fix 1:1 |     114 |    1    |       0.1 |     12.4 |       60 |     0.77 |       -7.5 |      10.5 |
| E fix 1:2 |     720 |    0.95 |     -20.2 |     39   |      387 |     0.85 |      -37.9 |      43.7 |
| H fix 1:2 |     679 |    0.93 |     -27.8 |     47.2 |      360 |     0.84 |      -39.4 |      46.6 |
| G fix 1:2 |     198 |    0.9  |     -12.9 |     20.4 |      106 |     0.76 |      -17.4 |      22.8 |


### XAUUSD

- IS PF>1.1 va ≥200 bitim: **0** variant; IS PF>1.0: 4 / 40; OOS PF>1.0: 14 / 40; OOS PF>1.3: 4 / 40.

Eng yaxshi 5 ta (IS PF bo'yicha):

| variant    |   IS_tr |   IS_PF |   IS_net% |   IS_DD% |   OOS_tr |   OOS_PF |   OOS_net% |   OOS_DD% |
|:-----------|--------:|--------:|----------:|---------:|---------:|---------:|-----------:|----------:|
| A fix 1:2  |     126 |    1.08 |       6.2 |     21.4 |       55 |     0.72 |      -10.2 |      14.5 |
| A trail    |     132 |    1.08 |       5.2 |     17.7 |       56 |     0.61 |      -11.7 |      14.7 |
| A BE+trail |     126 |    1.05 |       3.2 |     20.5 |       55 |     0.91 |       -2.8 |      15.1 |
| J fix 1:2  |     727 |    1.02 |       9.1 |     38.3 |      348 |     0.97 |       -5.4 |      28.5 |
| A BE+1:2   |     129 |    1    |       0.1 |     20.4 |       57 |     0.69 |       -9.3 |      14.5 |


### Eslatma (oltin, post-hoc)
Oltinda OOS davrida (2023 → 2025-mart) 4 ta variant PF>1.3 ko'rsatdi, lekin ularning in-sample natijasi ijobiy emas edi va tanlovdan o'tmagan. Oltin shu davrda kuchli o'sdi ($1800 → $3000+), shuning uchun bu strategiya emas, bozor trendi samarasi bo'lishi mumkin. 40 variantdan 4 tasi tasodifan yaxshi chiqishi kutiladigan hol. Bu natija ishonchli deb hisoblanmaydi.
