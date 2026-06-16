# -*- coding: utf-8 -*-
"""AI-Search guide rebuilt to match the Claude Cowork reference design."""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor

FB = "/tmp/fonts/inter_extracted/extras/ttf"; MB = "/tmp/fonts/jbmono/fonts/ttf"
for n, f in [("Inter","Inter-Regular"),("Inter-Med","Inter-Medium"),("Inter-SB","Inter-SemiBold"),
             ("Inter-Bold","Inter-Bold"),("Inter-Black","Inter-Black"),("Disp-Black","InterDisplay-Black")]:
    pdfmetrics.registerFont(TTFont(n, f"{FB}/{f}.ttf"))
for n, f in [("Mono","JetBrainsMono-Regular"),("Mono-Med","JetBrainsMono-Medium"),("Mono-Bold","JetBrainsMono-Bold")]:
    pdfmetrics.registerFont(TTFont(n, f"{MB}/{f}.ttf"))

YELLOW = HexColor(0xFFF55F); WHITE = HexColor(0xFFFFFF); BLACK = HexColor(0x000000)
INK = HexColor(0x0A0A0A); TEAL = HexColor(0x1FA89B)
PW, PH = A4; LM, RM = 56, 56; CW = PW - LM - RM; TOP = 762; BOTTOM = 92
NUMW = 128  # section opener left number column

def tw(s, font, size, cs=0.0):
    w = stringWidth(s, font, size)
    return w + cs*(len(s)-1) if cs and len(s) > 1 else w

def trtext(c, x, y, s, font, size, cs=0.0, color=BLACK):
    to = c.beginText(); to.setTextOrigin(x, y); to.setFont(font, size)
    if cs: to.setCharSpace(cs)
    to.setFillColor(color); to.textOut(s)
    if cs: to.setCharSpace(0)
    c.drawText(to)

def wrap(text, font, size, maxw, cs=0.0):
    out = []
    for para in str(text).split("\n"):
        cur = ""
        for w in para.split(" "):
            t = w if not cur else cur + " " + w
            if tw(t, font, size, cs) <= maxw: cur = t
            else:
                if cur: out.append(cur)
                cur = w
        out.append(cur)
    return out

