"""Generate the Beamer version of the talk from deck_spec.py (same coordinates as the PPTX)."""
import os, re, shutil, sys
from deck_spec import *

OUT = sys.argv[1] if len(sys.argv) > 1 else "beamer"
os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
os.makedirs(os.path.join(OUT, "fonts"), exist_ok=True)
for f in ["Merriweather-Regular.ttf", "Merriweather-Bold.ttf", "OpenSans-Regular.ttf", "OpenSans-Bold.ttf", "OpenSans-Italic.ttf", "OpenSans-SemiBold.ttf"]:
    shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "beamer", "fonts", f) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "beamer", "fonts", f)) else os.path.expanduser("~/.fonts/" + f), os.path.join(OUT, "fonts", f))

THEME = r"""% beamerthemeISU.sty -- ISU / Translational AI Center slide style (BioShield template)
% Merriweather Bold titles in ISU cardinal, 1.5pt blue rule, Open Sans body. Compile with XeLaTeX.
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{beamerthemeISU}[2026/10/26 ISU TrAC Beamer theme]
\RequirePackage{fontspec}
\RequirePackage{xcolor}
\RequirePackage{tikz}
\RequirePackage{tabularx,array,colortbl}
\RequirePackage{amsmath}
\definecolor{isuRed}{HTML}{C8102E}
\definecolor{isuAccent}{HTML}{CE1126}
\definecolor{isuBody}{HTML}{6E6259}
\definecolor{isuRule}{HTML}{0060C0}
\definecolor{isuNavy}{HTML}{1B3A5C}
\definecolor{isuMidBlue}{HTML}{3D6C9E}
\definecolor{isuTeal}{HTML}{3891A7}
\definecolor{isuCoolGray}{HTML}{8C97A6}
\definecolor{isuTintBlue}{HTML}{DCE6F1}
\definecolor{isuTintIce}{HTML}{E8F4F8}
\definecolor{isuTintGreen}{HTML}{D4EDDA}
\definecolor{isuTintGray}{HTML}{F2F2F2}
\definecolor{isuPanel}{HTML}{F2F5F9}
\definecolor{isuCode}{HTML}{F4F6F8}
\definecolor{isuInk}{HTML}{222222}
\setmainfont{OpenSans}[Path=./fonts/, Extension=.ttf, UprightFont=*-Regular, BoldFont=*-Bold, ItalicFont=*-Italic]
\setsansfont{OpenSans}[Path=./fonts/, Extension=.ttf, UprightFont=*-Regular, BoldFont=*-Bold, ItalicFont=*-Italic]
\newfontfamily\headfont{Merriweather}[Path=./fonts/, Extension=.ttf, UprightFont=*-Bold, BoldFont=*-Bold]
\setmonofont{DejaVu Sans Mono}[Scale=0.92]
\usefonttheme{professionalfonts}
\setbeamertemplate{navigation symbols}{}
\setbeamercolor{normal text}{fg=isuBody,bg=white}
\setbeamercolor{frametitle}{fg=isuRed}
\setbeamerfont{frametitle}{size=\fontsize{21}{24}\selectfont}
\setbeamertemplate{frametitle}{}
\setbeamertemplate{itemize item}{\textcolor{isuAccent}{\textbullet}}
\setbeamertemplate{footline}{%
  \begin{tikzpicture}[remember picture,overlay]
    \node[anchor=south west,inner sep=0,text=isuCoolGray,font=\fontsize{8}{9}\selectfont] at ([xshift=0.69in,yshift=0.12in]current page.south west) {FAIR Data Curation \,·\, ISU TrAC};
    \node[anchor=south east,inner sep=0,text=isuCoolGray,font=\fontsize{8}{9}\selectfont] at ([xshift=-0.69in,yshift=0.12in]current page.south east) {\insertframenumber};
  \end{tikzpicture}}
% \isutitle{text}: title + blue rule at the template positions (absolute, in inches)
\newcommand{\isutitle}[2][21]{%
  \begin{tikzpicture}[remember picture,overlay]
    \node[anchor=south west,inner sep=0,text width=8.62in,font=\headfont\fontsize{#1}{#1}\selectfont,text=isuRed,align=left] at ([xshift=0.69in,yshift=-1.0in]current page.north west) {#2};
    \draw[isuRule,line width=1.5pt] ([xshift=0.69in,yshift=-1.125in]current page.north west) -- ([xshift=9.31in,yshift=-1.125in]current page.north west);
  \end{tikzpicture}}
% place content at absolute inch coordinates measured from the top-left corner
\newcommand{\at}[3]{\begin{tikzpicture}[remember picture,overlay]\node[anchor=north west,inner sep=0] at ([xshift=#1in,yshift=-#2in]current page.north west) {#3};\end{tikzpicture}}
\newcommand{\panel}[6]{% x y w h fill content
  \begin{tikzpicture}[remember picture,overlay]
    \fill[#5] ([xshift=#1in,yshift=-#2in]current page.north west) rectangle ++(#3in,-#4in);
    \node[anchor=north west,inner sep=0,text width=#3in-0.24in] at ([xshift=#1in+0.12in,yshift=-#2in-0.1in]current page.north west) {#6};
  \end{tikzpicture}}
\newcommand{\statement}[5]{% x y w h text
  \begin{tikzpicture}[remember picture,overlay]
    \fill[isuPanel] ([xshift=#1in,yshift=-#2in]current page.north west) rectangle ++(#3in,-#4in);
    \fill[isuRed] ([xshift=#1in,yshift=-#2in]current page.north west) rectangle ++(0.07in,-#4in);
    \node[anchor=west,inner sep=0,text width=#3in-0.3in,text=isuInk] at ([xshift=#1in+0.2in,yshift=-#2in-#4in/2]current page.north west) {#5};
  \end{tikzpicture}}
"""
open(os.path.join(OUT, "beamerthemeISU.sty"), "w").write(THEME)

