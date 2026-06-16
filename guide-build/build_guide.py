# -*- coding: utf-8 -*-
"""Swiss-minimalist bilingual PDF guide: SEO / GEO / AEO with AI in 2026."""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor

# ---------- fonts ----------
FB = "/tmp/fonts/inter_extracted/extras/ttf"
MB = "/tmp/fonts/jbmono/fonts/ttf"
pdfmetrics.registerFont(TTFont("Inter",        f"{FB}/Inter-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Med",    f"{FB}/Inter-Medium.ttf"))
pdfmetrics.registerFont(TTFont("Inter-SB",     f"{FB}/Inter-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Bold",   f"{FB}/Inter-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Black",  f"{FB}/Inter-Black.ttf"))
pdfmetrics.registerFont(TTFont("Disp-Black",   f"{FB}/InterDisplay-Black.ttf"))
pdfmetrics.registerFont(TTFont("Mono",         f"{MB}/JetBrainsMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Mono-Med",     f"{MB}/JetBrainsMono-Medium.ttf"))
pdfmetrics.registerFont(TTFont("Mono-Bold",    f"{MB}/JetBrainsMono-Bold.ttf"))

# ---------- palette ----------
YELLOW = HexColor(0xFFF55F)
WHITE  = HexColor(0xFFFFFF)
BLACK  = HexColor(0x000000)
INK    = HexColor(0x0A0A0A)
GREEN  = HexColor(0x00A85A)   # iDeals-style green accent

PW, PH = A4                    # 595.28 x 841.89
LM, RM = 56, 56
CW = PW - LM - RM              # content width
TOP = 760                      # content top
BOTTOM = 92                    # content bottom limit

# ---------- helpers ----------
def tw(s, font, size, cs=0.0):
    w = stringWidth(s, font, size)
    if cs and len(s) > 1:
        w += cs * (len(s) - 1)
    return w

def trtext(c, x, y, s, font, size, cs=0.0, color=BLACK):
    to = c.beginText(); to.setTextOrigin(x, y); to.setFont(font, size)
    if cs: to.setCharSpace(cs)
    to.setFillColor(color); to.textOut(s)
    if cs: to.setCharSpace(0)   # reset; Tc is graphics state and persists past ET
    c.drawText(to)

def wrap(text, font, size, maxw, cs=0.0):
    out = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            trial = w if not cur else cur + " " + w
            if tw(trial, font, size, cs) <= maxw:
                cur = trial
            else:
                if cur:
                    out.append(cur)
                cur = w
        out.append(cur)
    return out

