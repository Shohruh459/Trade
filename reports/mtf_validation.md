# MTF tadqiqot: validation (2021-01-01 … 2022-12-31), faqat tavsifiy takrorlash

Discovery'da nomzod qoida chiqmadi (reports/mtf_candidates_discovery.json = []), shuning uchun Validation'da qoida sinalmaydi. Faqat tavsifiy topilmalar takrorlanadi (6A). Hodisalar: F1 169, F2 223.


## 6A.1 Bog'liqlik regressiyasi (Validation)

N = 6695

|     |   joint_beta |   joint_t |   uni_beta |   uni_t |
|:----|-------------:|----------:|-----------:|--------:|
| M1  |        0.02  |      0.55 |      0.04  |    0.93 |
| M5  |        0.048 |      0.73 |      0.07  |    1    |
| M15 |        0.037 |      0.43 |      0.055 |    0.68 |
| H1  |       -0.047 |     -0.47 |      0.002 |    0.02 |
| H4  |        0.081 |      0.77 |      0.067 |    0.65 |


## 6A. F1: har bir vaqt oralig'i H1 yo'nalishiga mos kelganda (descriptive)

|     |   share_aligned |   cont_netR_aligned |   cont_netR_not |   TP_first_aligned |   TP_first_not |
|:----|----------------:|--------------------:|----------------:|-------------------:|---------------:|
| M1  |            0.76 |               0.09  |           0.1   |               37.5 |           39   |
| M5  |            0.93 |               0.078 |           0.29  |               37.3 |           45.5 |
| M15 |            0.92 |               0.074 |           0.308 |               37.2 |           46.2 |
| H4  |            0.41 |               0.233 |          -0.008 |               42.9 |           34.3 |


## 6A. F1: trend davomiyligi (H1 barlar) va maksimal harakat (ATR) — belgi=1 va belgi=0

|       |   N1 |   N0 |   med_dur_1 |   med_dur_0 |   p_dur |   med_ext_1 |   med_ext_0 |   p_ext |
|:------|-----:|-----:|------------:|------------:|--------:|------------:|------------:|--------:|
| Lfull |  109 |   60 |        40   |        22.5 |   0.002 |        2.51 |        1.09 |   0.013 |
| H4ok  |   70 |   99 |        33.5 |        37   |   0.795 |        2    |        1.83 |   0.369 |
| T     |   63 |  106 |        43   |        24   |   0     |        2.87 |        1.4  |   0.018 |


## 6A. F1: umumiy

|    |   events |   median_duration_bars |   share_dur_ge_24 |   median_extent_ATR |
|---:|---------:|-----------------------:|------------------:|--------------------:|
|  0 |      169 |                     36 |              0.62 |                1.85 |