SP = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def esc(s):
    s = "".join(SP.get(c, c) for c in s)
    s = s.replace("<-", r"$\leftarrow$").replace("→", r"$\rightarrow$").replace("≈", r"$\approx$").replace("Σ", r"$\Sigma$").replace("×", r"$\times$")
    return re.sub(r"\*\*(.+?)\*\*", r"{\\color{isuInk}\\bfseries \1}", s)


def fs(size):
    return r"\fontsize{%g}{%g}\selectfont{}" % (size, size * 1.3)


def img_rel(p):
    n = os.path.basename(p); shutil.copy(p, os.path.join(OUT, "img", n)); return "img/" + n


def text_block(b, math=None):
    out, inlist = [], False
    for para in b["paras"]:
        if math and para.startswith("FAIR% ="):
            para = None; out.append(r"\par\vspace{2pt}{\color{isuInk}$%s$}\par\vspace{2pt}" % math["avg"]); continue
        if math and para.startswith("P(reuse)"):
            out.append(r"\par\vspace{2pt}{\color{isuInk}$%s$}\par\vspace{2pt}" % math["prod"]); continue
        if para.startswith("• "):
            if not inlist: out.append(r"\begin{itemize}\setlength{\itemsep}{%gpt}\setlength{\leftmargini}{1.1em}" % (b["size"] * 0.3)); inlist = True
            out.append(r"\item " + esc(para[2:]))
            continue
        if inlist: out.append(r"\end{itemize}"); inlist = False
        if para.startswith("## "):
            out.append(r"\par\vspace{%gpt}{\color{isuNavy}\bfseries %s}\par\vspace{1pt}" % (b["size"] * 0.5, esc(para[3:])))
        else:
            out.append(esc(para) + r"\par\vspace{%gpt}" % (b["size"] * 0.3))
    if inlist: out.append(r"\end{itemize}")
    body = "\n".join(out)
    return r"\at{%g}{%g}{\begin{minipage}[t]{%gin}\raggedright%s\color{isuBody}%s\end{minipage}}" % (b["x"], b["y"], b["w"], fs(b["size"]), body)


