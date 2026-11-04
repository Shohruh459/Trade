# Yangilik straddle: katta TP, har safar $10 risk, maqsad $100 → $1000 yoki sliv (pre-registered qo'shimcha reja)

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** `STRATEGY_STRADDLE.md` ga qo'shimcha; parametrlar muzlatilgan. O'zgartirish faqat 5-bo'limdagi jurnalga.

## 1. Foydalanuvchi o'zgartirishi
TP kichik bo'lmasin: maqsad **depozitni 10 barobarga ko'tarish yoki sliv**; **har safar $10 risk**.

## 2. Qoida
- Hodisalar, orderlar (±$2.50, 3 daqiqa, OCO), whipsaw (zararli), stop $3.00 — `STRATEGY_STRADDLE.md` dagidek.
- **Katta TP:** kirishdan **+$15.00** (stop masofasining 5 barobari); ushlash vaqti **30 daqiqa** (katta TP ga vaqt berish uchun; 10 daqiqa o'rniga). Vaqt chiqishi yopilish narxida.
- **Xarajat:** spred $0.80, sirpanish $0.50 (asosiy); stress — spred $1.50 va sirpanish $1.00.
- **Hajm:** har hodisada **risk = $10** (hisobdan qat'i nazar): hajm (oz) = 10 / (stop + sirpanish + spred) = 10 / 4.30; pozitsiya P&L = (sof natija/oz) × hajm. Hajm kompaundlanmaydi.
- **Hisob:** boshlang'ich $100. Hodisalar vaqt tartibida. **Muvaffaqiyat:** balans ≥ $1,000 (10×). **Sliv:** hodisadan keyin balans < $10 (keyingi $10 riskni ko'tara olmaydi). Aks holda ma'lumot tugaguncha (2025-02) davom etadi.
- Margin: 1:500, ~2.3 oz × narx / 500 ≈ $20 — $100 hisobda yetadi (margin call modellashtirilmagan, tavsif sifatida).

## 3. Sinov (o'lchovlar)
a) **Tarixiy yo'llar:** har hodisadan boshlanuvchi yo'l (293 ta, kesishuvchi): % muvaffaqiyat / sliv / ikkalasi ham bo'lmagan (ma'lumot tugagan), muvaffaqiyat/sliv gacha median hodisa soni, ikkalasi ham bo'lmaganlar yakuniy balansi.
b) **Monte-Karlo (iid):** haqiqiy hodisa natijalaridan qaytarib tanlash bilan 20,000 yo'l, 293 hodisagacha: xuddi shu ulushlar; muvaffaqiyat ehtimoli adolatli o'yin chegarasi bilan solishtiriladi (+90 birlik ga yetish, −9 birlik ga tushishdan oldin: 9/(90+9) ≈ 9.1%; manfiy kutilgan natija bilan bundan past).
c) Sezgirlik: TP $9 va $30 va $60; risk $5 va $20; stress xarajat; ushlash 10 va 60 daqiqa.
**Qaror ko'rsatkichi:** muvaffaqiyat ehtimoli (tarixiy va Monte-Karlo) adolatli chegaradan (9.1%) ishonchli yuqorimi va sliv ulushi nechta. Kutish: yuqori emas.

## 4. Cheklovlar
M1 BID ma'lumot, konservativ ijro taxminlari (`STRATEGY_STRADDLE.md` 6-bo'lim); 293 hodisa; yo'llar kesishadi (mustaqil emas); real brokerda yangilik paytida requote/spred; natija lotereya ehtimolini ko'rsatadi, foyda isboti emas.

## 5. O'zgartirishlar jurnali
- 2026-11-04: sinov ishga tushirildi (backtest/straddle10x.py, reports/straddle10x_results.md). Reja o'zgartirilmadi.
