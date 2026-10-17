# Oltin: trend qanday shakllanadi? M1·M5·M15·H1·H4 bog'liqliklari va davom etish/qaytish qoidalari (pre-registered reja)

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Ta'riflar, davrlar, mezonlar test paytida o'zgartirilmaydi. O'zgartirish faqat 10-bo'limdagi jurnalga sababi bilan yoziladi.

## 1. Maqsad
Oltin (XAUUSD) uchun 2018–2025-fevral davrida: (1) turli vaqt oralig'idagi (M1, M5, M15, H1, H4) trend holatlari bir-biri bilan bog'liqmi, trend qaysi
tartibda shakllanadi; (2) qaysi holatlardan keyin H1 trendi **davom etadi**, qaysilardan keyin **tez qaytadi**; (3) shundan xarajatdan keyin foyda beradigan, oddiy (≤3 shart) qoida chiqadimi.
Oldingi darslar (reports/summary_gold_EAs.md, event_study_H1.md, trend_results.md): oddiy indikator qoidalari xarajatdan keyin foyda bermadi; shuning uchun bu safar qat'iy
vaqt bo'yicha bo'lingan tasdiqlash, ko'p test tuzatmasi va mustaqil aktivlarda tekshiruv bor.

## 2. Ma'lumot (muzlatilgan)
- **Asosiy:** XAUUSD M1 BID shamlar, `ZombitX64/xauusd-gold-price-historical-data-2004-2025` (`XAU_1m_data.jsonl`), MT server vaqti (Europe/Athens) → UTC ga o'tkazilgan.
  Davr: 2018-01-02 → **2025-02-28** (undan keyingi oylarda bo'shliq). `parquet` nusxasi: 2 522 902 M1 sham.
- **Boshqa vaqt oralig'lari M1 dan quriladi** (bir xil manba, nomuvofiqlik yo'q): M5, M15, H1, H4 = UTC bo'yicha tekis (H4 = 00,04,08,12,16,20 UTC) resample; O=first, H=max, L=min, C=last.
- **Mustaqil tasdiqlash (Stage X):** EURUSD, GBPUSD, AUDUSD M1 (`qleap/dukascopy-ticks-ohlcv`, 1min), 2020-04 → 2025-12. FX qoidalari oltindan olingan; FX ma'lumoti qoida chiqarishda ishlatilmaydi.
- Spred ma'lumotda yo'q: xarajat 5-bo'limda belgilangan.

## 3. Vaqt bo'yicha bo'lish va qulflash protokoli
- **Discovery:** 2018-01-02 → 2020-12-31. **Validation:** 2021-01-01 → 2022-12-31. **Final:** 2023-01-01 → 2025-02-28. (Birinchi 20 kun indikator isitish uchun, hodisa hisoblanmaydi.)
- Tartib: (1) faqat Discovery tahlil qilinadi; nomzod qoidalar ro'yxati faylga yozilib **commit qilinadi**; (2) shundan keyingina Validation; nomzodlar ro'yxati yana commit;
  (3) shundan keyingina Final (bir marta); (4) shundan keyingina FX tasdiqlash. Har bosqichda oldingi bosqich ro'yxati o'zgartirilmaydi.

## 4. Trend holatlari va xususiyatlar (har vaqt oralig'i X ∈ {M1, M5, M15, H1, H4} uchun)
Har X uchun o'z yopilishlar qatorida:
- **Yo'nalish d_X** = sign(EMA20 − EMA50) (teng bo'lsa oldingi qiymat).
- **Trend kuchi ER_X** (Kaufman samaradorlik nisbati, n=20) = |C_t − C_{t−20}| / Σ_{i=t−19..t} |C_i − C_{i−1}|. "Trendli": ER_X ≥ 0.30.
- **Yoshi age_X** = d_X oxirgi almashganidan beri barlar soni.
- Qaror vaqti t da **faqat to'liq yopilgan** barlar ishlatiladi (ko'rilmagan kelajak yo'q): M1/M5/M15/H1/H4 ning t gacha tugagan oxirgi bari.
- ATR_H1 = oxirgi 14 ta H1 shamning TR o'rtachasi (SMA).

## 5. Hodisalar (faqat 07:00–20:00 UTC, likvid soatlar) va natija
Ikki hodisa oilasi, ikkalasi H1 trend atrofida:
- **F1 "Trend tug'ilishi":** H1 d_H1 almashadi (EMA20/EMA50 kesishuvi). Yo'nalish D = yangi d_H1. Qaror vaqti = shu H1 bar yopilishi.
- **F2 "Pullback hal bo'lishi":** H1 trendi yetilgan (age_H1 ≥ 6) va D = d_H1; M15 d_M15 D ga teskari tomonga o'tgan (pullback), keyin yana D ga qaytgan.
  Qaror vaqti = shu M15 bar yopilishi. Bitta pullback bitta hodisa.