def table_block(b):
    rows, cols = b["rows"], b["cols"]
    header = len(rows) > 1 and not rows[0][0].startswith(("Aug", "flight"))
    spec = "".join(r">{\raggedright\arraybackslash}p{%gin}" % (c - 0.12) for c in cols)
    lines = []
    for i, r in enumerate(rows):
        if header and i == 0:
            lines.append(r"\rowcolor{isuNavy}" + " & ".join(r"\textcolor{white}{\bfseries %s}" % esc(v) for v in r) + r"\\")
        else:
            col = "white" if i % 2 else "isuCode"
            cells = [r"\textcolor{isuNavy}{%s}" % esc(r[0])] + [esc(v) for v in r[1:]]
            lines.append(r"\rowcolor{%s}" % col + " & ".join(cells) + r"\\")
    t = (r"{%s\renewcommand{\arraystretch}{1.3}\setlength{\tabcolsep}{0.06in}\arrayrulecolor{isuTintBlue}\begin{tabular}{%s}" % (fs(b["size"]), spec)
         + "\n".join(lines) + r"\end{tabular}}")
    return r"\at{%g}{%g}{%s}" % (b["x"], b["y"], t)


def code_block(b):
    ls = []
    for line in b["text"].split("\n"):
        e = "".join(SP.get(c, c) for c in line).replace("<-", r"$\leftarrow$").replace(" ", r"\hphantom{0}")
        if line.lstrip().startswith("#"): e = r"{\color{isuCoolGray}%s}" % e
        ls.append(e if e else r"\ ")
    inner = r"{\ttfamily%s\color{isuInk}%s}" % (fs(b["size"]), r"\\".join(ls))
    return r"\panel{%g}{%g}{%g}{%g}{isuCode}{%s}" % (b["x"], b["y"], b["w"], b["h"], inner)


def box_block(b):
    fill = {TINT_B: "isuTintBlue", TINT_I: "isuTintIce", TINT_G: "isuTintGreen", "F2F2F2": "isuTintGray", "F2F5F9": "isuPanel"}[b["fill"]]
    hc = "isuRed" if b["headcolor"] == RED else "isuNavy"
    body = r"\par ".join(esc(x) if x else r"\vspace{2pt}" for x in b["body"].split("\n"))
    inner = r"\raggedright{%s\color{%s}\bfseries %s}\par\vspace{3pt}{%s\color{isuBody}%s}" % (fs(b["size"] + 1.5), hc, esc(b["head"]), fs(b["size"]), body)
    return r"\panel{%g}{%g}{%g}{%g}{%s}{%s}" % (b["x"], b["y"], b["w"], b["h"], fill, inner)


def block(b, math=None):
    k = b["k"]
    if k == "text": return text_block(b, math)
    if k == "img":
        fr = r"\imgframe{\includegraphics[width=%gin,height=%gin]{%s}}" if b["border"] else r"\includegraphics[width=%gin,height=%gin]{%s}"
        return r"\at{%g}{%g}{%s}" % (b["x"], b["y"], fr % (b["w"], b["h"], img_rel(b["path"])))
    if k == "code": return code_block(b)
    if k == "table": return table_block(b)
    if k == "stmt": return r"\statement{%g}{%g}{%g}{%g}{%s%s}" % (b["x"], b["y"], b["w"], b["h"], fs(b["size"]), esc(b["text"]))
    if k == "box": return box_block(b)
    if k == "src": return r"\at{0.69}{5.08}{%s\color{isuCoolGray}Source: %s}" % (fs(8), esc(b["text"]))