class Doc:
    def __init__(self, path, gtitle, foot_hint):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.page = 0
        self.gtitle = gtitle           # top-left running header
        self.cur_section = ""              # top-right
        self.foot_hint = foot_hint     # bottom-right base hint
        self.y = TOP
        self._newpage(furniture=True)

    # ----- page furniture -----
    def _furniture(self, cover=False):
        c = self.c
        bg = YELLOW if self.page == 1 else WHITE   # cover yellow, rest white
        c.setFillColor(bg); c.rect(0, 0, PW, PH, fill=1, stroke=0)
        c.setFillColor(BLACK)
        # top running header
        c.setFont("Mono-Med", 6.4)
        c.drawString(LM, 812, self.gtitle.upper())
        sec = (self.cur_section or "").upper()
        if sec:
            sw = stringWidth(sec, "Mono-Bold", 6.4)
            self._ychip(PW - RM - sw, 812, sec, "Mono-Bold", 6.4)
            c.setFillColor(BLACK)
        c.setLineWidth(0.8); c.setStrokeColor(BLACK)
        c.line(LM, 804, PW - RM, 804)
        # bottom
        c.line(LM, 70, PW - RM, 70)
        c.setFont("Mono-Bold", 6.4)
        c.drawString(LM, 58, "THE REACH")
        c.setFont("Mono-Med", 6.4)
        c.drawRightString(PW - RM, 58, f"{self.foot_hint} · P{self.page:02d}".upper())

    def _newpage(self, furniture=True):
        if self.page > 0:
            self.c.showPage()
        self.page += 1
        self._furniture()
        self.y = TOP

    def ensure(self, h):
        if self.y - h < BOTTOM:
            self._newpage()

    # ----- blocks -----
    def gap(self, h): self.y -= h

    # yellow accent shape (with black keyline so it reads on white)
    def _ybar(self, x, y, w, h):
        c = self.c
        c.setFillColor(YELLOW); c.setStrokeColor(BLACK); c.setLineWidth(0.6)
        c.rect(x, y, w, h, fill=1, stroke=1)

    # yellow highlight chip with black text (left-aligned), returns chip width
    def _ychip(self, x, y, text, font, size, padx=3):
        c = self.c
        w = stringWidth(text, font, size)
        c.setFillColor(YELLOW); c.setStrokeColor(BLACK); c.setLineWidth(0.4)
        c.rect(x - padx, y - 1.6, w + 2 * padx, size * 0.96 + 1.6, fill=1, stroke=0)
        c.setFillColor(BLACK); c.setFont(font, size); c.drawString(x, y, text)
        return w + 2 * padx

    def rule(self, color=BLACK, w=0.8, pad=10):
        self.ensure(pad * 2)
        self.y -= pad
        self.c.setStrokeColor(color); self.c.setLineWidth(w)
        self.c.line(LM, self.y, PW - RM, self.y)
        self.y -= pad

    def dotsep(self):
        self.ensure(24); self.y -= 14
        x = LM
        for i in range(3):
            self._ybar(x, self.y, 7, 7)
            x += 12
        self.y -= 10

    def cover(self, kicker, lines, subtitle):
        c = self.c
        c.setFillColor(GREEN); c.rect(LM, 690, 64, 12, fill=1, stroke=0)
        c.setFillColor(BLACK); c.setFont("Mono-Bold", 8)
        c.drawString(LM, 668, kicker.upper())
        # huge title
        size, cs, lead = 60, -2.6, 60
        y = 560
        for ln in lines:
            trtext(c, LM, y, ln, "Disp-Black", size, cs, BLACK); y -= lead
        # green underline accent
        c.setFillColor(GREEN); c.rect(LM, y + 30, 220, 10, fill=1, stroke=0)
        # subtitle
        c.setFillColor(INK)
        for ln in wrap(subtitle, "Inter-Med", 12.5, CW - 40):
            y -= 18
            c.setFont("Inter-Med", 12.5); c.drawString(LM, y, ln)
        self.y = BOTTOM  # force next content to new page

    def section(self, num, title, header, hint):
        self.cur_section = header
        self.foot_hint = hint
        self._newpage()
        c = self.c
        self._ychip(LM, self.y, f"SECTION {num}", "Mono-Bold", 8)
        self.y -= 8
        for ln in wrap(title, "Inter-Black", 27, CW, cs=-0.9):
            self.y -= 31
            trtext(c, LM, self.y, ln, "Inter-Black", 27, -0.9, BLACK)
        self.y -= 6
        self._ybar(LM, self.y, 46, 5)
        self.y -= 22; c.setFillColor(BLACK)

    def h3(self, text):
        self.ensure(30); self.y -= 8
        for ln in wrap(text, "Inter-Bold", 13.5, CW, cs=-0.2):
            self.y -= 18
            trtext(self.c, LM, self.y, ln, "Inter-Bold", 13.5, -0.2, BLACK)
        self.y -= 6

    def para(self, text, color=INK, size=10.5, lead=15.4):
        self.c.setFillColor(color)
        for ln in wrap(text, "Inter", size, CW):
            self.ensure(lead)
            self.y -= lead
            self.c.setFont("Inter", size); self.c.drawString(LM, self.y, ln)
        self.y -= 5

    def bullets(self, items, lead=15.2, gap=4):
        for it in items:
            lines = wrap(it, "Inter", 10.5, CW - 18)
            for i, ln in enumerate(lines):
                self.ensure(lead); self.y -= lead
                if i == 0:
                    self._ybar(LM + 1, self.y + 2.2, 5, 5)
                self.c.setFillColor(INK); self.c.setFont("Inter", 10.5)
                self.c.drawString(LM + 18, self.y, ln)
            self.y -= gap

    def numbered(self, items):
        # items: list of (title, desc)
        for idx, (t, d) in enumerate(items, 1):
            head = wrap(t, "Inter-Bold", 11, CW - 26, cs=-0.2)
            self.ensure(16 + len(head) * 15)
            self.y -= 16
            self._ychip(LM, self.y, f"{idx:02d}", "Inter-Black", 12, padx=2.5)
            for i, ln in enumerate(head):
                if i: self.y -= 14
                trtext(self.c, LM + 26, self.y, ln, "Inter-Bold", 11, -0.2, BLACK)
            if d:
                for ln in wrap(d, "Inter", 10, CW - 26):
                    self.ensure(13.6); self.y -= 13.6
                    self.c.setFillColor(INK); self.c.setFont("Inter", 10)
                    self.c.drawString(LM + 26, self.y, ln)
            self.y -= 7

    def callout(self, label, text):
        lines = wrap(text, "Inter-SB", 12, CW - 36)
        h = 22 + len(lines) * 16 + 16
        self.ensure(h + 8); self.y -= 8
        top = self.y; box_h = 18 + len(lines) * 16 + 14
        self.c.setFillColor(BLACK)
        self.c.rect(LM, top - box_h, CW, box_h, fill=1, stroke=0)
        self.c.setFillColor(YELLOW); self.c.rect(LM, top - box_h, 6, box_h, fill=1, stroke=0)
        yy = top - 18
        self.c.setFillColor(YELLOW); self.c.setFont("Mono-Bold", 7.5)
        self.c.drawString(LM + 20, yy, label.upper()); yy -= 14
        for ln in lines:
            self.c.setFillColor(YELLOW); self.c.setFont("Inter-SB", 12)
            self.c.drawString(LM + 20, yy, ln); yy -= 16
        self.y = top - box_h - 10

    def quote(self, text):
        lines = wrap(text, "Inter-Black", 18, CW - 20, cs=-0.5)
        self.ensure(len(lines) * 24 + 24); self.y -= 14
        self._ybar(LM, self.y - len(lines)*24 + 18, 6, len(lines)*24)
        for ln in lines:
            self.y -= 24
            trtext(self.c, LM + 20, self.y, ln, "Inter-Black", 18, -0.5, BLACK)
        self.y -= 10

    def bigstat(self, number, text):
        self.ensure(70); self.y -= 8
        trtext(self.c, LM, self.y - 38, number, "Disp-Black", 46, -2, BLACK)
        nx = LM + tw(number, "Disp-Black", 46, -2) + 16
        tlines = wrap(text, "Inter-Med", 11, CW - (nx - LM))
        ty = self.y - 16
        for ln in tlines:
            self.c.setFont("Inter-Med", 11); self.c.setFillColor(INK)
            self.c.drawString(nx, ty, ln); ty -= 14.5
        self.y -= 52

    def statgrid(self, items):
        # items: list of (number, label); 3 per row
        col = CW / 3.0
        i = 0
        while i < len(items):
            row = items[i:i+3]
            # measure row height
            maxlines = 0
            for _, lab in row:
                maxlines = max(maxlines, len(wrap(lab, "Inter-Med", 8.4, col - 12)))
            rh = 40 + maxlines * 11
            self.ensure(rh + 6)
            self.y -= 6
            for j, (num, lab) in enumerate(row):
                x = LM + j * col
                self._ybar(x, self.y - 2, 22, 4)
                trtext(self.c, x, self.y - 30, num, "Inter-Black", 25, -1, BLACK)
                ly = self.y - 44
                for ln in wrap(lab, "Inter-Med", 8.4, col - 12):
                    self.c.setFont("Inter-Med", 8.4); self.c.setFillColor(INK)
                    self.c.drawString(x, ly, ln); ly -= 11
            self.y -= rh
            i += 3

    def compare(self, left_title, right_title, rows):
        # two-column: was / now
        colw = (CW - 20) / 2.0
        xL = LM; xR = LM + colw + 20
        self.ensure(26); self.y -= 18
        self.c.setFont("Mono-Bold", 7.5); self.c.setFillColor(BLACK)
        self.c.drawString(xL, self.y, left_title.upper())
        self._ychip(xR, self.y, right_title.upper(), "Mono-Bold", 7.5)
        self.c.setFillColor(BLACK); self.y -= 6
        self.c.setLineWidth(0.8); self.c.line(LM, self.y, PW - RM, self.y); self.y -= 4
        for label, was, now in rows:
            wl = wrap(was, "Inter", 9.6, colw)
            nl = wrap(now, "Inter-Med", 9.6, colw)
            rh = 13 + max(len(wl), len(nl)) * 13 + 8
            self.ensure(rh)
            self.y -= 13
            self._ychip(xL, self.y, label.upper(), "Mono-Bold", 6.6)
            self.c.setFillColor(BLACK)
            yy = self.y - 13
            for k in range(max(len(wl), len(nl))):
                if k < len(wl):
                    self.c.setFont("Inter", 9.6); self.c.setFillColor(INK)
                    self.c.drawString(xL, yy, wl[k])
                if k < len(nl):
                    self.c.setFont("Inter-Med", 9.6); self.c.setFillColor(BLACK)
                    self.c.drawString(xR, yy, nl[k])
                yy -= 13
            self.y = yy - 6
            self.c.setStrokeColor(HexColor(0x000000)); self.c.setLineWidth(0.3)
            self.c.line(LM, self.y + 3, PW - RM, self.y + 3)

    def save(self):
        self.c.showPage_done = True
        self.c.save()


