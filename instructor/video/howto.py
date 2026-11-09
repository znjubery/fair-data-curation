"""How to use the FAIR data curation apps — voice-over tutorial (Manim CE 0.19+).
Render one scene:  manim -qh --fps 30 howto.py S03
Each scene lasts exactly as long as its narration (durations.json)."""
from manim import *
import json, os

config.background_color = "#FFFFFF"
config.pixel_width, config.pixel_height = 1920, 1080
HERE = os.path.dirname(os.path.abspath(__file__))
DUR = json.load(open(os.path.join(HERE, "durations.json")))
BOX = json.load(open(os.path.join(HERE, "boxes.json")))

RED, BLUE, NAVY, GRAY, DARK = "#C8102E", "#0060C0", "#1B3A5C", "#6E6259", "#222222"
T1, T2, T3, T4, PINK, GREEN = "#DCE6F1", "#E8F4F8", "#D4EDDA", "#F2F2F2", "#FBEFF1", "#2e8540"
HEAD, BODY, MONO = "Merriweather", "Open Sans", "DejaVu Sans Mono"
STEPS = ["1  Scan", "2  Describe", "3  Organize", "4  Check + deposit"]

IMG_W = 12.2
IMG_C = np.array([0, -0.55, 0])


def txt(s, size=28, color=DARK, font=BODY, weight=NORMAL):
    return Text(s, font=font, font_size=size, color=color, weight=weight)


class Base(Scene):
    key = "s1"
    step = None
    title = ""

    def setup(self):
        self.t0 = 0.0

    # ---------- timing ----------
    @property
    def total(self):
        return DUR[self.key] + 0.6

    def until(self, frac):
        """wait until a fraction of the narration has passed"""
        target = frac * self.total
        now = self.renderer.time
        if target > now + 1 / 30:
            self.wait(target - now)

    def finish(self):
        now = self.renderer.time
        if self.total > now + 1 / 30:
            self.wait(self.total - now)

    # ---------- chrome ----------
    def header(self):
        bar = Rectangle(width=config.frame_width, height=0.08, fill_color=RED, fill_opacity=1, stroke_width=0).to_edge(UP, buff=0)
        band = Rectangle(width=config.frame_width, height=1.35, fill_color=WHITE, fill_opacity=1, stroke_width=0).to_edge(UP, buff=0)
        title = txt(self.title, 36, RED, HEAD, BOLD)
        if title.width > 5.8:
            title.scale_to_fit_width(5.8)
        title.to_corner(UL, buff=0.45).shift(DOWN * 0.1)
        rule = Line(LEFT * 6.65, RIGHT * 6.65, color=BLUE, stroke_width=3).move_to([0, 2.72, 0])
        chips = VGroup()
        for i, s in enumerate(STEPS):
            on = self.step is not None and i == self.step
            done = self.step is not None and i < self.step
            lab = txt(("✓ " if done else "") + s, 16, WHITE if on else (GREEN if done else GRAY), BODY, BOLD if on else NORMAL)
            box = RoundedRectangle(corner_radius=0.12, width=lab.width + 0.3, height=0.38, fill_color=NAVY if on else WHITE,
                                   fill_opacity=1, stroke_color=NAVY if on else "#c9ced6", stroke_width=1.5)
            chips.add(VGroup(box, lab.move_to(box)))
        chips.arrange(RIGHT, buff=0.08).to_corner(UR, buff=0.45).shift(DOWN * 0.1)
        g = VGroup(band, bar, title, rule, chips)
        g.set_z_index(10)
        return g

    def caption(self, s):
        band = Rectangle(width=config.frame_width, height=0.78, fill_color=WHITE, fill_opacity=0.96, stroke_width=0).to_edge(DOWN, buff=0)
        t = txt(s, 26, NAVY, BODY, BOLD).move_to(band)
        if t.width > 13.4:
            t.scale_to_fit_width(13.4)
        band.set_z_index(10); t.set_z_index(11)
        return VGroup(band, t)

    def set_caption(self, s, old=None):
        new = self.caption(s)
        if old is None:
            self.add(new[0])
            self.play(FadeIn(new[1], shift=UP * 0.1), run_time=0.4)
        else:
            self.remove(old[0]); self.add(new[0])
            self.play(FadeOut(old[1]), FadeIn(new[1]), run_time=0.4)
        return new

    # ---------- screenshots ----------
    def shot(self, name):
        img = ImageMobject(os.path.join(HERE, "shots", name + ".jpg"))
        img.width = IMG_W
        img.move_to(IMG_C)
        frame = SurroundingRectangle(img, buff=0, color="#c9ced6", stroke_width=2)
        return Group(img, frame)

    def px(self, grp, x, y):
        img = grp[0]
        W, H = img.width, img.height
        tl = img.get_corner(UL)
        return np.array([tl[0] + x * W / 1920, tl[1] - y * H / 1080, 0])

    def hl(self, grp, name, i, pad=8, color=RED):
        b = BOX[name][i]
        x, y, w, h = b[0] - pad, b[1] - pad, b[2] + 2 * pad, b[3] + 2 * pad
        y2 = min(y + h, 1078); y = max(y, 2)
        p1, p2 = self.px(grp, x, y), self.px(grp, x + w, y2)
        r = Rectangle(width=p2[0] - p1[0], height=p1[1] - p2[1], stroke_color=color, stroke_width=6, fill_opacity=0)
        r.move_to((p1 + p2) / 2)
        return r

    def zoom_to(self, grp, rect, factor, run_time=1.0):
        """scale screenshot (and its highlight) about the rect centre, then move that centre toward the content area centre"""
        c = rect.get_center()
        target = np.array([0, -0.45, 0])
        self.play(grp.animate.scale(factor, about_point=c).shift(target - c), rect.animate.scale(factor, about_point=c).shift(target - c), run_time=run_time)

    def unzoom(self, grp, rect, factor, run_time=0.8):
        c = rect.get_center()
        self.play(grp.animate.scale(1 / factor, about_point=c).move_to(IMG_C), FadeOut(rect), run_time=run_time)


