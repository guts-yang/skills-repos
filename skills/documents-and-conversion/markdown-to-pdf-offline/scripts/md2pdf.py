# -*- coding: utf-8 -*-
"""
md2pdf.py — 无 pandoc / Chrome 环境下把 Markdown 或 CSV 转成排版良好的 PDF。
依赖: pip install markdown reportlab (pypdf/pymupdf 仅校验用, 可选)
用法:
  python md2pdf.py input.md output.pdf [--title "标题"] [--subtitle "副题"] [--landscape]
  python md2pdf.py input.csv output.pdf [--landscape] [--col-ratio "0.05,0.1,..."]
按扩展名自动路由: .md -> markdown 渲染; .csv -> 表格(横向更佳, 表头每页重复)。
"""
import csv, os, re, sys, argparse
from html.parser import HTMLParser
from xml.sax.saxutils import escape
import markdown
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable)

BLUE = colors.HexColor('#0C447C'); GREEN = colors.HexColor('#0F6E56')
AMB = colors.HexColor('#854F0B'); AMBBG = colors.HexColor('#FAEEDA')
GRID = colors.HexColor('#b9c6d2'); ZEBRA = colors.HexColor('#f4f8fb')

def register_cjk():
    # 注意: Hiragino/STHeiti 的 .ttc 是 postscript outlines, reportlab 不支持;
    # PingFang.ttc 同理。优先找普通 .ttf 的 CJK 字体。
    candidates = [
        ("/Library/Fonts/Arial Unicode.ttf", None),
        ("/System/Library/Fonts/Supplemental/Songti.ttc", 0),
        ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),
    ]
    for path, idx in candidates:
        if not os.path.exists(path):
            continue
        try:
            if idx is None:
                pdfmetrics.registerFont(TTFont("CN", path))
            else:
                pdfmetrics.registerFont(TTFont("CN", path, subfontIndex=idx))
            if pdfmetrics.stringWidth("测试中文", "CN", 10) > 0:
                return "CN"
        except Exception:
            continue
    raise SystemExit("no usable CJK font")

F = register_cjk()

def P(name, **kw):
    d = dict(fontName=F, fontSize=9, leading=13.2, spaceAfter=4, textColor=colors.HexColor('#1a1a1a'))
    d.update(kw); return ParagraphStyle(name, **d)

S = {
 'h1': P('h1', fontSize=17, leading=22, alignment=TA_CENTER, textColor=BLUE, spaceAfter=3, spaceBefore=0),
 'h2': P('h2', fontSize=12.5, leading=17, textColor=GREEN, spaceBefore=13, spaceAfter=5),
 'h3': P('h3', fontSize=10.5, leading=15, textColor=BLUE, spaceBefore=9, spaceAfter=3),
 'h4': P('h4', fontSize=9.5, leading=14, spaceBefore=7, spaceAfter=2),
 'p': P('p'),
 'li': P('li', fontSize=8.8, leading=12.5, leftIndent=10, spaceAfter=1.5),
 'q': P('q', fontSize=8.6, leading=12.5, textColor=AMB, leftIndent=4, rightIndent=4,
        backColor=AMBBG, borderPadding=5, spaceBefore=4, spaceAfter=6),
 'cell': P('cell', fontSize=7.0, leading=9.2, spaceAfter=0),
 'cellh': P('cellh', fontSize=7.0, leading=9.2, spaceAfter=0, textColor=colors.white),
 'sub': P('sub', fontSize=8, leading=12, alignment=TA_CENTER, textColor=colors.HexColor('#666')),
}
INL_S = {'strong': '<b>', 'b': '<b>', 'em': '<i>', 'i': '<i>',
         'code': '<font face="Courier" size="7">', 'br': '<br/>'}
INL_E = {'strong': '</b>', 'b': '</b>', 'em': '</i>', 'i': '</i>', 'code': '</font>'}

def wlen(s):
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in s)

