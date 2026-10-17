# Oltin: portfeldagi roli, trend filtri bilan xavfni kamaytirish va fundamental omillar (pre-registered reja)

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Ta'riflar, davrlar, mezonlar test paytida o'zgartirilmaydi. O'zgartirish faqat 9-bo'limdagi jurnalga sababi bilan yoziladi.

## 1. Nega bu yo'nalish
Savdo signallari (skalping, kunlik/ko'p-TF trend) xarajatdan keyin foyda bermadi (README.md). Bu reja boshqa savol beradi: signal topish o'rniga, **oltinni qanday ushlash kerak?**
(A) oltin portfelga qo'shilsa risk-moslashtirilgan natija yaxshilanadimi; (B) oltin uchun oddiy trend filtri/o'zgaruvchanlik nazorati drawdownni kamaytiradimi, o'ta qimmat narxsiz;
(C) fundamental omillar (real foiz, dollar, inflyatsiya, qiymat, mavsumiylik) oltinning o'rta muddatli daromadini bashorat qiladimi. Oylik uzoq tarix (50 yil) statistik kuch beradi,
xarajat esa ahamiyatsiz. Bu **investitsiya/risk** savollari, kun ichi savdo emas.

## 2. Ma'lumot (muzlatilgan, oylik)
- Oltin: `datasets/gold-prices/data/monthly.csv` (oylik narx, USD/uns; manbaga ko'ra oylik o'rtacha bo'lishi mumkin). Aksiya: `datasets/s-and-p-500/data/data.csv` (S&P 500 narx, dividend; Shiller, oylik o'rtacha).
  Obligatsiya: `datasets/bond-yields-us-10y/data/monthly.csv` (10 yillik foiz, %). Inflyatsiya: `datasets/cpi-us/data/cpiai.csv` (CPI indeksi). Dollar: `datasets/exchange-rates/data/daily.csv` (Fed H.10, oy oxirgi kuni).
- **Davr:** 1976-01 → **2026-06** (indikator isitishi uchun 1973-01 dan boshlab hisoblanadi). Oxirgi oylar to'liq emas bo'lishi mumkin, shuning uchun 2026-06 da kesiladi.
- **Davrlar:** E1 = 1976-01 … 1999-12 (288 oy), E2 = 2000-01 … 2026-06 (318 oy).
- **Hosila qatorlar (approksimatsiya, rejada belgilangan):**
  - oltin oylik daromadi r_g = P_t/P_{t−1} − 1.
  - aksiya to'liq daromadi r_e = S_t/S_{t−1} − 1 + dy_t/12, dy_t = Dividend_t/S_t (Dividend 2023-06 dan keyin nolga teng ma'lumotda: oxirgi nolmas qiymat oldinga to'ldiriladi).
  - obligatsiya daromadi r_b = y_{t−1}/1200 − 7.5 × (y_t − y_{t−1})/100 (modifikatsiyalangan durasiya 7.5 faraz).
  - CPI ma'lumoti 1 oy kechikish bilan ishlatiladi (e'lon qilinishi).
  - Naqd pul/nol foiz: Sharpe uchun risksiz stavka = 0 (hamma qatorlar uchun bir xil).
- **Cheklov:** oylik o'rtacha narxlar volatillik va drawdownni kamaytirib ko'rsatadi (silliqlash); mutlaq raqamlar emas, **solishtirish** muhim.

## 3. Tadqiqot A: oltinning portfeldagi roli
Oylik qayta balanslangan portfellar (xarajat: aylanmaning 5 baza punkti):
- P0: 60% aksiya / 40% obligatsiya. P1: 54/36/10 (10% oltin). P2: 48/32/20 (20% oltin). P3: teskari-vol (risk parity) 3 aktiv, 36 oylik trailing vol. P4: faqat oltin (ma'lumot uchun).
- O'lchovlar (E1, E2, to'liq): yillik daromad, vol, Sharpe, maksimal drawdown, eng yomon 12 oy, Kalmar.
- Sharpe farqi (P1−P0, P2−P0) uchun **harakatlanuvchi blok bootstrap** (blok 12 oy, 5000 marta, oylar birgalikda tanlanadi): 90% ishonch oralig'i va bir tomonlama p (ΔSharpe ≤ 0).
- **Mezon:** oltin vazni w ∈ {10%, 20%} **foydali** deb hisoblanadi, agar (i) ΔSharpe > 0 va (ii) maksimal drawdown P0 dan yomon emas, ikkala davrda (E1 va E2); va (iii) to'liq namunada bootstrap p ≤ 0.10. Aks holda: "ishonchli dalil yo'q".
- Tavsif: oltin korrelyatsiyasi aksiya/obligatsiya bilan (davrlar bo'yicha); aksiya −5% dan ko'p tushgan oylarda oltinning o'rtacha daromadi.

## 4. Tadqiqot B: oltinga trend filtri va vol nazorati (xavfni kamaytirish)
Faqat oltin, oylik signal t oy oxirida, ushlash t+1 oyi uchun (cheksiz kelajak yo'q):
- **O1 (SMA10, Faber):** pozitsiya 1 (long), agar P_t > o'rtacha(P_{t−9..t}); aks holda naqd (0). O'tish xarajati 10 baza punkti.
- **O2 (vol-maqsad):** leverage = min(1.5, 0.10/σ̂), σ̂ = oxirgi 12 oylik daromadlar std × √12. Xarajat 5 b.p. aylanmaga.
- Benchmark: oltin buy&hold. O'lchovlar: Sharpe, maksimal drawdown, eng yomon 12 oy, yillik daromad, almashtirishlar soni (E1, E2, to'liq).
- **Mezon:** overlay **qimmatli**, agar ikkala davrda: (i) maksimal drawdown buy&hold ga nisbatan kamida 20% nisbiy kamaygan va (ii) Sharpe buy&hold Sharpe dan 0.05 dan ko'p past emas.
  (Maqsad: foyda ko'paytirish emas, xavfni arzon kamaytirish.)

## 5. Tadqiqot C: fundamental omillar (o'rta muddatli bashorat)
Oltinning h ∈ {3, 12} oylik keyingi logaritmik daromadi y = ln(P_{t+h}/P_t). Predikatorlar t oy oxirida ma'lum ma'lumotdan (kelajaksiz):
- **x1 real foiz o'zgarishi:** real10y_t = y10_t − infl12_t, infl12_t = 100 × (CPI_{t−1}/CPI_{t−13} − 1); x1 = real10y_t − real10y_{t−12} (kutilgan ishora: manfiy).
- **x2 dollar:** 9 valyuta (UK, Japan, Switzerland, Canada, Australia, New Zealand, Sweden, Norway, Denmark; qiymatlar "valyuta/USD") 12 oylik logaritmik o'zgarishi o'rtachasi (teng vazn; ortishi = dollar kuchayishi).
- **x3 oltin momentumi:** ln(P_t/P_{t−12}). **x4 qiymat:** ln(P_t/CPI_{t−1}) − oldingi 120 oy o'rtachasi (faqat o'tmish). **x5 inflyatsiya:** infl12_t.
- **Mavsumiylik (x6):** gipoteza H_S: sentyabr–fevral oylari o'rtacha oylik daromadi qolgan oylardan yuqori (bir tomonlama HAC t-test; ikkala davrda ham ishora musbat bo'lishi shart).
- **Usul:** har bir predikator uchun bir o'zgaruvchili OLS, **kengayuvchi oyna**, birinchi baholash oynasi tugashi 1989-12 (x4 uchun mavjud bo'lgan boshlanishdan), OOS bashorat 1990-01 → 2026-06−h. Benchmark: kengayuvchi tarixiy o'rtacha.
  O'lchov: OOS R² (Campbell–Thompson) va **Clark–West** bir tomonlama p (Newey–West, lag h−1).