# ===================== scenes =====================
class S01(Base):
    key, title = "s1", ""

    def construct(self):
        bar = Rectangle(width=config.frame_width, height=0.12, fill_color=RED, fill_opacity=1, stroke_width=0).to_edge(UP, buff=0)
        kick = txt("FAIR DATA CURATION · BASKAR LAB · ISU TrAC", 22, BLUE, BODY, BOLD).to_corner(UL, buff=0.7).shift(DOWN * 0.3)
        t = txt("Organize your data in four steps", 58, RED, HEAD, BOLD).next_to(kick, DOWN, aligned_edge=LEFT, buff=0.35)
        rule = Line(LEFT * 6.4, RIGHT * 6.4, color=BLUE, stroke_width=3).next_to(t, DOWN, buff=0.2).align_to(t, LEFT)
        sub = txt("FAIR Folder Curator  ·  Study Card Builder  ·  make_manifest.py", 28, GRAY).next_to(rule, DOWN, aligned_edge=LEFT, buff=0.25)
        self.add(bar)
        self.play(FadeIn(kick), Write(t), run_time=1.6)
        self.play(Create(rule), FadeIn(sub, shift=UP * 0.1), run_time=0.8)
        self.until(0.40)
        # passport analogy
        pp = RoundedRectangle(corner_radius=0.15, width=2.5, height=3.0, fill_color=NAVY, fill_opacity=1, stroke_width=0)
        pl = VGroup(txt("STUDY", 24, WHITE, BODY, BOLD), txt("CARD", 24, WHITE, BODY, BOLD), txt("~20 facts", 20, "#DCE6F1")).arrange(DOWN, buff=0.12).move_to(pp)
        passport = VGroup(pp, pl).move_to([-4.6, -1.15, 0])
        cps = VGroup()
        for i, (n, col) in enumerate([("README", T1), ("MIAPPE", T2), ("Croissant", T3), ("DOI record", T4)]):
            b = RoundedRectangle(corner_radius=0.1, width=2.6, height=0.62, fill_color=col, fill_opacity=1, stroke_width=0)
            cps.add(VGroup(b, txt(n, 24, NAVY, BODY, BOLD).move_to(b)))
        cps.arrange(DOWN, buff=0.18).move_to([3.6, -1.15, 0])
        arrows = VGroup(*[Arrow(passport.get_right(), c.get_left(), buff=0.15, color=RED, stroke_width=4, max_tip_length_to_length_ratio=0.08) for c in cps])
        self.play(FadeIn(passport, shift=UP * 0.2), run_time=0.7)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.2), LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in cps], lag_ratio=0.2), run_time=1.6)
        note = txt("Like a passport: give your facts once; every checkpoint reads the same page.", 26, NAVY, BODY, BOLD).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note), run_time=0.5)
        self.finish()


