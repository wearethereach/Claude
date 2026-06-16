# -*- coding: utf-8 -*-
"""Claude Cowork guide rebuilt in THE REACH Swiss-minimalist style (matches AI-Search guides)."""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor

FB = "/tmp/fonts/inter_extracted/extras/ttf"
MB = "/tmp/fonts/jbmono/fonts/ttf"
for n, f in [("Inter","Inter-Regular"),("Inter-Med","Inter-Medium"),("Inter-SB","Inter-SemiBold"),
             ("Inter-Bold","Inter-Bold"),("Inter-Black","Inter-Black"),("Disp-Black","InterDisplay-Black")]:
    pdfmetrics.registerFont(TTFont(n, f"{FB}/{f}.ttf"))
for n, f in [("Mono","JetBrainsMono-Regular"),("Mono-Med","JetBrainsMono-Medium"),("Mono-Bold","JetBrainsMono-Bold")]:
    pdfmetrics.registerFont(TTFont(n, f"{MB}/{f}.ttf"))

YELLOW = HexColor(0xFFF55F); WHITE = HexColor(0xFFFFFF)
BLACK = HexColor(0x000000); INK = HexColor(0x0A0A0A); GREEN = HexColor(0x00A85A)
PW, PH = A4; LM, RM = 56, 56; CW = PW - LM - RM; TOP = 760; BOTTOM = 92

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

    def _furniture(self):
        c = self.c
        cover = self.page == 1
        c.setFillColor(YELLOW if cover else WHITE); c.rect(0, 0, PW, PH, fill=1, stroke=0)
        c.setFillColor(BLACK); c.setFont("Mono-Med", 6.4)
        c.drawString(LM, 812, self.gtitle.upper())
        if cover:
            c.setFont("Mono-Med", 6.4); c.drawRightString(PW - RM, 812, self.cover_tr.upper())
        elif self.cur_section:
            sec = self.cur_section.upper(); sw = stringWidth(sec, "Mono-Bold", 6.4)
            self._ychip(PW - RM - sw, 812, sec, "Mono-Bold", 6.4)
            c.setFillColor(BLACK)
        c.setLineWidth(0.8); c.setStrokeColor(BLACK); c.line(LM, 804, PW - RM, 804)
        c.line(LM, 70, PW - RM, 70)
        if not cover:                      # cover draws its own footer
            c.setFont("Mono-Bold", 6.4); c.drawString(LM, 58, self.foot_left.upper())
            c.setFont("Mono-Med", 6.4); c.drawRightString(PW - RM, 58, f"P{self.page:02d}")

    def _newpage(self):
        if self.page > 0: self.c.showPage()
        self.page += 1; self._furniture(); self.y = TOP

    def ensure(self, h):
        if self.y - h < BOTTOM: self._newpage()

    def _ybar(self, x, y, w, h):
        self.c.setFillColor(YELLOW); self.c.setStrokeColor(BLACK); self.c.setLineWidth(0.6)
        self.c.rect(x, y, w, h, fill=1, stroke=1)

    def _ychip(self, x, y, text, font, size, padx=3):
        w = stringWidth(text, font, size)
        self.c.setFillColor(YELLOW); self.c.rect(x - padx, y - 1.6, w + 2*padx, size*0.96 + 1.6, fill=1, stroke=0)
        self.c.setFillColor(BLACK); self.c.setFont(font, size); self.c.drawString(x, y, text)
        return w + 2*padx

    # ---------- blocks ----------
    def cover(self, kicker, lines, subtitle, fl, fr):
        c = self.c
        c.setFillColor(GREEN); c.rect(LM, 690, 64, 12, fill=1, stroke=0)
        c.setFillColor(BLACK); c.setFont("Mono-Bold", 8); c.drawString(LM, 668, kicker.upper())
        y = 560
        for ln in lines:
            trtext(c, LM, y, ln, "Disp-Black", 60, -2.6, BLACK); y -= 60
        c.setFillColor(GREEN); c.rect(LM, y + 30, 220, 10, fill=1, stroke=0)
        c.setFillColor(INK)
        for ln in wrap(subtitle, "Inter-Med", 12.5, CW - 40):
            y -= 18; c.setFont("Inter-Med", 12.5); c.drawString(LM, y, ln)
        # custom cover footer
        c.setFillColor(BLACK); c.setFont("Inter", 8.5)
        yy = 60
        for ln in fl: c.drawString(LM, yy, ln); yy -= 12
        c.setFont("Mono-Med", 7); yy = 60
        for ln in fr: c.drawRightString(PW - RM, yy, ln.upper()); yy -= 12
        self.y = BOTTOM

    def section(self, num, title, header):
        self.cur_section = header; self._newpage(); c = self.c
        self._ychip(LM, self.y, f"SECTION {num}", "Mono-Bold", 8); self.y -= 8
        for ln in wrap(title, "Inter-Black", 27, CW, cs=-0.9):
            self.y -= 31; trtext(c, LM, self.y, ln, "Inter-Black", 27, -0.9, BLACK)
        self.y -= 6; self._ybar(LM, self.y, 46, 5); self.y -= 22

    def subhead(self, text):
        self.ensure(30); self.y -= 16
        self._ybar(LM, self.y + 14, 22, 5)
        for ln in wrap(text, "Inter-Black", 16, CW, cs=-0.4):
            self.y -= 21; trtext(self.c, LM, self.y, ln, "Inter-Black", 16, -0.4, BLACK)
        self.y -= 6

    def para(self, text, size=10.5, lead=15.4):
        self.c.setFillColor(INK)
        for ln in wrap(text, "Inter", size, CW):
            self.ensure(lead); self.y -= lead
            self.c.setFont("Inter", size); self.c.drawString(LM, self.y, ln)
        self.y -= 5

    def toc(self, items):
        for num, title in items:
            self.ensure(30); self.y -= 20
            self._ychip(LM, self.y, num, "Mono-Bold", 9)
            self.c.setFillColor(BLACK); self.c.setFont("Inter-SB", 13)
            self.c.drawString(LM + 50, self.y, title)
            self.y -= 9
            self.c.setStrokeColor(HexColor(0x000000)); self.c.setLineWidth(0.4)
            self.c.line(LM, self.y, PW - RM, self.y)

    def deflist(self, items):
        for label, title, body in items:
            blines = wrap(body, "Inter", 10, CW) if body else []
            self.ensure(18 + len(blines) * 13.6)
            self.y -= 15; tx = LM
            if label:
                w = self._ychip(LM, self.y, label, "Mono-Bold", 8); tx = LM + w + 8
            if title:
                trtext(self.c, tx, self.y, title, "Inter-Bold", 12, -0.2, BLACK)
            self.y -= 3
            for ln in blines:
                self.ensure(13.6); self.y -= 13.6
                self.c.setFillColor(INK); self.c.setFont("Inter", 10); self.c.drawString(LM, self.y, ln)
            self.y -= 8

    def table(self, headers, rows, weights):
        n = len(headers); gut = 10; avail = CW - (n - 1) * gut
        widths = [avail * w for w in weights]
        xs = [LM]
        for k in range(1, n): xs.append(xs[-1] + widths[k - 1] + gut)
        self.ensure(34); self.y -= 16
        for k, h in enumerate(headers):
            self.c.setFont("Inter-Bold", 8.4); self.c.setFillColor(BLACK)
            for hi, hl in enumerate(wrap(h, "Inter-Bold", 8.4, widths[k])):
                self.c.drawString(xs[k], self.y - hi * 10, hl)
        self.y -= 7
        self.c.setStrokeColor(BLACK); self.c.setLineWidth(0.8); self.c.line(LM, self.y, PW - RM, self.y); self.y -= 4
        for row in rows:
            cells = [wrap(c, "Inter-SB" if k == 0 else "Inter", 9.3, widths[k]) for k, c in enumerate(row)]
            ml = max(len(c) for c in cells); rh = ml * 12 + 10
            self.ensure(rh); self.y -= 12; yy0 = self.y
            for k, cell in enumerate(cells):
                self.c.setFont("Inter-SB" if k == 0 else "Inter", 9.3)
                self.c.setFillColor(BLACK if k == 0 else INK)
                for ci, cl in enumerate(cell):
                    self.c.drawString(xs[k], yy0 - ci * 12, cl)
            self.y = yy0 - (ml - 1) * 12 - 8
            self.c.setStrokeColor(HexColor(0x000000)); self.c.setLineWidth(0.3); self.c.line(LM, self.y + 3, PW - RM, self.y + 3)
        self.y -= 4

    def prompt(self, text, label="PROMPT"):
        lines = []
        for part in text.split("\n"):
            lines += wrap(part, "Mono", 9, CW - 36)
        box_h = 30 + len(lines) * 13
        self.ensure(box_h + 10); self.y -= 8; top = self.y
        self.c.setFillColor(WHITE); self.c.setStrokeColor(BLACK); self.c.setLineWidth(1)
        self.c.rect(LM, top - box_h, CW, box_h, fill=1, stroke=1)
        self._ychip(LM + 14, top - 16, label.upper(), "Mono-Bold", 7)
        yy = top - 16 - 16
        for ln in lines:
            self.c.setFillColor(BLACK); self.c.setFont("Mono", 9); self.c.drawString(LM + 16, yy, ln); yy -= 13
        self.y = top - box_h - 10

    def callout(self, label, text):
        lines = wrap(text, "Inter-SB", 12, CW - 36)
        box_h = 18 + len(lines) * 16 + 14
        self.ensure(box_h + 10); self.y -= 8; top = self.y
        self.c.setFillColor(BLACK); self.c.rect(LM, top - box_h, CW, box_h, fill=1, stroke=0)
        self.c.setFillColor(YELLOW); self.c.rect(LM, top - box_h, 6, box_h, fill=1, stroke=0)
        yy = top - 18
        self.c.setFillColor(YELLOW); self.c.setFont("Mono-Bold", 7.5); self.c.drawString(LM + 20, yy, label.upper()); yy -= 14
        for ln in lines:
            self.c.setFillColor(YELLOW); self.c.setFont("Inter-SB", 12); self.c.drawString(LM + 20, yy, ln); yy -= 16
        self.y = top - box_h - 10

    def checklist(self, items):
        for it in items:
            lines = wrap(it, "Inter", 10.5, CW - 24)
            self.ensure(len(lines) * 14.5 + 6); self.y -= 14.5
            self.c.setStrokeColor(BLACK); self.c.setFillColor(WHITE); self.c.setLineWidth(0.9)
            self.c.rect(LM, self.y - 0.5, 9, 9, fill=1, stroke=1)
            self.c.setFillColor(INK); self.c.setFont("Inter", 10.5)
            for i, ln in enumerate(lines):
                if i: self.y -= 14.5
                self.c.drawString(LM + 20, self.y, ln)
            self.y -= 5

    def closing(self, lines, links, attrib, header):
        self.cur_section = header; self._newpage(); c = self.c
        y = 600
        for ln in lines:
            trtext(c, LM, y, ln, "Disp-Black", 46, -2, BLACK); y -= 50
        c.setFillColor(GREEN); c.rect(LM, y + 22, 180, 9, fill=1, stroke=0)
        y -= 30; c.setFillColor(INK); c.setFont("Inter-Med", 12)
        for ln in attrib:
            y -= 17; c.drawString(LM, y, ln)
        y -= 30
        for lk in links:
            self._ychip(LM, y, lk, "Mono-Bold", 9); y -= 22
        self.y = BOTTOM

    def save(self): self.c.save()


