# Keyingi bosqich: ko'p aktivli past chastotali portfel (N1) va rejadagi yangiliklarga oltin reaksiyasi (N2): pre-registered reja

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Qoidalar, ta'riflar, davrlar, mezonlar test paytida o'zgartirilmaydi. O'zgartirish faqat 9-bo'limdagi jurnalga sababi bilan yoziladi.

## 1. Kelishuv (foydalanuvchi bilan)
- **Maqsad:** daromad, imkon qadar barqaror oylik natija ("har oy foyda" bo'lsa davomiy bo'ladi). Ochiq gap: har oy foyda kafolatlanmaydi (Sharpe 1 da ~61% oy foydali). Shuning uchun qaror **12 oylik va drawdown** bo'yicha, oylik ko'rsatkichlar (foydali oylar ulushi, eng yomon oy) har doim e'lon qilinadi, lekin pass/fail uchun ishlatilmaydi.
- **Risk chegarasi:** portfel (N1) uchun maksimal drawdown ≤ **20%**; kun ichi/hodisa savdosi (N2) uchun ≤ **30%** (foydalanuvchi roziligi). Katta drawdown ruxsati ustunlik bermaydi: skalping bo'yicha oldingi hamma sinovlar zarar edi.
- **Vaqt:** natija chiqquncha, lekin to'xtatish qoidasi bor (7-bo'lim).

## 2. Umumiy tamoyillar
Xarajat hisobga olingan; vaqt bo'yicha qulflangan bosqichlar; Holm/FDR; 1 oy kechiktirilgan variant (oylik o'rtacha narx artefakti uchun); natijadan qat'i nazar hammasi e'lon qilinadi; parametrlar sozlanmaydi.

---
## 3. N1: ko'p aktivli past chastotali portfel (Faber/GTAA turi)
### 3.1 Ma'lumot (muzlatilgan, oylik)
- Aksiya: S&P 500 to'liq daromadi (`STRATEGY_PORTFOLIO.md` dagi kabi: narx + dividend/12, dividend oxirgi nolmas qiymatdan oldinga to'ldirilgan). Obligatsiya: 10 yillik to'liq daromad approksimatsiyasi (durasiya 7.5). Oltin: `datasets/gold-prices` oylik.
  Neft: WTI oylik (`datasets/oil-prices/wti-monthly.csv`, 1986-01+). Tabiiy gaz: Henry Hub oylik (`datasets/natural-gas/data/monthly.csv`, 1997-01+).