class S02(Base):
    key, title, step = "s2", "The four steps", None

    def construct(self):
        self.add(self.header())
        specs = [("1", "Scan", "FAIR Folder Curator", "reads dates, GPS,\nsensors from files", T1),
                 ("2", "Describe", "Study Card Builder", "everything else,\nonce", T2),
                 ("3", "Organize", "FAIR Folder Curator", "plans layout,\nwrites organize.py", T3),
                 ("4", "Check + deposit", "make_manifest.py", "checksums, QC,\nthen a DOI", T4)]
        cards = VGroup()
        for n, h, app, d, col in specs:
            b = RoundedRectangle(corner_radius=0.12, width=3.0, height=3.4, fill_color=col, fill_opacity=1, stroke_width=0)
            num = txt(n, 64, RED, HEAD, BOLD)
            hh = txt(h, 27, NAVY, BODY, BOLD)
            if hh.width > 2.7:
                hh.scale_to_fit_width(2.7)
            aa = txt(app, 20, BLUE, BODY, BOLD)
            dd = Paragraph(*d.split("\n"), font=BODY, font_size=21, color=GRAY, alignment="center", line_spacing=0.8)
            inner = VGroup(num, hh, aa, dd).arrange(DOWN, buff=0.18).move_to(b)
            cards.add(VGroup(b, inner))
        cards.arrange(RIGHT, buff=0.42).move_to([0, -0.35, 0])
        arrows = VGroup(*[Arrow(cards[i].get_right(), cards[i + 1].get_left(), buff=0.04, color=RED, stroke_width=5, max_tip_length_to_length_ratio=0.35) for i in range(3)])
        cues = [0.06, 0.30, 0.50, 0.72]
        cap = None
        caps = ["Scan the folder", "Describe it once", "Organize with a script", "Check, then deposit for a DOI"]
        for i in range(4):
            self.until(cues[i])
            anims = [FadeIn(cards[i], shift=UP * 0.2)]
            if i:
                anims.append(GrowArrow(arrows[i - 1]))
            self.play(*anims, run_time=0.7)
            cap = self.set_caption(caps[i], cap)
        self.finish()


class S03(Base):
    key, title, step = "s3", "Load the messy folder", 0

    def construct(self):
        self.add(self.header())
        g = self.shot("cur_s1")
        self.play(FadeIn(g), run_time=0.8)
        cap = self.set_caption("Open app/fair-folder-curator.html in Chrome or Edge")
        self.until(0.22)
        r = self.hl(g, "cur_s1", 0)
        self.play(Create(r), run_time=0.6)
        cap = self.set_caption("Drop your folder here · nothing is uploaded", cap)
        self.until(0.55)
        r2 = self.hl(g, "cur_s1", 1)
        self.play(ReplacementTransform(r, r2), run_time=0.6)
        self.zoom_to(g, r2, 1.7)
        cap = self.set_caption("313 files · 17.7 GB · 3 junk · 2 possible duplicates", cap)
        self.finish()


class S04(Base):
    key, title, step = "s4", "Read metadata inside the files", 0

    def construct(self):
        self.add(self.header())
        g = self.shot("cur_meta")
        self.play(FadeIn(g), run_time=0.8)
        cap = self.set_caption("Capture dates, GPS centre and sensor models from file headers")
        self.until(0.12)
        r = self.hl(g, "cur_meta", 0, pad=4)
        self.play(Create(r), run_time=0.6)
        self.until(0.30)
        self.zoom_to(g, r, 1.25, run_time=1.2)
        self.until(0.72)
        cap = self.set_caption("Save the session (curator_session.json) for the next app", cap)
        self.finish()


