# Kunlik qoida qatlami (micro hisob): −3 ta zarar, +10$ maqsad, +5$ ni saqlash (pre-registered reja)

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Parametrlar muzlatilgan, sozlanmaydi. O'zgartirish faqat 8-bo'limdagi jurnalga.

## 1. G'oya va halol kutish
Foydalanuvchi qoidasi: kuniga **3 marta $1 yo'qotilsa savdo yopiladi**; **+$10 kunlik foyda** bo'lsa yopiladi; **+$5 va undan yuqori** foyda bo'lsa uni saqlab qolish. Micro hisobda ishlash uchun tayyorlash.
Bu qatlam **risk menejmenti**: kunlik zararni $3 ga cheklaydi, lekin **o'zi ustunlik yaratmaydi**: kirish signalida ustunlik bo'lmasa, kunlik chegaralar kutilgan natijani o'zgartirmaydi (faqat taqsimotni siljitadi), spred esa uni manfiy qiladi (martingale va N3 sinovlarida ko'rilgan). Shuning uchun bu sinov ikki savolga javob beradi: (1) qatlam sinalgan eng yaxshi kirish qoidasi bilan sof foyda beradimi; (2) qatlam oylik barqarorlikni (foydali oylar ulushi) yaxshilaydimi.

## 2. Qatlam qoidalari (muzlatilgan)
- **Birlik:** har savdoda risk = $1 (stop masofasi bo'yicha lot hisoblanadi; micro/cent hisobda kasr lot ruxsat etiladi deb faraz). Boshlang'ich balans $100. Sof natija R·$1 (kompaundsiz).
- **Kun:** UTC sana (kirish sanasi bo'yicha). Kun ichidagi savdolar vaqt tartibida.
- **Yopish shartlari (birinchi bajarilgani):** (a) shu kunda 3 ta zararli savdo (net R < 0); (b) kunlik natija ≥ +$10; (c) **foydani saqlash:** kunlik natija bir marta ≥ +$5 ga yetgandan keyin, savdodan keyingi natija < +$5 ga tushsa — kun yopiladi. Shart savdo yopilgandan keyin tekshiriladi (ochiq savdo o'rtasida emas).
- Boshqa filtrlar qoida bilan bir xil (sessiya, trend, yangilik).

## 3. Kirish qoidasi (sinalgan eng yaxshi, o'zgartirilmagan)
`STRATEGY_M15.md` dagi oltin qoidasi (Daily+H4 bias, M15 breakout, ATR_H1 stop 1×/TP 2×, 07–16 UTC, yangilik filtri), faqat kuniga savdolar chegarasi 2 o'rniga **20** va "3 ketma-ket zarar → 24 soat" o'chirilgan (uning o'rniga kunlik qatlam). Ma'lumot, xarajat (spred $0.30, stress $0.50), davr: `STRATEGY_M15.md` dagidek (2019-01 → 2025-02).
Eslatma: shu qoida o'z rejasida FAIL bo'lgan (xarajatsiz o'rtacha ≈ 0). Bu sinov uning ustiga qatlam qo'shish ta'sirini o'lchaydi, qoidani qayta baholamaydi.

## 4. O'lchovlar
Qatlamsiz (baza) va qatlam bilan: savdolar soni, o'rtacha net R, jami $ foyda, final balans ($100 dan), maksimal drawdown ($ va %), foydali kunlar ulushi, kunlik chegaralarga yetgan kunlar soni (−3 zarar / +10 / +5 saqlash), foydali oylar ulushi, eng yomon oy ($), eng uzun zararli oylar ketma-ketligi, yillar bo'yicha. 12 oylik oynalar (har chorak boshlanishi) foydali ulushi.
Tasodifiy nazorat: baza savdolar ketma-ketligida qatlam ta'siri tekshiriladi — savdo natijalari har kun ichida **tasodifiy tartibda** aralashtiriladi (1000 marta), qatlam bilan o'rtacha jami foyda taqsimoti; real jami foyda shu taqsimotga nisbatan (qatlam vaqt tartibidan foyda olayaptimi).

## 5. Qaror mezonlari (hammasi shart; qatlam bilan)
- **D1:** butun davrda sof foyda > 0 va 2019–2021 hamda 2022–2025 yarmlarida alohida > 0.
- **D2:** maksimal drawdown ≤ 30% ($100 balansga nisbatan).
- **D3:** foydali oylar ulushi ≥ 60% va eng yomon oy ≥ −$10.
- **D4:** stress xarajatda ($0.50) sof foyda > 0.
- **D5:** 12 oylik oynalarning ≥ 70% i foydali.
Hammasi bajarilsa — "micro hisob (demo) uchun tayyorlashga arziydi (dastlabki)"; aks holda FAIL: real/micro pulda ishlatish tavsiya qilinmaydi.

## 6. Natijaga qarab
- **PASS:** MT5 EA spetsifikatsiyasi va kodi tayyorlanadi (kunlik chegaralar, lot hisobi), demo ≥ 3 oy.
- **FAIL:** qatlam alohida risk-nazorat vositasi sifatida hujjatlanadi (kunlik zararni $3 ga cheklash foydali, lekin foyda manbai emas); kirish signali bo'lmasa daromad ham bo'lmaydi.

## 7. Cheklovlar
Qatlam savdolar tartibiga bog'liq (sham ichidagi tartib taxmin), kunlik chegara ochiq savdo o'rtasida emas yopilgandan keyin tekshiriladi (real EA da floating bo'yicha ham tekshirish mumkin), spred doimiy, sirpanish yo'q; kirish signali ilgari FAIL bo'lgan.

## 8. O'zgartirishlar jurnali
(hozircha bo'sh)