# =================================================================
# CONTENT
# =================================================================
def build(doc, S):
    doc.cover(S["kicker"], S["cover_lines"], S["cover_sub"])

    for sec in S["sections"]:
        doc.section(sec["num"], sec["title"], sec["header"], sec["hint"])
        for blk in sec["blocks"]:
            kind = blk[0]
            if kind == "h3": doc.h3(blk[1])
            elif kind == "para": doc.para(blk[1])
            elif kind == "bullets": doc.bullets(blk[1])
            elif kind == "numbered": doc.numbered(blk[1])
            elif kind == "callout": doc.callout(blk[1], blk[2])
            elif kind == "quote": doc.quote(blk[1])
            elif kind == "bigstat": doc.bigstat(blk[1], blk[2])
            elif kind == "statgrid": doc.statgrid(blk[1])
            elif kind == "compare": doc.compare(blk[1], blk[2], blk[3])
            elif kind == "dotsep": doc.dotsep()
            elif kind == "rule": doc.rule()
    doc.save()


# ---- import content modules ----
import content_en, content_ru

EN = content_en.DATA
RU = content_ru.DATA

OUT = "/home/user/Claude"
d1 = Doc(f"{OUT}/AI-Search-2026-Guide-EN.pdf", "THE REACH — AI SEARCH FIELD GUIDE", "SEO·GEO·AEO 2026")
build(d1, EN)
d2 = Doc(f"{OUT}/AI-Search-2026-Guide-RU.pdf", "THE REACH — ГАЙД ПО AI-ПОИСКУ", "SEO·GEO·AEO 2026")
build(d2, RU)
print("done")