class Doc:
    def __init__(self, path, gtitle, cover_tr, foot_left):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.page = 0; self.gtitle = gtitle; self.cover_tr = cover_tr
        self.foot_left = foot_left; self.cur_section = ""; self.y = TOP
        self._newpage()

    def _logo(self):
        c = self.c
        for (dx, dy, col) in [(0, 6, BLACK), (6, 6, TEAL), (0, 0, BLACK), (6, 0, BLACK)]:
            c.setFillColor(col); c.circle(LM + 1.4 + dx, 810 + dy, 2.2, fill=1, stroke=0)
        c.setFillColor(BLACK); c.setFont("Mono-Med", 6.4)
        c.drawString(LM + 20, 808.5, self.gtitle.upper())

    def _furniture(self):
        c = self.c; cover = self.page == 1
        c.setFillColor(YELLOW if cover else WHITE); c.rect(0, 0, PW, PH, fill=1, stroke=0)
        self._logo()
        c.setFillColor(BLACK); c.setFont("Mono-Med", 6.4)
        right = self.cover_tr if cover else self.cur_section
        if right: c.drawRightString(PW - RM, 808.5, right.upper())
        c.setLineWidth(0.8); c.setStrokeColor(BLACK); c.line(LM, 802, PW - RM, 802)
        c.line(LM, 70, PW - RM, 70)
        if not cover:
            c.setFont("Mono-Med", 6.4); c.drawString(LM, 58, self.foot_left.upper())
            c.setFont("Mono-Bold", 8); c.drawRightString(PW - RM, 57, f"{self.page:02d}")

    def _newpage(self):
        if self.page > 0: self.c.showPage()
        self.page += 1; self._furniture(); self.y = TOP

    def ensure(self, h):
        if self.y - h < BOTTOM: self._newpage()

    def _ytick(self, x, y, w, h):
        self.c.setFillColor(YELLOW); self.c.setStrokeColor(BLACK); self.c.setLineWidth(0.6)
        self.c.rect(x, y, w, h, fill=1, stroke=1)

    # ---------- blocks ----------
    def cover(self, kicker, lines, subtitle):
        c = self.c
        c.setFillColor(BLACK); c.setFont("Mono-Bold", 8); c.drawString(LM, 660, kicker.upper())
        y = 560
        for ln in lines:
            trtext(c, LM, y, ln, "Disp-Black", 58, -2.4, BLACK); y -= 58
        c.setFillColor(INK)
        y -= 14
        for ln in wrap(subtitle, "Inter-Med", 12.5, CW - 30):
            y -= 18; c.setFont("Inter-Med", 12.5); c.drawString(LM, y, ln)
        # cover footer
        c.setFillColor(BLACK); c.setFont("Mono-Med", 6.4); c.drawString(LM, 58, "THE REACH")
        c.drawRightString(PW - RM, 58, self.cover_tr.upper())
        self.y = BOTTOM

    def opener(self, num, title, header, intro):
        self.cur_section = header; self._newpage(); c = self.c
        rx = LM + NUMW; rw = CW - NUMW
        trtext(c, LM, TOP - 48, num, "Disp-Black", 64, -2, BLACK)
        c.setFillColor(BLACK); c.setFont("Mono-Bold", 8); c.drawString(rx, TOP - 6, f"SECTION {num}")
        ty = TOP - 26
        for ln in wrap(title, "Inter-Black", 25, rw, cs=-0.8):
            trtext(c, rx, ty, ln, "Inter-Black", 25, -0.8, BLACK); ty -= 29
        if intro:
            ty -= 8
            for ln in wrap(intro, "Inter-Med", 11.5, rw):
                trtext(c, rx, ty, ln, "Inter-Med", 11.5, 0, INK); ty -= 16
        self.y = min(TOP - 60, ty) - 16

    def para(self, text, size=10.5, lead=15.4):
        self.c.setFillColor(INK)
        for ln in wrap(text, "Inter", size, CW):
            self.ensure(lead); self.y -= lead
            self.c.setFont("Inter", size); self.c.drawString(LM, self.y, ln)
        self.y -= 5

    def h3(self, text):
        self.ensure(30); self.y -= 10
        for ln in wrap(text, "Inter-Bold", 13.5, CW, cs=-0.2):
            self.y -= 18; trtext(self.c, LM, self.y, ln, "Inter-Bold", 13.5, -0.2, BLACK)
        self.y -= 5

    def bullets(self, items, lead=15.2, gap=4):
        for it in items:
            lines = wrap(it, "Inter", 10.5, CW - 18)
            for i, ln in enumerate(lines):
                self.ensure(lead); self.y -= lead
                if i == 0:
                    self.c.setFillColor(BLACK); self.c.rect(LM + 1, self.y + 2.4, 4.5, 4.5, fill=1, stroke=0)
                self.c.setFillColor(INK); self.c.setFont("Inter", 10.5); self.c.drawString(LM + 18, self.y, ln)
            self.y -= gap

    def numbered(self, items):
        for idx, (t, d) in enumerate(items, 1):
            head = wrap(t, "Inter-Bold", 12, CW - 40, cs=-0.2)
            body = wrap(d, "Inter", 10, CW - 40) if d else []
            rh = 16 + len(head) * 15 + len(body) * 13.6 + 12
            self.ensure(rh)
            self.c.setStrokeColor(HexColor(0x000000)); self.c.setLineWidth(0.4)
            self.c.line(LM, self.y, PW - RM, self.y)
            self.y -= 16
            trtext(self.c, LM, self.y, f"{idx:02d}", "Inter-Black", 16, -0.5, BLACK)
            ty = self.y
            for ln in head:
                trtext(self.c, LM + 40, ty, ln, "Inter-Bold", 12, -0.2, BLACK); ty -= 15
            ty -= 2
            for ln in body:
                self.c.setFont("Inter", 10); self.c.setFillColor(INK); self.c.drawString(LM + 40, ty, ln); ty -= 13.6
            self.y = ty - 12

    def callout(self, label, text):
        lines = wrap(text, "Inter-SB", 11.5, CW - 36)
        box_h = 18 + len(lines) * 15.5 + 13
        self.ensure(box_h + 10); self.y -= 8; top = self.y
        self.c.setFillColor(YELLOW); self.c.setStrokeColor(BLACK); self.c.setLineWidth(1)
        self.c.rect(LM, top - box_h, CW, box_h, fill=1, stroke=1)
        yy = top - 18
        self.c.setFillColor(BLACK); self.c.setFont("Mono-Bold", 7.5); self.c.drawString(LM + 18, yy, label.upper()); yy -= 16
        for ln in lines:
            self.c.setFont("Inter-SB", 11.5); self.c.setFillColor(BLACK); self.c.drawString(LM + 18, yy, ln); yy -= 15.5
        self.y = top - box_h - 10

    def quote(self, text):
        lines = wrap(text, "Inter-Black", 18, CW - 16, cs=-0.4)
        self.ensure(len(lines) * 27 + 16); self.y -= 12
        for ln in lines:
            self.y -= 27
            w = tw(ln, "Inter-Black", 18, -0.4)
            self.c.setFillColor(YELLOW); self.c.rect(LM - 2, self.y - 4, w + 10, 24, fill=1, stroke=0)
            trtext(self.c, LM + 2, self.y, ln, "Inter-Black", 18, -0.4, BLACK)
        self.y -= 12

    def bigstat(self, number, text):
        self.ensure(70); self.y -= 8
        trtext(self.c, LM, self.y - 38, number, "Disp-Black", 44, -2, BLACK)
        nx = LM + tw(number, "Disp-Black", 44, -2) + 16
        ty = self.y - 16
        for ln in wrap(text, "Inter-Med", 11, CW - (nx - LM)):
            self.c.setFont("Inter-Med", 11); self.c.setFillColor(INK); self.c.drawString(nx, ty, ln); ty -= 14.5
        self.y -= 52

    def statgrid(self, items):
        col = CW / 3.0; i = 0
        while i < len(items):
            row = items[i:i+3]
            ml = max(len(wrap(l, "Inter-Med", 8.4, col - 12)) for _, l in row)
            rh = 40 + ml * 11
            self.ensure(rh + 6); self.y -= 6
            for j, (num, lab) in enumerate(row):
                x = LM + j * col
                self._ytick(x, self.y - 2, 22, 4)
                trtext(self.c, x, self.y - 30, num, "Inter-Black", 25, -1, BLACK)
                ly = self.y - 44
                for ln in wrap(lab, "Inter-Med", 8.4, col - 12):
                    self.c.setFont("Inter-Med", 8.4); self.c.setFillColor(INK); self.c.drawString(x, ly, ln); ly -= 11
            self.y -= rh; i += 3

    def compare(self, left_title, right_title, rows):
        colw = (CW - 20) / 2.0; xL = LM; xR = LM + colw + 20
        self.ensure(40); self.y -= 8; bt = self.y; bh = 18
        self.c.setFillColor(YELLOW); self.c.setStrokeColor(BLACK); self.c.setLineWidth(0.8)
        self.c.rect(LM, bt - bh, CW, bh, fill=1, stroke=1)
        self.c.setFillColor(BLACK); self.c.setFont("Mono-Bold", 7.5)
        self.c.drawString(xL + 6, bt - 12, left_title.upper()); self.c.drawString(xR, bt - 12, right_title.upper())
        self.y = bt - bh - 6
        for label, was, now in rows:
            wl = wrap(was, "Inter", 9.6, colw - 6); nl = wrap(now, "Inter-Med", 9.6, colw)
            ml = max(len(wl), len(nl)); rh = 13 + ml * 13 + 8
            self.ensure(rh); self.y -= 13
            self.c.setFont("Mono-Bold", 6.6); self.c.setFillColor(BLACK); self.c.drawString(xL, self.y, label.upper())
            yy = self.y - 13
            for k in range(ml):
                if k < len(wl):
                    self.c.setFont("Inter", 9.6); self.c.setFillColor(INK); self.c.drawString(xL, yy, wl[k])
                if k < len(nl):
                    self.c.setFont("Inter-Med", 9.6); self.c.setFillColor(BLACK); self.c.drawString(xR, yy, nl[k])
                yy -= 13
            self.y = yy - 6
            self.c.setStrokeColor(HexColor(0x000000)); self.c.setLineWidth(0.3); self.c.line(LM, self.y + 3, PW - RM, self.y + 3)
        self.y -= 4

    def dotsep(self):
        self.ensure(24); self.y -= 14; x = LM
        for _ in range(3):
            self._ytick(x, self.y, 7, 7); x += 12
        self.y -= 10

    def rule(self, pad=10):
        self.ensure(pad * 2); self.y -= pad
        self.c.setStrokeColor(BLACK); self.c.setLineWidth(0.8); self.c.line(LM, self.y, PW - RM, self.y)
        self.y -= pad

    def save(self): self.c.save()