class Conv(HTMLParser):
    """markdown 库产出的 HTML -> reportlab flowables。表格列宽按内容自适应。"""
    def __init__(self, width):
        super().__init__(convert_charrefs=True)
        self.width = width; self.flows = []
        self.cur = None; self.buf = []
        self.ltype = None; self.litems = []
        self.tbl = None; self.tbl_txt = None
        self.row = None; self.row_txt = None
        self.cell = None; self.ctag = None

    def handle_starttag(self, tag, attrs):
        if tag in ('td', 'th'):
            self.cell = []; self.ctag = tag; return
        if self.cell is not None:
            if tag in INL_S: self.cell.append(INL_S[tag])
            return
        if tag in ('h1', 'h2', 'h3', 'h4', 'p', 'blockquote'):
            if self.cur is None:
                self.cur = tag; self.buf = []
            return
        if tag == 'li':
            if self.litems is None: self.litems = []
            self.cur = 'li'; self.buf = []; return
        if tag in ('ul', 'ol'):
            self.ltype = tag; self.litems = []; return
        if tag == 'table':
            self.tbl = []; self.tbl_txt = []; return
        if tag == 'tr':
            self.row = []; self.row_txt = []; return
        if tag in INL_S: self.buf.append(INL_S[tag])
        if tag == 'hr':
            self.flows.append(HRFlowable(width="100%", thickness=0.4,
                                         color=colors.HexColor('#d0d0d0'),
                                         spaceBefore=6, spaceAfter=6))

    def handle_endtag(self, tag):
        if tag in ('td', 'th'):
            if self.cell is not None:
                txt = "".join(self.cell).strip()
                self.row.append(Paragraph(txt, S['cellh'] if self.ctag == 'th' else S['cell']))
                if self.row_txt is None: self.row_txt = []
                self.row_txt.append(re.sub(r'<[^>]+>', '', txt))
            self.cell = None; return
        if tag in INL_E and self.cell is not None:
            self.cell.append(INL_E[tag]); return
        if tag in INL_E:
            self.buf.append(INL_E[tag]); return
        if tag == 'tr':
            if self.tbl is not None and self.row:
                self.tbl.append(self.row)
                self.tbl_txt.append(self.row_txt or [])
            self.row = None; self.row_txt = None; return
        if tag == 'table':
            self._emit_table(); self.tbl = None; self.tbl_txt = None; return
        if tag == 'li':
            if self.buf: self.litems.append("".join(self.buf).strip())
            self.cur = None; self.buf = []; return
        if tag in ('ul', 'ol'):
            for i, it in enumerate(self.litems or []):
                mark = f"{i+1}. " if self.ltype == 'ol' else "• "
                self.flows.append(Paragraph(mark + it, S['li']))
            if self.litems: self.flows.append(Spacer(1, 3))
            self.ltype = None; self.litems = []; return
        if tag in ('h1', 'h2', 'h3', 'h4', 'p', 'blockquote'):
            if self.cur == tag:
                txt = "".join(self.buf).strip()
                if txt:
                    key = {'h1': 'h1', 'h2': 'h2', 'h3': 'h3', 'h4': 'h4',
                           'blockquote': 'q'}.get(tag, 'p')
                    self.flows.append(Paragraph(txt, S[key]))
                    if tag == 'h2':
                        self.flows.append(HRFlowable(width="100%", thickness=0.8,
                                                     color=GREEN, spaceBefore=0, spaceAfter=4))
                self.cur = None; self.buf = []
            elif tag == 'p' and self.cur == 'blockquote':
                self.buf.append('<br/>')
            return

    def handle_data(self, data):
        t = escape(data)
        if self.cell is not None: self.cell.append(t)
        elif self.cur is not None: self.buf.append(t)

    def _emit_table(self):
        rows = self.tbl; txts = self.tbl_txt or []
        if not rows: return
        ncol = max(len(r) for r in rows)
        rows = [r + [Paragraph('', S['cell'])] * (ncol - len(r)) for r in rows]
        ws = []
        for i in range(ncol):
            vals = [wlen(r[i]) for r in txts if i < len(r)]
            ws.append(min(max(max(vals) if vals else 4, 7), 42))
        tot = float(sum(ws))
        cw = [self.width * w / tot for w in ws]
        MINW = min(26.0, self.width * 0.05)
        cw = [max(c, MINW) for c in cw]
        s2 = sum(cw)
        if s2 > self.width:
            cw = [c * self.width / s2 for c in cw]
        t = Table(rows, colWidths=cw, repeatRows=1, hAlign='LEFT')
        st = [('GRID', (0, 0), (-1, -1), 0.35, GRID),
              ('BACKGROUND', (0, 0), (-1, 0), BLUE),
              ('VALIGN', (0, 0), (-1, -1), 'TOP'),
              ('LEFTPADDING', (0, 0), (-1, -1), 3),
              ('RIGHTPADDING', (0, 0), (-1, -1), 3),
              ('TOPPADDING', (0, 0), (-1, -1), 2.5),
              ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5)]
        for i in range(1, len(rows)):
            if i % 2 == 0: st.append(('BACKGROUND', (0, i), (-1, i), ZEBRA))
        t.setStyle(TableStyle(st))
        self.flows.append(Spacer(1, 3)); self.flows.append(t); self.flows.append(Spacer(1, 7))

