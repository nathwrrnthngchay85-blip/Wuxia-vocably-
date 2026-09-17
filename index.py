# -*- coding: utf-8 -*-
"""
武侠词汇录 — Flashcard Survival (Wuxia Edition)
เกมฝึกคำศัพท์จีนแบบเล่นคนเดียว เน้น Active Recall + Spaced Repetition
รันด้วย: python wuxia_vocab.py
"""

import random
import time
import os

# ─────────────────────────────────────────────────────────
# คลังคำศัพท์:  (汉字, พินอิน, [ความหมายที่ยอมรับได้])
# ─────────────────────────────────────────────────────────
VOCAB = [
    ("丝毫",     "sīháo",        ["แม้แต่น้อย", "เพียงเล็กน้อย"]),
    ("压迫",     "yāpò",         ["กดขี่", "บีบคั้น"]),
    ("电压",     "diànyā",       ["แรงดันไฟฟ้า"]),
    ("高压",     "gāoyā",        ["แรงดันสูง", "ความดันสูง", "แรงกดดัน"]),
    ("气压",     "qìyā",         ["ความกดอากาศ"]),
    ("压力",     "yālì",         ["ความกดดัน", "ความเครียด"]),
    ("压缩",     "yāsuō",        ["อัด", "บีบอัด"]),
    ("压制",     "yāzhì",        ["ปราบปราม", "กดขี่", "ยับยั้ง"]),
    ("镇压",     "zhènyā",       ["ปราบปราม", "กดขี่ด้วยความรุนแรง"]),
    ("至今",     "zhìjīn",       ["จนถึงตอนนี้", "จนบัดนี้"]),
    ("至少",     "zhìshǎo",      ["อย่างน้อย"]),
    ("甚至",     "shènzhì",      ["แม้กระทั่ง", "ถึงกับ"]),
    ("甚至于",   "shènzhìyú",    ["แม้กระทั่ง", "ถึงกับ"]),
    ("以至",     "yǐzhì",        ["จนกระทั่ง", "ถึงขนาดที่"]),
    ("至于",     "zhìyú",        ["ส่วน", "สำหรับ", "ถึงกับ"]),
    ("自始至终", "zìshǐzhìzhōng",["ตั้งแต่ต้นจนจบ", "ตลอดมา"]),
    ("竹子",     "zhúzi",        ["ไม้ไผ่"]),
    ("血液",     "xuèyè",        ["เลือด"]),
    ("鲜血",     "xiānxuè",      ["เลือดสด"]),
    ("血管",     "xuèguǎn",      ["หลอดเลือด", "เส้นเลือด"]),
    ("血汗",     "xuèhàn",       ["เลือดและเหงื่อ"]),
    ("伞",       "sǎn",          ["ร่ม"]),
    ("斗争",     "dòuzhēng",     ["ต่อสู้", "ดิ้นรน"]),
    ("战争",     "zhànzhēng",    ["สงคราม"]),
    ("争论",     "zhēnglùn",     ["โต้เถียง", "ถกเถียง", "การโต้เถียง"]),
    ("争取",     "zhēngqǔ",      ["แย่งชิง", "ต่อสู้เพื่อ", "พยายาม"]),
    ("竞争",     "jìngzhēng",    ["แข่งขัน", "การแข่งขัน"]),
    ("力争",     "lìzhēng",      ["พยายามอย่างเต็มที่", "มุ่งมั่น"]),
    ("争夺",     "zhēngduó",     ["แย่งชิง", "ช่วงชิง"]),
    ("并且",     "bìngqiě",      ["และ", "อีกทั้ง"]),
    ("严格",     "yángé",        ["เข้มงวด", "เคร่งครัด"]),
    ("严肃",     "yánsù",        ["เคร่งขรึม", "จริงจัง"]),
    ("严重",     "yánzhòng",     ["ร้ายแรง", "รุนแรง"]),
    ("庄严",     "zhuāngyán",    ["สง่างาม", "เคร่งขรึม"]),
    ("严禁",     "yánjìn",       ["ห้ามเด็ดขาด", "ห้ามอย่างเคร่งครัด"]),
    ("严厉",     "yánlì",        ["เข้มงวด", "รุนแรง"]),
]

