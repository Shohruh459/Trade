# Yangilik "straddle" EA (oltin): ikki tomonlama kutish orderlari, bittasi ishlasa qarshisi bekor, full margin (pre-registered reja)

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Qoida foydalanuvchi g'oyasi; yozilmagan joylarni (6-bo'lim) natijani ko'rmasdan muzlatdim. Parametrlar sozlanmaydi. O'zgartirish faqat 9-bo'limdagi jurnalga.

## 1. G'oya va halol kutish
Yangilik chiqishidan oldin ikki tomonga stop-order qo'yiladi (Buy Stop yuqorida, Sell Stop pastda); biri ishlasa qarshisi darhol bekor qilinadi; pozitsiya vaqt bo'yicha yoki foyda maqsadida yopiladi; hajm full margin. Bu klassik "news straddle". Amalda (a) yangilik paytida spred 3–10 barobar kengayadi, (b) stop-orderlar sirpanish bilan to'ldiriladi, (c) bir daqiqada ikkala tomon ham tegib ketishi (whipsaw) tez-tez uchraydi. Kutish: ustunlik topilmaydi, xarajat va whipsaw uni yeydi; full margin esa zararni katta qiladi. Sinov buni M1 ma'lumotida konservativ taxminlar bilan o'lchaydi.

## 2. Qoida (muzlatilgan, asosiy variant)
- **Hodisalar:** AQSh yuqori ta'sirli: NFP, CPI (m/m, core m/m, y/y), GDP (advance/prelim/second/final), FOMC Statement / Federal Funds Rate. Sana kalendardan, vaqt standart ET jadvalidan (08:30 / 14:00 ET, AQSh DST) — `STRATEGY_NEWS_FULLMARGIN_5X.md` dagidek. Davr 2018-01 → 2025-02 (M1 to'liq bo'lgan hodisalar).
- **Orderlar:** t = chiqish daqiqasi. Ref = t−1 daqiqa shamining yopilishi. **Buy Stop = Ref + $2.50, Sell Stop = Ref − $2.50.** Orderlar t dan boshlab 3 daqiqa (3 ta M1 sham: t, t+1, t+2) amal qiladi; keyin bekor qilinadi.
- **OCO:** bir tomon to'lsa, qarshisi bekor qilinadi. **Whipsaw:** bir M1 shamda ikkala daraja ham tegsa — noaniq tartib: konservativ ravishda **zararli** hisoblanadi (stop-zarar + sirpanish + spred).
- **Stop-loss:** kirishdan $3.00 qarshi tomonda (foydalanuvchi qoidasida stop yo'q; full margin bilan stopsiz sinov hisobni yo'q qilgani uchun himoya stop qo'shildi; sezgirlikda stopsiz variant ham ko'rsatiladi).
- **Chiqish (birinchi bajarilgani):** (a) foyda maqsadi: kirishdan +$5.00 (limit); (b) stop-loss; (c) **vaqt: to'ldirilgandan 10 daqiqa keyin** yopilish narxida.
- **Hajm (ikki variant):** **F (full margin):** hajm = equity × 500 / narx (margin level 100%, leverage 1:500). **R (risk-asosli):** hisobning 2% i risk (stop masofasi $3.00 ga nisbatan). Variant R — amaliy nomzod; F — foydalanuvchi talabi (xavf ko'rsatish uchun).

## 3. Xarajat va ijro (konservativ, muzlatilgan)
Spred (aylanma) **$0.80**; stop-orderlar **sirpanishi $0.50** (kirishda) va stop-loss da $0.50; foyda maqsadi va vaqt chiqishida qo'shimcha sirpanish yo'q. To'ldirilgan sham ichida faqat yopilish narxi tekshiriladi (sham ichi tartibi noma'lum); keyingi shamlarda qarshi ekstremum avval. **Stress:** spred $1.50, sirpanish $1.00. Komissiya/swap yo'q.

## 4. O'lchovlar
Hodisalar soni; to'ldirilgan (bir tomon), whipsaw, to'ldirilmagan ulushlar; yutuq ulushi; o'rtacha sof natija (R varianti: % hisob; F varianti: % equity); butun yo'l (hodisalar vaqt tartibida, kompaund) final va maksimal drawdown; hisob yo'qolishi (equity ≤ 10%); yillar bo'yicha; yarmlar (2018–2021, 2022–2025).
**Tasodifiy vaqt nazorati:** shu qoida yangilik bo'lmagan tasodifiy vaqtlarda (07–20 UTC, ish kunlari, yangilikdan ±30 daqiqa tashqarida), 20,000 tasodifiy daqiqa; real o'rtacha sof natija shu taqsimotdagi bir xil o'lchamli tanlanmalar o'rtachasiga nisbatan (p = tasodifiy o'rtacha ≥ real).

## 5. Qaror mezonlari (hammasi shart; variant R uchun; variant F alohida e'lon qilinadi)
- **S1:** o'rtacha sof natija / hodisa > 0 va tasodifiy vaqt nazoratida p ≤ 0.10. **S2:** stress xarajatda ham o'rtacha > 0. **S3:** 2018–2021 va 2022–2025 yarmlarida alohida > 0. **S4:** butun yo'l maksimal drawdown ≤ 30% va hisob yo'qolmaydi. **S5:** hodisalar soni ≥ 150.
Hammasi bajarilsa — "dastlabki nomzod" (demo/forward kerak); aks holda FAIL.

## 6. Aniqlashtirishlar / cheklovlar
1. Bu M1 BID ma'lumot (tick yo'q): kirish/chiqish ketma-ketligi sham ichida noaniq; konservativ taxminlar shuning uchun. Haqiqiy brokerda stop-orderlar yangilik paytida **requote yoki rad etilishi**, spred keskin kengayishi mumkin (M1 bid ma'lumotda ko'rinmaydi): natija optimistik bo'lishi ehtimoli katta.
2. ECB/BOE kiritilmagan (kalendar vaqtlari ishonchsiz).
3. Parametrlar ($2.50 / $3.00 / $5.00 / 10 daqiqa / 3 daqiqa) a priori tanlangan, optimallashtirilmagan.
4. Sezgirlik (faqat ma'lumot): masofa $1.50 va $4.00; stop $2.00 va $5.00; ushlash 5 va 20 daqiqa; stopsiz; spred $0.30; leverage 1:200; faqat NFP/CPI/FOMC.

## 7. Natijaga qarab
PASS: demo EA spetsifikatsiyasi; FAIL: rad etiladi, parametrlar "yaxshilanmaydi". Natijadan qat'i nazar xavf (whipsaw ulushi, F varianti drawdowni) e'lon qilinadi.

## 8. Eslatma
Oldingi yangilik sinovlari (`STRATEGY_NEXT.md` N2, `STRATEGY_NEWS_FULLMARGIN_5X.md`) ustunlik topmagan: yo'nalishni bashorat qilish ham, trend bo'yicha full margin ham.

## 9. O'zgartirishlar jurnali
(hozircha bo'sh)