- **Ko'p test:** 5 predikator × 2 ufq + mavsumiylik = 11 test, **Holm** tuzatmasi (oila bo'yicha 5%).
- **Iqtisodiy sinov** (faqat Holm dan o'tgan predikator uchun): oylik qoida: long, agar bashorat > 0, aks holda naqd; OOS davrda Sharpe va drawdown buy&hold bilan, ikki yarim bo'yicha (1990–2007, 2008–2026).
- **Mezon:** predikator **qabul qilinadi**, agar: OOS R² > 0 va Holm-p ≤ 0.05; ikki OOS yarmida ham R² > 0; iqtisodiy qoida ikkala yarmida Sharpe ≥ buy&hold − 0.05 va maksimal drawdown kamida 20% nisbiy kam.

## 6. Natijaga qarab nima qilamiz
- A: foydali vazn topilsa, "oltin ulushi" bo'yicha aniq tavsiya (vazn, qayta balanslash); topilmasa, "ishonchli dalil yo'q" deyiladi.
- B: qimmatli overlay topilsa, oltin ushlovchi uchun oddiy qoida (oy oxirida tekshiruv) hujjatlanadi; aks holda "buy&hold ni overlay yaxshilamadi".
- C: qabul qilingan predikator topilsa, faqat risk nazorati/o'rta muddatli vazn sifatida, kichik ta'sir bilan; aks holda "ishonchli fundamental bashorat topilmadi".
- Hech qaysi holda parametrlar natijaga qarab "yaxshilanmaydi".

## 7. Xavflar va cheklovlar
- **Hindsight:** oltin tarixini bilamiz (1980 cho'qqi, 2001–2012 o'sish, 2013–2018 tushish); eralarga bo'lish va bootstrap shu uchun.
- **Kam mustaqil davrlar:** 50 yilda ~4–5 katta oltin tsikli; ishonch oralig'lari keng bo'ladi.
- **Oylik o'rtacha narxlar** silliqlash va soxta avtokorrelyatsiya keltiradi (ayniqsa signal sinovlarida); natijalarni ehtiyotkorlik bilan o'qish kerak.
- **Bond va aksiya daromadlari approksimatsiya** (durasiya, dividend qo'shish); mutlaq daromadlar aniq emas, nisbiy solishtirish muhim.
- **Bo'sh natija ehtimoli:** hech bir qoida ishlamasligi ham mumkin; bu ham foydali natija.

## 8. Chiqish
`reports/portfolio_results.md` (A, B, C bo'limlari, jadvallar, qaror), kod `backtest/portfolio.py`, birlik testlari (daromad formulalari, blok bootstrap, Clark–West).

## 9. O'zgartirishlar jurnali
- 2026-10-17 (kod yozilgandan keyin, natijani ko'rishdan OLDIN): **oylik o'rtacha narxlar vaqt xatosi (Working effect)** haqida qo'shimcha. Oy oxirida qaror va keyingi oy (o'rtacha-dan-o'rtachaga) daromadi
  bir-biriga to'liq mos emas: daromadning bir qismi qaror vaqtida allaqachon realizatsiya bo'lgan va trend/momentum signallari bilan bog'liq, bu B va C ni sun'iy yaxshilashi mumkin.
  Shuning uchun B va C ga **1 oy kechiktirilgan variant** (signal t−1 oy oxirigacha, qaror/bashorat bir oy keyin) qo'shiladi. Mezonlar o'zgarmaydi. Asosiy variant mezondan o'tsa-yu kechiktirilgan o'tmasa,
  natija "vaqt artefakti ehtimoli" deb belgilanadi va qabul qilinmaydi.