def build(doc, S):
    doc.cover(S["kicker"], S["cover_lines"], S["cover_sub"])
    for sec in S["sections"]:
        blocks = sec["blocks"]; intro = ""; rest = blocks
        if blocks and blocks[0][0] == "para":
            intro = blocks[0][1]; rest = blocks[1:]
        doc.opener(sec["num"], sec["title"], sec["header"], intro)
        for b in rest:
            k = b[0]
            if k == "para": doc.para(b[1])
            elif k == "h3": doc.h3(b[1])
            elif k == "bullets": doc.bullets(b[1])
            elif k == "numbered": doc.numbered(b[1])
            elif k == "callout": doc.callout(b[1], b[2])
            elif k == "quote": doc.quote(b[1])
            elif k == "bigstat": doc.bigstat(b[1], b[2])
            elif k == "statgrid": doc.statgrid(b[1])
            elif k == "compare": doc.compare(b[1], b[2], b[3])
            elif k == "dotsep": doc.dotsep()
            elif k == "rule": doc.rule()
    doc.save()


import content_en, content_ru
build(Doc("/home/user/Claude/AI-Search-2026-Guide-EN.pdf",
          "THE REACH — AI SEARCH FIELD GUIDE", "SEO · GEO · AEO · 2026", "THE REACH"), content_en.DATA)
build(Doc("/home/user/Claude/AI-Search-2026-Guide-RU.pdf",
          "THE REACH — ГАЙД ПО AI-ПОИСКУ", "SEO · GEO · AEO · 2026", "THE REACH"), content_ru.DATA)
print("done")
