# Yangilik + full margin: balansni 5 barobar oshirish (oltin, pre-registered reja)

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Qoida foydalanuvchi tomonidan berilgan; yozilmagan joylarni (6-bo'lim) natijani ko'rmasdan muzlatdim. O'zgartirish faqat 8-bo'limdagi jurnalga.

## 1. Halol kutish (oldindan)
Full margin, stop-loss'siz, yagona qoida "5x yoki sliv": bu lotereya. Narx nolga drift qiladigan adolatli o'yinda 5x (+400%) ga yetmasdan −50% (margin call) ga tushish ehtimoli yuqori (taxminan 1/(1+8) ≈ 11% muvaffaqiyat kutiladi, 30 daqiqalik vaqt chegarasi uni yanada pasaytiradi); spred esa kutilgan natijani manfiy qiladi. Sinov shuni empirik o'lchaydi. **Muvaffaqiyat mezoni "5x ga yetgan kunlar borligi" emas**, balki o'rtacha yakuniy balans > 1 va 5x ga yetish ulushi tasodifiy yo'nalishdagi nazoratdan ishonchli yuqori bo'lishi (5-bo'lim).

## 2. Qoida (foydalanuvchi matni bo'yicha)
- XAUUSD, M1 narx yo'li. Boshlang'ich balans **1 birlik** (foizlarda hisoblanadi; 100$ ga ko'paytirish mumkin). Maqsad: balans 5 birlik (equity ≥ 5). Sliv: equity ≤ 0.10 yoki margin call (qaysi biri birinchi).
- **Yangiliklar:** yuqori ta'sirli AQSh: NFP, FOMC (Statement, Fed Funds Rate), CPI (m/m, Core m/m, y/y), GDP (Advance/Prelim/Second/Final q/q). ECB/BOE **kiritilmaydi** (kalendar vaqtlari ishonchsiz, 6.2).
- **Trend:** yangilik chiqishidan oldingi 60 daqiqalik harakat: yuqoriga → faqat Buy, pastga → faqat Sell (asosiy). Sezgirlik: 30 daqiqalik oyna; "birinchi impuls" varianti (yangilikdan keyingi 2 daqiqalik harakat yo'nalishi, kirish t+2 daqiqa).
- **Kirish (asosiy):** yangilik chiqish daqiqasida (t = chiqish vaqti; narx = t−1 daqiqa shamining yopilishi, ya'ni chiqish lahzasi), **full margin**: pozitsiya hajmi shunday tanlanadiki, ishlatilgan margin = boshlang'ich equity (margin level 100%). Stop-loss ham take-profit ham yo'q.
- **Chiqish:** equity ≥ 5 → hammasi yopiladi (muvaffaqiyat); equity ≤ 0.10 yoki margin level ≤ 50% → sliv; aks holda t + 30 daqiqada pozitsiya yopiladi, yakuniy balans yoziladi.
- Har yangilik alohida oyna (bir vaqtda chiqqan bir nechta yangilik bitta oyna).

## 3. Ma'lumot
XAUUSD M1 BID (ZombitX64, UTC), 2018-01-02 → 2025-02-28. Kalendar: Forex Factory (`forex_factory_cache.csv`); sana fayldan, **vaqt standart ET jadvalidan** (NFP/CPI/GDP 08:30 ET; FOMC 14:00 ET), AQSh DST bilan UTC ga (`STRATEGY_NEXT.md` jurnalidagi tuzatish bilan bir xil sabab). Oynada M1 shamlar to'liq bo'lishi kerak (yo'q bo'lsa tashlanadi).

## 4. Parametrlar (muzlatilgan)
Leverage 1:500; margin = lot(oz) × narx / 500; margin call: equity / ishlatilgan margin ≤ 50%. Spred **$0.80/oz** (yangilik paytida kengaygan; boshida floating ga kiradi), sezgirlik $0.30. Sirpanish yo'q (optimistik). Shamlar ichida tartib konservativ: ochilish → qarshi ekstremum → qulay ekstremum → yopilish; qarshi nuqtada sliv, qulay nuqtada maqsad. Equity manfiy bo'lmaydi.
Sezgirlik: leverage 1:200 va 1:1000; trend oynasi 30 daqiqa; "birinchi impuls" varianti; yo'nalish tasodifiy (nazorat).

## 5. O'lchovlar (foydalanuvchi so'ragan + nazorat)
Oynalar soni; 5x ga yetgan kunlar (soni va %, Wilson 95%); sliv bo'lgan kunlar; 30 daqiqada ikkalasi ham bo'lmaganlar; o'rtacha vaqt (daqiqa) 5x ga yetganda va sliv bo'lganda; yillar bo'yicha taqsimot; **o'rtacha yakuniy balans** (boshlang'ich 1); yakuniy balansning taqsimoti (eng yaxshi/eng yomon).
**Nazorat:** shu oynalar, yo'nalish har oynada tasodifiy (1000 marta); 5x ulushi va o'rtacha yakuniy balans taqsimoti; real natija tasodifiy nazoratdan ishonchli yuqorimi (p).
**Qaror:** (a) o'rtacha yakuniy balans > 1.00 va (b) tasodifiy nazorat bo'yicha p ≤ 0.10 (o'rtacha yakuniy balans bo'yicha). Aks holda "ustunlik yo'q; lotereya".

## 6. Aniqlashtirishlar va cheklovlar
1. **1 birlik full margin** da hajm foizlar bo'yicha hisoblanadi; haqiqiy brokerda minimal lot cheklovi bo'lishi mumkin (100$ da 0.01 lot = 1 oz margin ~ 8$ — mumkin).
2. **ECB/BOE** kiritilmaydi: kalendar vaqtlari ishonchsiz (Eron/AQSh DST siljishi) va standart jadval aniq emas; ro'yxat faqat AQSh yangiliklari.
3. Kalendar sanalari uchinchi tomondan; yangilik vaqti standartdan farq qilgan kunlar (kechiktirilgan e'lon) xato qo'shadi.
4. Yangilik paytida spred, sirpanish va to'ldirmaslik real ijroni ancha yomonlashtiradi.
5. Natija o'tgan ma'lumotda; real pulga tavsiya emas.

## 7. Natijaga qarab nima qilamiz
E'lon qilinadi; parametrlar "yaxshilanmaydi". Ustunlik topilmasa — qoida lotereya sifatida hujjatlanadi.

## 8. O'zgartirishlar jurnali
(hozircha bo'sh)