import content_cowork as M
d = Doc("/home/user/Claude/Claude-Cowork-Guide-EN.pdf",
        "CLAUDE COWORK", "OPUS 4.6 · PLUGINS · CONNECTORS · SKILLS", "PRACTICAL GUIDE")
S = M.DATA
d.cover(S["kicker"], S["cover_lines"], S["cover_sub"], S["foot_l"], S["foot_r"])
# contents
d.section("", "What's inside", "CONTENTS") if False else None
d.cur_section = "CONTENTS"; d._newpage()
d._ychip(LM, d.y, "CONTENTS", "Mono-Bold", 8); d.y -= 8
for ln in wrap("What's inside", "Inter-Black", 27, CW, cs=-0.9):
    d.y -= 31; trtext(d.c, LM, d.y, ln, "Inter-Black", 27, -0.9, BLACK)
d.y -= 6; d._ybar(LM, d.y, 46, 5); d.y -= 18
d.toc(S["toc"])
# sections
for sec in S["sections"]:
    d.section(sec["num"], sec["title"], sec["header"])
    for b in sec["blocks"]:
        k = b[0]
        if k == "para": d.para(b[1])
        elif k == "subhead": d.subhead(b[1])
        elif k == "deflist": d.deflist(b[1])
        elif k == "table": d.table(b[1], b[2], b[3])
        elif k == "prompt": d.prompt(b[1], b[2] if len(b) > 2 else "PROMPT")
        elif k == "callout": d.callout(b[1], b[2])
        elif k == "checklist": d.checklist(b[1])
        elif k == "label":
            d.ensure(20); d.y -= 14; d._ychip(LM, d.y, b[1], "Mono-Bold", 7.5); d.y -= 8
d.closing(S["closing"], S["links"], S["close_attrib"], "END OF GUIDE")
d.save()
print("done")