MAX_QI = 3                    # 内力 เริ่มต้น
WRONG_LOG = "wrong_words.txt" # ไฟล์บันทึกคำที่ตอบผิด

RANKS = [
    (0,  "无名小卒", "ไพร่พลไร้นาม"),
    (5,  "门下弟子", "ศิษย์ในสำนัก"),
    (12, "江湖侠客", "จอมยุทธ์พเนจร"),
    (20, "一代大侠", "ยอดคนแห่งยุค"),
    (30, "武林宗师", "ปรมาจารย์บู๊ลิ้ม"),
]


# ─────────────────────────────────────────────────────────
# ฟังก์ชันช่วยเหลือ
# ─────────────────────────────────────────────────────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")


def normalize(text):
    """ตัดช่องว่างและอักขระกวนใจออก เพื่อเทียบคำตอบแบบยืดหยุ่น"""
    return text.replace(" ", "").replace("-", "").strip().lower()


def is_correct(user_answer, meanings):
    """ถูกถ้าตรงกับความหมายใดความหมายหนึ่ง (หรือเป็นส่วนหนึ่งของกันและกัน)"""
    ua = normalize(user_answer)
    if not ua:
        return False
    for m in meanings:
        nm = normalize(m)
        if ua == nm or (len(ua) >= 3 and (ua in nm or nm in ua)):
            return True
    return False


def get_rank(score):
    title = RANKS[0]
    for need, cn, th in RANKS:
        if score >= need:
            title = (need, cn, th)
    return title


def qi_bar(qi):
    return "🔴" * qi + "⚪" * (MAX_QI - qi)


def banner():
    print("═" * 56)
    print("        ⚔️  武 侠 词 汇 录  ⚔️")
    print("        ตำนานจอมยุทธ์อักษรจีน")
    print("═" * 56)