**Natija (triple-barrier, R birligida):** kirish — hodisadan keyingi birinchi M15 bar ochilishi. ATR_H1 hodisa vaqtidagi qiymat. TP = 2.0 × ATR_H1, SL = 1.0 × ATR_H1
(yo'nalishda), vaqt bilan chiqish 24 H1 bar (=96 M15 bar). Yo'l M15 shamlar bo'yicha tekshiriladi; bir shamda ikkalasi bo'lsa — SL birinchi. Vaqt chiqishida R = (C − kirish)·D/ATR_H1.
**Xarajat:** bitim boshiga $0.30 (aylanma), R birligida $0.30/ATR_H1 ayriladi → net R. Stress: $0.50. (FX: ATR 1.0 pip = 0.0001 xarajat, stress 1.5 pip.)
- **Continuation** = D yo'nalishida, **Fade** = teskari yo'nalishda (bir xil to'siqlar). Sezgirlik (faqat ma'lumot uchun): TP 1.0/SL 1.0.

## 6. Tahlillar
**A) Tavsifiy (qoida tanlashga ta'sir qilmaydi, faqat bog'liqliklarni tushunish uchun; Discovery va Validation alohida):**
1. *Bog'liqlik regressiyasi:* barcha 07–20 UTC H1 yopilishlarida y = (C_{t+12} − C_t)/ATR_H1 ni [d_M1, d_M5, d_M15, d_H1, d_H4] ga OLS (HAC 24 lag): qaysi vaqt oralig'i boshqalardan tashqari qo'shimcha ma'lumot beradi.
2. *Trend holatlarining o'zaro bog'liqligi:* d_X lar orasidagi hamjihatlik jadvali; H1 almashuvlaridan oldin M15/M5/M1 almashganmi (oldingi 4 H1 bar ichida) — "pastdan yuqoriga yoyilish" va "yuqoridan pastga" ulushlari.
3. *Trend davomiyligi:* F1 hodisalari uchun keyingi H1 almashuvigacha bo'lgan barlar soni va yo'nalishdagi maksimal harakat (ATR birligida), holatlar bo'yicha (Mann–Whitney).
**B) Asosiy gipoteza testlari (qoida shu yerdan chiqadi):**
Har hodisa uchun uchta ikkilik belgi: **Lfull** (F1: M1,M5,M15 hammasi D ga mos; F2: M1 va M5 ikkalasi D ga mos), **H4ok** (d_H4 = D), **T** (ER_H1 ≥ 0.30).
2³ = 8 "hujayra" × 2 oila (F1, F2) × 2 yo'nalish (continuation, fade) = **32 ta test**. Har hujayra uchun o'rtacha net R > 0 (bir tomonlama, hafta bo'yicha klasterlangan t).
Discovery'da N < 40 bo'lgan hujayra sinalmaydi (hisobotda ko'rsatiladi). Qo'shimcha ikkilik belgilar (yuqori o'zgaruvchanlik, sessiya, yosh) faqat tavsif uchun.

## 7. Nomzod qoida tanlash va o'tish mezonlari (hammasi bajarilishi shart, bosqichma-bosqich)
1. **Discovery:** hujayra net R o'rtachasi > 0, Benjamini–Hochberg FDR q ≤ 0.10 (32 test bo'yicha), N ≥ 40, o'rtacha net R ≥ +0.10.
2. **Validation:** shu hujayra: net R o'rtachasi > 0, bir tomonlama p ≤ 0.10, N ≥ 30.
3. **Final:** shu hujayra: net R o'rtachasi > 0, p ≤ 0.10, stress xarajat ($0.50) bilan ham o'rtacha net R > 0.
4. **FX tasdiqlash:** EURUSD+GBPUSD+AUDUSD hodisalari birlashtirilgan, shu qoida: o'rtacha net R > 0, p ≤ 0.10.
5. **Savdo simulyatsiyasi** (faqat nomzod o'tsa): bir vaqtda bitta pozitsiya, bitimga 0.5% risk, 2018-01 → 2025-02: net R yig'indisi, Sharpe, maksimal drawdown (≤ 25%), timing testi
   (hodisalar vaqtini tasodifiy aylana bo'ylab siljitish, 3000 marta, p ≤ 0.10).
Bir nechta hujayra o'tsa, afzallik: eng oddiy (eng kam shartli), keyin eng yuqori Discovery o'rtacha net R. Hech biri o'tmasa — xulosa: "ishonchli qoida topilmadi".

## 8. Natijaga qarab nima qilamiz
- **Qoida o'tdi:** aniq kirish/chiqish/SL/risk qoidasi yoziladi, MT5 uchun kod, keyin demo (kamida 3 oy).
- **Qoida o'tmadi:** bog'liqliklar bo'yicha topilmalar (6A) hisobotda qoladi (ular ham foydali ma'lumot); qoida chiqmagani aniq aytiladi. Natijaga qarab parametrlar o'zgartirilmaydi.

## 9. Xavflar va cheklovlar
- Hodisalar soni kam bo'lishi mumkin (3 yillik Discovery); shu uchun N chegaralari qo'yilgan va ko'p test tuzatmasi bor.
- Hodisalar bir-biriga yaqin (autokorrelyatsiya): hafta bo'yicha klasterlangan standart xato ishlatiladi.
- Spred doimiy faraz qilinadi (haqiqiy spred vaqt bo'yicha o'zgaradi); BID shamlar; kechikish/sirpanish yo'q (stress qisman qoplaydi).
- Hindsight: oltin 2019–2020 va 2023–2025 da kuchli o'sganini bilamiz; shuning uchun Validation (2021–22 yon/tushish) va FX tasdig'i qo'yilgan.
- Tahlil o'zi "naqsh topish" bo'lgani uchun tasodifiy topilmalar xavfi katta; shuning uchun qulflash protokoli (3-bo'lim).

## 10. O'zgartirishlar jurnali
(hozircha bo'sh)
