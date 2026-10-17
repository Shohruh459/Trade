# N3: oltin, M1 swing-trend, ATR filtri va kunlik ±10% chegara: pre-registered reja

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Qoida bitta, parametrlar muzlatilgan, sozlanmaydi. O'zgartirish faqat 8-bo'limdagi jurnalga sababi bilan yoziladi.

## 1. G'oya va halol kutish
Foydalanuvchi g'oyasi: M1 da swing max/min yordamida trendni aniqlab kirish; kun boshidagi kapitalning +10% foydasiga yoki −10% zarariga yetguncha qisqa savdolar ochish; ATR kichik kunlarda savdo qilmaslik; faqat oltin.
Kunlik chegara o'zi ustunlik yaratmaydi (u riskni taqsimlaydi); foyda faqat kirish/chiqish qoidasida haqiqiy ustunlik bo'lsa chiqadi. Shuning uchun sinov tasodifiy kirish nazoratini o'z ichiga oladi. Oldingi M1/M5/M15 sinovlari (MTF, MTF2, skalper EA lar) xarajatdan keyin foyda bermagan; bu g'oya shundan farq qiladi: tuzilma (swing) bo'yicha kirish, kunlik chegara va ATR filtri.

## 2. Ma'lumot
XAUUSD M1 BID (ZombitX64, UTC), 2018-01-02 → 2025-02-28; M15/H1 M1 dan quriladi (`backtest/mtf.py` dagidek). Spred ma'lumotda yo'q: xarajat 5-bo'limda.
**Ochiq cheklov:** bu davr oldingi tadqiqotlarda (boshqa qoidalar bilan) ko'rilgan; bu aniq qoida hech qachon sinalmagan, lekin davr mustaqil "ko'rilmagan" emas. Natija, hatto o'tsa ham, **dastlabki** hisoblanadi va forward (qog'oz) kuzatuv talab qilinadi.
Davrlar (qoida sozlanmagani uchun hammasi hisobot qilinadi): Dev 2018-01 → 2021-12; Val 2022-01 → 2023-12; Final 2024-01 → 2025-02. Qaror davri: **2022-01 → 2025-02**.

## 3. Qoida (hammasi muzlatilgan)
**Sessiya:** 07:00 ≤ t < 20:00 UTC, dushanba–juma. Pozitsiya 20:00 da yopiladi.
**ATR filtri (kunlik):** kun boshida (07:00 UTC gacha oxirgi to'liq H1) A = ATR_H1(14) (TR ning SMA si). Agar A < oxirgi 60 ish kunining 07:00 dagi ATR_H1 medianasi (bugunsiz) bo'lsa — **shu kun savdo yo'q**. (Dastlabki 60 kun isitish.)
**Swing (M1, fractal k = 5):** M1 bar swing-high, agar high i dan oldingi 5 va keyingi 5 barning high laridan qat'iy yuqori bo'lsa; swing-low nosimmetrik. Swing faqat 5 bar o'tgandan keyin (tasdiqlanganda) ma'lum bo'ladi (kelajaksiz).
**Trend:** oxirgi ikki tasdiqlangan swing-high **va** oxirgi ikki swing-low o'sayotgan (HH+HL) → **up**; ikkalasi tushayotgan (LH+LL) → **down**; aks holda trend yo'q.
**Kirish (M1 bar yopilishi, keyingi bar ochilishida bajariladi):** up trendda M1 yopilishi oxirgi swing-high dan yuqori → long; down trendda yopilishi oxirgi swing-low dan past → short.
**Stop:** long uchun oxirgi swing-low (short uchun oxirgi swing-high). Stop masofasi s. Agar s < 0.15 × A yoki s > 1.0 × A bo'lsa, signal o'tkazib yuboriladi (ichi-ichidan juda tor yoki juda keng).
**Take-profit:** 1.5 × s. **Vaqt chiqishi:** 60 M1 bar. Bir shamda stop va TP ikkalasi tegsa — stop birinchi. Bir vaqtda faqat bitta pozitsiya; chiqishdan keyin shu bar yopilishidan boshlab yangi signal mumkin.
**Risk:** har savdoda kun boshidagi kapitalning **1%**. Lot: risk$ / s. Kun uchun maksimal 20 ta savdo.
**Kunlik chegara:** kun boshidagi kapitalga nisbatan realizatsiya + ochiq PnL **≥ +10%** yoki **≤ −10%** bo'lsa, ochiq pozitsiya yopiladi va shu kunga savdo tugaydi. (Amalda 1% risk va 20 savdo bilan chegara kamdan-kam ishlaydi: u hisobotda ko'rsatiladi.)
**Xarajat:** spred $0.30 aylanma (stress $0.50), moliyalashtirish yo'q (kun ichi). R = sof foyda / (s·lot) ... ya'ni net R = (foyda − xarajat) / s.