class S05(Base):
    key, title, step = "s5", "Study Card Builder", 1

    def construct(self):
        self.add(self.header())
        g = self.shot("bld_import")
        self.play(FadeIn(g), run_time=0.8)
        cap = self.set_caption("Import from Curator session: dates, location, sensors filled in")
        self.until(0.10)
        r = self.hl(g, "bld_import", 1, pad=6)
        self.play(Create(r), run_time=0.6)
        self.until(0.42)
        g2 = self.shot("bld_types")
        self.play(FadeOut(r), FadeOut(g), FadeIn(g2), run_time=0.7)
        cap = self.set_caption("Pick your dataset type: 17 types, grouped", cap)
        self.until(0.62)
        r2 = self.hl(g2, "bld_types", 0, pad=6)
        self.play(Create(r2), run_time=0.6)
        self.zoom_to(g2, r2, 1.6)
        cap = self.set_caption("Each type changes the questions, sensors and folder layout", cap)
        self.finish()


class S06(Base):
    key, title, step = "s6", "Sensors and settings", 1

    def construct(self):
        self.add(self.header())
        g = self.shot("bld_sensors")
        self.play(FadeIn(g), run_time=0.8)
        cap = self.set_caption("Add suggested sensors, then fill model, serial and settings")
        self.until(0.10)
        r = self.hl(g, "bld_sensors", 0, pad=6)
        self.play(Create(r), run_time=0.6)
        self.until(0.50)
        r2 = self.hl(g, "bld_sensors", 1, pad=10)
        self.play(ReplacementTransform(r, r2), run_time=0.6)
        self.zoom_to(g, r2, 2.0)
        cap = self.set_caption("ON THE DAY = write it down while collecting", cap)
        self.finish()


class S07(Base):
    key, title, step = "s7", "Protocol and variables", 1

    def construct(self):
        self.add(self.header())
        g = self.shot("bld_protocol")
        self.play(FadeIn(g), run_time=0.8)
        cap = self.set_caption("Protocol: short numbered steps a new student could repeat")
        self.until(0.10)
        r = self.hl(g, "bld_protocol", 0, pad=6)
        self.play(Create(r), run_time=0.6)
        self.until(0.48)
        g2 = self.shot("bld_vars")
        self.play(FadeOut(r), FadeOut(g), FadeIn(g2), run_time=0.7)
        r2 = self.hl(g2, "bld_vars", 0, pad=6)
        self.play(Create(r2), run_time=0.6)
        self.zoom_to(g2, r2, 1.25)
        cap = self.set_caption("Every column: unit · ontology ID · observed / derived / simulated", cap)
        self.finish()


class S08(Base):
    key, title, step = "s8", "Review and download", 1

    def construct(self):
        self.add(self.header())
        g = self.shot("bld_review")
        self.play(FadeIn(g), run_time=0.8)
        cap = self.set_caption("One zip: study card, README, data dictionary, MIAPPE, Croissant …")
        self.until(0.12)
        r = self.hl(g, "bld_review", 0, pad=6)
        self.play(Create(r), run_time=0.6)
        self.until(0.42)
        r2 = self.hl(g, "bld_review", 1, pad=6)
        self.play(ReplacementTransform(r, r2), run_time=0.6)
        self.zoom_to(g, r2, 1.3)
        cap = self.set_caption("… plus Hugging Face, Zenodo, Kaggle and Ag Data Commons files", cap)
        self.until(0.82)
        cap = self.set_caption("Save progress (.json) to come back later", cap)
        self.finish()


class S09(Base):
    key, title, step = "s9", "Load the study card", 2

    def construct(self):
        self.add(self.header())
        g = self.shot("cur_card")
        self.play(FadeIn(g), run_time=0.8)
        cap = self.set_caption("Curator → Load study card (.json)")
        self.until(0.18)
        r = self.hl(g, "cur_card", 1, pad=6)
        self.play(Create(r), run_time=0.6)
        cap = self.set_caption("The interview shows only what is still missing", cap)
        self.until(0.52)
        g2 = self.shot("cur_export")
        self.play(FadeOut(r), FadeOut(g), FadeIn(g2), run_time=0.7)
        r2 = self.hl(g2, "cur_export", 0, pad=6)
        self.play(Create(r2), run_time=0.6)
        self.zoom_to(g2, r2, 1.25)
        cap = self.set_caption("README / MIAPPE / Croissant come from the builder: one source of truth", cap)
        self.finish()