def clean(t):
    # Arial Unicode 无这些 emoji 字形, 替换为文本标记防黑块
    return (t.replace('⚠️', '[!]').replace('⚠', '[!]')
             .replace('✅', '[OK]').replace('❌', '[X]')
             .replace('🔒', '').replace('📌', ''))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(F, 7.5); canvas.setFillColor(colors.HexColor('#888'))
    canvas.drawCentredString(doc.pagesize[0] / 2.0, 9 * mm, f"— {doc.page} —")
    canvas.restoreState()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--title", default=None)
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--landscape", action="store_true")
    ap.add_argument("--col-ratio", default=None, help="CSV 列宽比例, 逗号分隔, 如 0.05,0.1,...")
    a = ap.parse_args()
    pagesize = landscape(A4) if a.landscape else A4
    W = pagesize[0] - 32 * mm
    ext = os.path.splitext(a.src)[1].lower()
    flows = []
    if ext == ".md":
        md = clean(open(a.src, encoding="utf-8").read())
        html_body = markdown.markdown(md, extensions=["tables", "fenced_code", "attr_list", "sane_lists"])
        c = Conv(W); c.feed(html_body)
        flows = c.flows
        if a.subtitle:
            flows.insert(0, Paragraph(clean(a.subtitle), S['sub']))
    else:
        rows = list(csv.reader(open(a.src, encoding="utf-8-sig")))
        head, data = rows[0], rows[1:]
        if a.col_ratio:
            cw = [W * float(x) for x in a.col_ratio.split(",")]
        else:
            def colmax(i):
                vals = [wlen(r[i]) for r in data if i < len(r)] or [4]
                return min(max(max(vals), 7), 60)
            ws = [colmax(i) for i in range(len(head))]
            tot = float(sum(ws)); cw = [W * w / tot for w in ws]
        tbl = [[Paragraph(clean(h), S['cellh']) for h in head]]
        for r in data:
            tbl.append([Paragraph(clean(x), S['cell']) for x in r])
        t = Table(tbl, colWidths=cw, repeatRows=1, hAlign='LEFT')
        st = [('GRID', (0, 0), (-1, -1), 0.3, GRID),
              ('BACKGROUND', (0, 0), (-1, 0), BLUE),
              ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
              ('LEFTPADDING', (0, 0), (-1, -1), 2.5),
              ('RIGHTPADDING', (0, 0), (-1, -1), 2.5),
              ('TOPPADDING', (0, 0), (-1, -1), 2.2),
              ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2)]
        for i in range(1, len(tbl)):
            if i % 2 == 0: st.append(('BACKGROUND', (0, i), (-1, i), ZEBRA))
        t.setStyle(TableStyle(st))
        title = a.title or os.path.basename(a.src)
        flows = [Paragraph(clean(title), S['h1'])]
        if a.subtitle: flows.append(Paragraph(clean(a.subtitle), S['sub']))
        flows += [Spacer(1, 6), t]
    doc = SimpleDocTemplate(a.dst, pagesize=pagesize,
                            leftMargin=16 * mm, rightMargin=16 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm)
    doc.build(flows, onFirstPage=footer, onLaterPages=footer)
    print("OK:", a.dst, os.path.getsize(a.dst), "bytes")

if __name__ == "__main__":
    main()