- Aktiv mavjud bo'lgan oydan boshlab portfelga kiradi (N_t = shu oyda mavjud aktivlar soni). Narx indekslari: aksiya/obligatsiya uchun to'liq daromaddan yig'ilgan indeks.
- Davr: 1976-01 → 2026-06 (signal isitishi uchun 1973 dan). Davrlar: E1 = 1976-01…1999-12, E2 = 2000-01…2026-06.
### 3.2 Qoida (muzlatilgan)
- Har aktiv uchun oy oxirida: narx > oxirgi 10 oy o'rtachasi (SMA10) bo'lsa signal = 1, aks holda 0. Pozitsiya keyingi oy uchun.
- Portfel vazni: signal = 1 bo'lgan har aktivga 1/N_t; qolgan qism naqd (daromadi 0). Oyiga qayta balanslanadi.
- **Xarajat:** 10 baza punkti × Σ|vazn o'zgarishi|. **Lag-1 variant:** signal bir oy oldingi (t−1) oy oxiridan, qaror bir oy keyin (asosiy bilan birga hisoblanadi).
- **Benchmarklar:** B1 teng vaznli buy&hold (1/N_t, oylik qayta balanslash, xarajat bilan), B2 60/40 (aksiya/obligatsiya).
### 3.3 O'lchovlar
CAGR, vol, Sharpe (rf=0), maksimal drawdown, eng yomon 12 oy, **foydali oylar ulushi, eng yomon oy, har qanday 3 oylik oyna foydali ulushi** (E1, E2, to'liq). Timing nazorati: signal qatorini tasodifiy aylana bo'ylab siljitish (5000 marta), Sharpe p-qiymati.
### 3.4 O'tish mezonlari (hammasi bajarilishi shart)
- (a) to'liq namunada sof Sharpe ≥ 0.50; (b) maksimal drawdown ≤ 20% (to'liq) va ≤ 25% har davrda;
- (c) har davrda sof CAGR > 0 va Sharpe ≥ 0.30; (d) B1 ga nisbatan: drawdown ≤ 0.6 × B1 drawdowni va Sharpe ≥ B1 Sharpe − 0.05 (xavfni arzon kamaytirish);
- (e) timing p ≤ 0.10; (f) lag-1 variantda sof Sharpe ≥ 0.40 va drawdown ≤ 25%.
- B2 bilan solishtirish faqat tavsifiy.
### 3.5 Natijaga qarab
O'tsa: qoida hujjatlanadi, oylik hisoblagich (`tools/gold_monthly_check.py`) ko'p aktivli holatga kengaytiriladi, forward kuzatuv (qog'oz, ≥ 12 oy). O'tmasa: N1 rad etiladi.

---
## 4. N2: rejadagi AQSh yangiliklari atrofida oltin reaksiyasi (hodisa tadqiqoti)
### 4.1 Ma'lumot (muzlatilgan)
- Kalendar: `Ehsanrs2/Forex_Factory_Calendar` (`forex_factory_cache.csv`; 2007-01 → 2025-04). Vaqt ISO formatida UTC siljishi bilan beriladi; barchasi UTC ga o'tkaziladi.
  **Vaqt tekshiruvi** (sinovdan oldin): "Non-Farm Employment Change" chiqish vaqtlari 12:30 yoki 13:30 UTC atrofida to'planishi kerak; mos kelmasa sabab yoziladi va jurnalga kiritiladi.
- Oltin: XAUUSD M1 BID (ZombitX64), 2018-01-02 → 2025-02-28 (UTC).
### 4.2 Hodisa to'plami (muzlatilgan)
USD, "High Impact Expected", Actual va Forecast sonli bo'lgan hodisalar, 10 oila: Non-Farm Employment Change, Unemployment Rate (ishora teskari), CPI m/m, Core CPI m/m, Retail Sales m/m, Core Retail Sales m/m,
ISM Manufacturing PMI, ISM Services PMI, Average Hourly Earnings m/m, Federal Funds Rate. "Dollar uchun yaxshi" yo'nalishi: Actual > Forecast (Unemployment Rate uchun teskari).
Ajablanish z = (Actual − Forecast) / σ_oila, σ_oila = shu oiladagi oldingi hodisalar uchun kengayuvchi std (≥ 12 oldingi hodisa; kelajaksiz). **Asosiy to'plam:** |z| ≥ 1.0. Bir kunda bir nechta hodisa shu minutda chiqsa, bittasi olinadi (eng katta |z|).
### 4.3 Reaksiya va savdo ta'rifi
- t = chiqish daqiqasi. Boshlang'ich reaksiya = P(t+2 daqiqa yopilishi) − P(t−1 daqiqa yopilishi); yo'nalishi D0 = sign(reaksiya) (teng bo'lsa tashlanadi).
- **Kirish:** t+2 daqiqa yopilishida (ya'ni birinchi 2 daqiqa o'tkazib yuboriladi: kechikish va spred kengayishi uchun). **Continuation** = D0 yo'nalishida, **Fade** = teskari.
- **Chiqish:** vaqt bo'yicha h daqiqadan keyin, h ∈ {5, 15, 30}; himoya stop 1.0 × ATR_H1 (M1 yo'l bo'yicha, stop birinchi). R = sof foyda / ATR_H1.
- **Xarajat:** aylanma $0.80 (yangilik atrofida spred kengayishi), stress $1.50.
- **6 ta hujayra:** {continuation, fade} × {5, 15, 30 daqiqa}.
### 4.4 Davrlar va qulflash
Discovery 2018-01 → 2021-12; Validation 2022-01 → 2023-12; Final 2024-01 → 2025-02. Har bosqichdan keyin nomzodlar ro'yxati commit qilinadi; keyingi bosqich faqat shundan keyin.
### 4.5 Mezonlar (bosqichma-bosqich, hammasi shart)
- Discovery: hujayra o'rtacha sof R > 0 va **Holm** (6 test, 5%) dan o'tgan, N ≥ 60, o'rtacha ≥ +0.05 R.
- Validation: o'rtacha sof R > 0, bir tomonlama p ≤ 0.10 (kunlar bo'yicha klasterlangan), N ≥ 40.
- Final: o'rtacha sof R > 0, p ≤ 0.10, stress xarajatda ham > 0, N ≥ 20; 0.5% risk bilan equity drawdown ≤ 30%.
- Qo'shimcha tavsif (qarorga ta'sir qilmaydi): oila bo'yicha taqsimot, |z| ≥ 0.5 va ≥ 2 sezgirligi, yo'nalish (buy/sell) bo'yicha, oylar bo'yicha foydali ulush.

