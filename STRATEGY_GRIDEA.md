# GitHub `shahmeetk/grid-scalper-ea` (oltin, MT5) ni Python'da qayta tiklab sinash: pre-registered reja

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** EA ning o'zi (`grid-scalper.mql5`) va `Gold_Optimized.set` sozlamalari o'qildi; mantiq Python'ga ko'chiriladi. Parametrlar sozlanmaydi. O'zgartirish faqat 9-bo'limdagi jurnalga.

## 1. EA nima qiladi (kod bo'yicha)
Grid/averaging-down: pozitsiya ochadi; narx qarshi ketsa `GridDistance` (+ `AddToDistance` 3-pozitsiyadan keyin) masofada yangi pozitsiya, lot ketma-ketlik bo'yicha; `TP_Type=Average` bo'lsa butun savat o'rtacha kirish narxidan `TakeProfit` masofada yopiladi. Stop-loss yo'q (`UseStopLoss=false`); himoya: floating zarar (balans − equity) > `MaxDDToHedge` bo'lsa `CloseOnMaxDD=true` hammasini yopadi. Savat foydasi ≥ `ProfitToStartTrail` bo'lganda oxirgi pozitsiyaga trailing-stop.

## 2. Sozlamalar (`Gold_Optimized.set`, o'zgarishsiz)
`Trade_Direction=2` (= **faqat Sell**, enum: BOTH=0, BUY=1, SELL=2), `StartMode=1` (= **Immediate**, enum: SIGNAL=0, IMMEDIATE=1), `LotSequence=0.01,0.01,0.01,0.02,0.02,0.03,0.04,0.06,0.10` (oxirgisi takrorlanadi), `MaxOrders=12`, `GridDistance=400` pt, `AddToDistance=200`, `IncreaseDistAfter=3`, `TP_Type=0` (Average), `TakeProfit=1000` pt, trailing: `ProfitToStartTrail=30$`, `TrailStart=500` pt, `TrailStep=100` pt, `TrailOnlyLast=true`, `CooldownSeconds=300`, `MaxDDToHedge=2000$`, `CloseOnMaxDD=true`. Oltinda 1 pt = $0.01; 1 lot = 100 oz.
(Eslatma: .set faylidagi raqamli enumlar haqida README "Both" yozadi, lekin kod bo'yicha 2 = Sell. Asosiy variant .set kodlangani bo'yicha — **faqat Sell**. EA default holati (Both) alohida sezgirlik sifatida sinaladi.)

## 3. Ma'lumot va simulyatsiya (muzlatilgan)
XAUUSD M1 BID (ZombitX64, UTC), 2018-01-02 → 2025-02-28. Boshlang'ich balans **$5,000** (README minimal $3,000–5,000), sezgirlik $3,000. Bid sham; Sell: kirish Bid da, yopish Ask = Bid + spred; Buy: kirish Ask da. Spred **$0.30** (stress $0.50); moliyalashtirish (swap) yiliga 3% × pozitsiya qiymati, har bar balansdan yechiladi. Komissiya yo'q.
Sham ichidagi tartib (konservativ): ochilish → qarshi ekstremum (Sell: high) → qulay ekstremum → yopilish. **Yangi savat faqat sham ochilishida ochiladi**; grid kengayishi, savat TP, trailing, DD himoyasi har nuqtada tekshiriladi. TP gap bo'lmasa TP narxida, gap bo'lsa joriy narxda bajariladi. Savat TP yopilishidan keyin cooldown qo'llanmaydi (EA da `m_last_close_time` faqat `CloseAll` da yangilanadi); DD himoyasi (`CloseAll`) dan keyin 5 daqiqa cooldown. Sirpanish yo'q (optimistik).

## 4. O'lchovlar
Yakuniy balans va sof foyda; maksimal drawdown (equity, sham ekstremumlari bo'yicha, % va $); DD-himoya ishga tushish soni va jami realizatsiya qilingan zarar; maksimal bir vaqtdagi lot/leverage; eng uzun "suv ostida" davr; yillar bo'yicha foyda; oylik foydali oylar ulushi, eng yomon oy; **12 oylik oynalar** (har chorak boshlanishidan, balans $5,000 dan qayta boshlab): foydali oynalar ulushi, eng yomon oyna.
Sezgirlik: Both va Buy-only; stress xarajat; balans $3,000.

## 5. Qaror mezonlari (hammasi bajarilishi shart, asosiy variant)
- **G1:** butun davrda sof foyda > 0 (spred+swap bilan); **G2:** maksimal drawdown ≤ 30% (balansga nisbatan; foydalanuvchi skalping chegarasi); **G3:** DD-himoya ishga tushishlari soni ≤ 5 va hisob bankrot bo'lmaydi (equity ≤ 0 yo'q);
- **G4:** 12 oylik oynalarning ≥ 70% i foydali va eng yomon oyna ≥ −20%; **G5:** stress xarajatda ($0.50, swap 5%) sof foyda > 0; **G6:** 2018–2021 va 2022–2025 yarmlarida alohida sof foyda > 0.
Hammasi bajarilsa — "backtestda ishlaydi (dastlabki, simulyatsiya)"; aks holda FAIL.

## 6. Cheklovlar (oldindan)
Real tick yo'q (M1 sham, ichki yo'l taxmin), spred doimiy, sirpanish/requote yo'q, MT5 ning haqiqiy margin/stop-out mexanizmi soddalashtirilgan (DD himoyasi $2000 dan oldin stop-out bo'lmaydi deb faraz; 60 oz × $33 ≈ 2000$ — leverage 1:500 bo'lsa margin yetadi). Python qayta tiklash EA ning barcha tafsilotlarini (masalan, tick darajasidagi trailing) aynan takrorlamaydi. Bu isbot emas, taxminiy sinov.

## 7. Natijaga qarab
E'lon qilinadi; parametrlar o'zgartirilmaydi. Grid/martingale xususiyati: kichik foydalar ko'p, kam uchraydigan katta zarar; shuning uchun asosiy ko'rsatkichlar DD, DD-himoya soni va 12 oylik eng yomon oyna.

## 8. Eslatma
EA muallifi `COMMERCIALIZATION_GUIDE.md` da backtestlarga ishonmaslikni yozgan; bu sinov ham shu cheklovlarni tan oladi.

## 9. O'zgartirishlar jurnali
- 2026-11-04: sinov ishga tushirildi (backtest/gridea.py, reports/gridea_results.md). Natija: asosiy (Sell-only, .set) **O'TMADI** (G1–G6 hammasi bajarilmadi; hisob 2019 da yo'qoldi). Reja va mezonlarga o'zgartirish kiritilmadi. Eslatma: M1 ma'lumot qayta yuklandi (yangi muhit), davr 2018-01 → 2025-02 ga kesilgan.