def save_wrong(wrong_set):
    if not wrong_set:
        return
    with open(WRONG_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n--- บทเรียนวันที่ {time.strftime('%Y-%m-%d %H:%M')} ---\n")
        for hanzi, pinyin, meanings in wrong_set:
            f.write(f"{hanzi} | {pinyin} | {', '.join(meanings)}\n")


# ─────────────────────────────────────────────────────────
# เกมหลัก
# ─────────────────────────────────────────────────────────
def play():
    clear()
    banner()
    print("""
  📜 เจ้าคือศิษย์ใหม่ที่เพิ่งเหยียบเข้าประตูสำนัก
     เบื้องหน้าคือ "หอคอยอักษร" สูงเสียดฟ้า
     ทุกชั้นมีอักษรจีนเฝ้าอยู่ ตอบถูกจึงจะผ่านไปได้

  กติกา:
    • ข้าจะแสดงอักษรจีน เจ้าต้องพิมพ์ "คำแปลไทย" เอง
    • ตอบผิด = เสีย 内力 1 หน่วย และอักษรนั้นจะย้อนกลับมาหาเจ้า
    • 内力 หมด = ตกหอคอย เกมจบ
    • พิมพ์ "?" เพื่อขอดูพินอิน (ไม่เสีย 内力 แต่คำนั้นถือว่ายังไม่ผ่าน)
    • พิมพ์ "quit" เพื่อออกจากเกม
""")
    input("  กด Enter เพื่อเริ่มฝึกวิชา... ")

    deck = VOCAB[:]
    random.shuffle(deck)
    total = len(deck)

    qi = MAX_QI
    score = 0
    streak = 0
    best_streak = 0
    wrong_set = []
    hint_used = set()

    while deck and qi > 0:
        hanzi, pinyin, meanings = deck.pop(0)

        clear()
        banner()
        print(f"  内力 {qi_bar(qi)}    连击 {streak} 🔥    "
              f"ผ่านแล้ว {score}/{total}    เหลือในกอง {len(deck)}")
        print("─" * 56)
        print(f"\n\n            【  {hanzi}  】\n")
        if hanzi in hint_used:
            print(f"            พินอิน: {pinyin}\n")
        print("─" * 56)

        answer = input("  ✍️  แปลว่าอะไร? > ").strip()

        if answer.lower() in ("quit", "exit", "q"):
            print("\n  เจ้าเก็บดาบกลับสำนัก... แล้วพบกันใหม่")
            break

        if answer == "?":
            hint_used.add(hanzi)
            deck.insert(0, (hanzi, pinyin, meanings))  # ถามคำเดิมซ้ำทันที
            continue

        if is_correct(answer, meanings):
            score += 1
            streak += 1
            best_streak = max(best_streak, streak)
            print(f"\n  ✅ 好！ ถูกต้อง  →  {hanzi} ({pinyin}) = {', '.join(meanings)}")
            if streak > 0 and streak % 5 == 0:
                print(f"  🔥 连击 {streak} ครั้ง! ลมปราณเจ้าไหลลื่นดั่งสายน้ำ")
        else:
            qi -= 1
            streak = 0
            wrong_set.append((hanzi, pinyin, meanings))
            print(f"\n  ❌ 错了！ คำตอบคือ  {hanzi} ({pinyin}) = {', '.join(meanings)}")
            print(f"  💥 เจ้าเสีย 内力 ไป 1 หน่วย  เหลือ {qi_bar(qi)}")
            # ── Spaced Repetition: เด้งกลับมาในอีก 2 คำ ──
            pos = min(2, len(deck))
            deck.insert(pos, (hanzi, pinyin, meanings))

        input("\n  กด Enter เพื่อไปต่อ... ")

    # ─── สรุปผล ───
    clear()
    banner()
    need, cn_rank, th_rank = get_rank(score)

    if qi <= 0:
        print("""
  💀 内力耗尽！ พลังภายในเจ้าหมดสิ้น
     เจ้าร่วงจากหอคอยอักษร... แต่จอมยุทธ์ที่แท้จริงย่อมลุกขึ้นใหม่
""")
    elif not deck:
        print("""
  🏆 通关成功！ เจ้าพิชิตหอคอยอักษรได้สำเร็จ!
     ชื่อของเจ้าจะถูกจารึกไว้ในตำนานบู๊ลิ้ม
""")

    print("─" * 56)
    print(f"  คำที่ผ่าน       : {score} / {total}")
    print(f"  连击 สูงสุด     : {best_streak} ครั้ง")
    print(f"  内力 ที่เหลือ   : {qi_bar(qi)}")
    print(f"  ตำแหน่ง        : {cn_rank}  ({th_rank})")
    print("─" * 56)

    if wrong_set:
        uniq = {w[0]: w for w in wrong_set}.values()
        print(f"\n  📕 อักษรที่เจ้ายังเอาชนะไม่ได้ ({len(uniq)} คำ):")
        for hanzi, pinyin, meanings in uniq:
            print(f"     {hanzi:<6} {pinyin:<14} {', '.join(meanings)}")
        save_wrong(list(uniq))
        print(f"\n  💾 บันทึกไว้ในไฟล์ '{WRONG_LOG}' แล้ว — พรุ่งนี้มาชำระแค้นต่อ")
    else:
        print("\n  ✨ ไร้ที่ติ! เจ้าไม่พลาดแม้แต่อักษรเดียว")

    print()


if __name__ == "__main__":
    while True:
        play()
        again = input("  ฝึกวิชาอีกรอบหรือไม่? (y/n) > ").strip().lower()
        if again != "y":
            print("\n  江湖再见！ แล้วพบกันใหม่ในยุทธภพ ⚔️\n")
            break