doc = [r"""% FAIR Data Curation for Our Lab -- Beamer version (generated from deck_spec.py)
% Build: latexmk -xelatex talk.tex     Notes PDF: uncomment the pgfpages line below.
\documentclass[aspectratio=169]{beamer}
\geometry{paperwidth=10in,paperheight=5.625in}
\usetheme{ISU}
% \usepackage{pgfpages}\setbeameroption{show notes on second screen=right}
\setlength{\fboxsep}{0pt}\setlength{\fboxrule}{0.5pt}
\newcommand{\imgframe}[1]{{\color{isuCoolGray!70}\fboxsep0pt\fboxrule0.5pt\fbox{#1}}}
\begin{document}"""]

for n, s in enumerate(SLIDES, 1):
    notes = r"\note{%s}" % esc(s["notes"])
    if s.get("kind") == "title":
        tiles = []
        for i, (L_, word, sub) in enumerate(s["tiles"]):
            fill = ["isuTintBlue", "isuTintIce", "isuTintGreen", "isuTintGray"][i]
            x = 0.69 + i * 2.2
            tiles.append(r"\panel{%g}{3.05}{2.02}{1.45}{%s}{{\headfont\fontsize{38}{40}\selectfont\color{isuRed}%s}\par\vspace{2pt}{\fontsize{13}{15}\selectfont\color{isuNavy}\bfseries %s}\par{\fontsize{10.5}{13}\selectfont %s}}" % (x, fill, L_, esc(word), esc(sub)))
        body = "\n".join([
            r"\begin{tikzpicture}[remember picture,overlay]\fill[isuRed] (current page.north west) rectangle ++(10in,-0.12in);\end{tikzpicture}",
            r"\at{0.69}{0.8}{{\fontsize{10.5}{12}\selectfont\color{isuRule}\bfseries %s}}" % esc(s["eyebrow"]),
            r"\begin{tikzpicture}[remember picture,overlay]\node[anchor=south west,inner sep=0,text width=8.62in,font=\headfont\fontsize{32}{36}\selectfont,text=isuRed] at ([xshift=0.69in,yshift=-1.9in]current page.north west) {%s};\draw[isuRule,line width=1.5pt] ([xshift=0.69in,yshift=-2.02in]current page.north west) -- ([xshift=9.31in,yshift=-2.02in]current page.north west);\end{tikzpicture}" % esc(s["title"]),
            r"\at{0.69}{2.15}{\begin{minipage}{8.62in}\fontsize{17}{21}\selectfont %s\end{minipage}}" % esc(s["subtitle"]),
            *tiles,
            r"\at{0.69}{4.85}{\begin{minipage}{8.62in}\fontsize{11}{13}\selectfont %s\end{minipage}}" % esc(s["byline"])])
        doc.append(r"{\setbeamertemplate{footline}{}\begin{frame}[plain]" + "\n" + body + "\n" + notes + r"\end{frame}}")
        continue
    tsize = 21 if len(s["title"]) < 52 else 18.5
    body = "\n".join(block(b, s.get("math")) for b in s["blocks"])
    doc.append(r"\begin{frame}" + "\n" + r"\isutitle[%g]{%s}" % (tsize, esc(s["title"])) + "\n" + body + "\n" + notes + r"\end{frame}")

doc.append(r"\end{document}")
src = "\n\n".join(doc)
open(os.path.join(OUT, "talk.tex"), "w").write(src)
NOTEOPT = r"\setbeameroption{show only notes}\setbeamertemplate{note page}{\vspace*{0.45in}\hspace*{0.6in}\begin{minipage}{8.8in}\fontsize{16}{23}\selectfont\color{isuInk}{\color{isuRed}\bfseries Slide \insertframenumber}\par\medskip\insertnote\end{minipage}}"
open(os.path.join(OUT, "talk-notes.tex"), "w").write(src.replace("% \\usepackage{pgfpages}\\setbeameroption{show notes on second screen=right}", NOTEOPT))
print("wrote", OUT)