class S10(Base):
    key, title, step = "s10", "Plan, export, run organize.py", 2

    def construct(self):
        self.add(self.header())
        g = self.shot("cur_plan")
        self.play(FadeIn(g), run_time=0.8)
        cap = self.set_caption("Check the planned layout")
        self.until(0.06)
        r = self.hl(g, "cur_plan", 0, pad=6)
        self.play(Create(r), run_time=0.6)
        self.until(0.22)
        g2 = self.shot("cur_howto")
        self.play(FadeOut(r), FadeOut(g), FadeIn(g2), run_time=0.7)
        r2 = self.hl(g2, "cur_howto", 0, pad=6)
        self.play(Create(r2), run_time=0.6)
        self.zoom_to(g2, r2, 1.55)
        cap = self.set_caption("Run once to preview · then add --apply to copy", cap)
        self.until(0.80)
        cap = self.set_caption("Originals stay put · every run can be undone (--undo)", cap)
        self.finish()


class S11(Base):
    key, title, step = "s11", "Check with make_manifest.py", 3

    def construct(self):
        self.add(self.header())
        term = RoundedRectangle(corner_radius=0.12, width=12.6, height=5.6, fill_color="#1b1f24", fill_opacity=1, stroke_width=0).move_to([0, -0.6, 0])
        dots = VGroup(*[Dot(radius=0.07, color=c) for c in ["#ff5f56", "#ffbd2e", "#27c93f"]]).arrange(RIGHT, buff=0.12).move_to(term.get_corner(UL) + np.array([0.45, -0.3, 0]))
        lines = [
            ("$ python tools/make_manifest.py 2025_AEA_maize-uav-lidar", "#9be9a8"),
            ("Done: 7 files, 0.000 GB, 6 problems.", "#e6edf3"),
            ("Wrote 01_metadata/MANIFEST.sha256, manifest.csv, qc_report.md", "#e6edf3"),
            (".", "#1b1f24"),
            ("## junk (1)        misc/Thumbs.db", "#ffbd2e"),
            ("## duplicate (1)   lidar/final_v3_REAL.laz = 20250714_AEA_f01.laz", "#ffbd2e"),
            ("## empty (2)       04_results/empty.csv, misc/Thumbs.db", "#ffbd2e"),
            ("## ID pattern (1)  lidar/final_v3_REAL.laz", "#ff7b72"),
        ]
        tl = VGroup(*[Text(s, font=MONO, font_size=22, color=c) for s, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        tl.move_to(term).align_to(term, LEFT).shift(RIGHT * 0.45 + DOWN * 0.15)
        self.play(FadeIn(term), FadeIn(dots), run_time=0.5)
        self.play(AddTextLetterByLetter(tl[0]), run_time=1.4)
        cap = self.set_caption("Checksums + a quality report for the organized folder")
        self.until(0.30)
        self.play(LaggedStart(*[FadeIn(x) for x in tl[1:4]], lag_ratio=0.3), run_time=1.0)
        self.until(0.45)
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.15) for x in tl[4:]], lag_ratio=0.35), run_time=1.6)
        cap = self.set_caption("Junk · duplicates · empty files · names that break your ID rule", cap)
        self.until(0.84)
        cap = self.set_caption("Fix them, run it again", cap)
        self.finish()


class S12(Base):
    key, title, step = "s12", "Deposit and finish", 3

    def construct(self):
        self.add(self.header())
        g = self.shot("bld_finish")
        self.play(FadeIn(g), run_time=0.8)
        cap = self.set_caption("Deposit → DOI → enter it in the builder → tick the finish checklist")
        self.until(0.10)
        r = self.hl(g, "bld_finish", 0, pad=10)
        self.play(Create(r), run_time=0.6)
        self.until(0.52)
        cover = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=WHITE, fill_opacity=1, stroke_width=0).set_z_index(20)
        one = VGroup(txt("In one line", 30, RED, BODY, BOLD),
                     txt("describe it once  →  organize it  →  check it  →  deposit it", 44, NAVY, HEAD, BOLD),
                     txt("github.com/znjubery/fair-data-curation  ·  start with README.md", 26, GRAY)).arrange(DOWN, buff=0.45).set_z_index(21)
        one[1].scale_to_fit_width(min(one[1].width, 12.8))
        self.play(FadeIn(cover), run_time=0.6)
        self.play(FadeIn(one[0]), Write(one[1]), run_time=1.6)
        self.play(FadeIn(one[2]), run_time=0.5)
        self.finish()