---
## 5. Foydalanuvchi maqsadiga bog'liq hisobotlar
Ikkala tadqiqot uchun: foydali oylar ulushi, eng yomon oy, eng uzun zararli ketma-ketlik, 12 oylik rolling natija. Bu raqamlar "har oy daromad" maqsadiga qanchalik yaqinligini ochiq ko'rsatadi.

## 6. Natijaga qarab nima qilamiz
Biror tadqiqot o'tsa — shu qoida hujjatlanadi va forward (qog'oz) kuzatuvga qo'yiladi (kamida 12 oy), keyin kichik risk bilan. Ikkalasi ham o'tsa — ikkalasi, lekin alohida.

## 7. To'xtatish qoidasi (oldindan kelishilgan)
N1 va N2 ikkalasi ham mezondan o'tmasa — **yangi qidiruv to'xtatiladi**. Qoladi: oylik oltin hisoblagichi (SMA10, 10% oltin), forward kuzatuv va loyiha hujjatlari. Natijaga qarab parametrlarni "yaxshilash" yoki yangi variantni "yana bir marta" sinash taqiqlanadi; yangi g'oya faqat yangi oldindan yozilgan reja va yangi (ko'rilmagan) ma'lumot bilan.

## 8. Xavflar va cheklovlar
- **N1:** oylik o'rtacha narxlar (drawdown/vol past, Working effect: lag-1 bilan nazorat); neft/gaz spot narxlari (fyuchers roll daromadi yo'q); aktivlar soni kam (4–5), uzun davrda ham bir necha tsikl; hindsight.
- **N2:** kalendar uchinchi tomondan (vaqt/qiymat xatolari mumkin); M1 BID shamlar, real spred yangilik paytida o'zgaruvchan; ijro kechikishi/sirpanish katta; 2 daqiqa kechikish ham ko'pchilik harakatni o'tkazib yuboradi; hodisalar soni cheklangan (Final'da kam).
- Bu moliyaviy maslahat emas; yo'qotishlar mumkin.

## 9. O'zgartirishlar jurnali
- 2026-10-17: N1 ishga tushirildi (backtest/n1.py, reports/n1_results.md). Natija: **PASS** (a–f hammasi bajarildi). Reja va mezonlarga o'zgartirish kiritilmadi. Amalga oshirish tafsiloti: timing nazoratida har aktiv signali mustaqil aylana siljitiladi; xarajat vazn o'zgarishi yig'indisi (driftsiz) bo'yicha hisoblandi. N2 hali ishga tushirilmagan.
- 2026-10-17 (N2 ma'lumot tekshiruvi, gold natijasini ko'rishdan OLDIN): 4.1 dagi vaqt tekshiruvi muvaffaqiyatsiz: kalendar vaqtlari ishonchsiz (NFP uchun 220 dan 161 ta, Unemployment Rate va Retail Sales uchun barchasi 00:00 yarim-tun "placeholder"; qolganlarida Eron/AQSh DST farqidan 1 soatlik siljishlar: ET 07:30/09:00/13:00). Haqiqiy vaqti borlari standart ET jadvaliga 2018+ da 83% mos, qolganlari aynan −1 soat. **Tuzatish:** hodisa SANASI fayldan (DateTime ning birinchi 10 belgisi), VAQTI oila bo'yicha standart ET jadvalidan, AQSh DST bilan UTC ga o'tkaziladi: 08:30 ET (NFP, Unemployment Rate, CPI m/m, Core CPI m/m, Retail Sales, Core Retail Sales, Average Hourly Earnings), 10:00 ET (ISM Manufacturing, ISM Services), 14:00 ET (Federal Funds Rate). Qolgan reja o'zgarmadi.
- 2026-10-17: N2 Discovery (backtest/n2.py, reports/n2_discovery.md): 96 hodisa, 6 hujayraning hammasi o'rtacha net R < 0 (−0.14 … −0.29 R); nomzod yo'q. **N2 rad etildi.** Validation va Final ishlatilmadi (ko'rilmagan qoldi). Reja va mezonlarga o'zgartirish kiritilmadi. Eslatma: ajablanish to'plami (|z|≥1, 96 hodisa) kichik; kuch past, lekin barcha hujayralarda ishora manfiy.