## 4. O'lchovlar
Savdo darajasida: N, yutuq ulushi, o'rtacha net R, profit factor, ushlab turish mediana. Kun darajasida: savdoli kunlar ulushi, ATR filtri bilan o'tkazib yuborilgan kunlar ulushi, +10% / −10% ga yetgan kunlar soni, kunlik PnL taqsimoti. Oy darajasida: foydali oylar ulushi, eng yomon oy, eng uzun zararli ketma-ketlik. Equity: 1% risk bilan kompaundlangan, maksimal drawdown, maksimal leverage (notional/equity).
Statistika: o'rtacha net R > 0 uchun **kun bo'yicha klasterlangan** t-test (bir tomonlama).
**Tasodifiy kirish nazorati:** shu sessiya, shu ATR filtri va kunlar, shu stop/TP/vaqt chiqishi, lekin kirish vaqti tasodifiy (har kun real savdolar soni teng, yo'nalish tasodifiy, s ni real savdolar taqsimotidan olinadi); 1000 marta; p = tasodifiy o'rtacha net R ≥ real o'rtacha bo'lgan ulush.

## 5. Qaror mezonlari (hammasi bajarilishi shart, qaror davri 2022-01 → 2025-02)
- **C1:** o'rtacha net R > 0, bir tomonlama klasterlangan p ≤ 0.10, N ≥ 200.
- **C2:** stress xarajat ($0.50) bilan ham o'rtacha net R > 0.
- **C3:** 2022–2023 va 2024-01–2025-02 alohida-alohida o'rtacha net R > 0.
- **C4:** Dev (2018–2021) da o'rtacha net R ishonchli manfiy emas (agar < 0 va p(manfiy) ≤ 0.10 bo'lsa o'tmagan).
- **C5:** tasodifiy kirish nazoratida p ≤ 0.10.
- **C6:** equity maksimal drawdown ≤ 30% (qaror davri, 1% risk).
- **C7:** foydali oylar ulushi hisobotda e'lon qilinadi (qarorga ta'sir qilmaydi).
Hammasi bajarilsa — **PASS (dastlabki)**.

## 6. Sezgirlik (faqat ma'lumot uchun, qarorga ta'sir qilmaydi)
ATR filtrisiz; risk 0.5% va 2%; TP 1.0R va 2.0R; fractal k = 3 va 8; long/short alohida; yillar bo'yicha.
Kunlik chegara g'oyasining o'zi uchun: chegarasiz (cheksiz savdo) bilan solishtirish.

## 7. Natijaga qarab nima qilamiz
- **PASS:** dastlabki deb belgilanadi; MT5 uchun kod yoziladi, demo/forward kamida 3 oy (kompyuter bo'lganda), haqiqiy pul faqat kichik risk bilan.
- **FAIL:** qoida rad etiladi; parametrlarni "yaxshilash" taqiqlanadi. Hisobot to'liq e'lon qilinadi, shuningdek tasodifiy nazorat natijasi ("kirish signali ustunlik beryaptimi?") ochiq aytiladi.

## 8. O'zgartirishlar jurnali
- 2026-10-17: sinov ishga tushirildi (backtest/n3.py, reports/n3_results.md). Natija: **FAIL** (C1–C6 hammasi bajarilmadi). Qoida, parametrlar va mezonlarga o'zgartirish kiritilmadi. Amalga oshirish tafsiloti: ±10% chegara pozitsiya ichida ham stop/TP darajasini qisqartirish orqali qo'llandi; tasodifiy nazoratda savdolar bir-biri bilan ustma-ust tushishi mumkin va kunlik chegara qo'llanmagan.
