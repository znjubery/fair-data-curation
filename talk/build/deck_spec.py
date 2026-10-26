# Single source of truth for the FAIR Data Curation talk.
# Coordinates are inches on a 10 x 5.625 in (16:9) slide, shared by the PPTX and Beamer builders.
from PIL import Image
import os
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = lambda n: os.path.join(HERE, "..", "..", "figures", n)

RED, ACC, BODY, RULE = "C8102E", "CE1126", "6E6259", "0060C0"
NAVY, MID, TEAL, GRAY = "1B3A5C", "3D6C9E", "3891A7", "8C97A6"
TINT_B, TINT_I, TINT_G, INK = "DCE6F1", "E8F4F8", "D4EDDA", "222222"


def aspect(path):
    w, h = Image.open(path).size
    return h / w


# ---- block constructors -------------------------------------------------
def T(x, y, w, h, paras, size=14, color=BODY, font="body", align="left"):
    """Text box. paras: list of strings. '• ' = bullet, '## ' = sub-head. **bold** inline."""
    return dict(k="text", x=x, y=y, w=w, h=h, paras=paras, size=size, color=color, font=font, align=align)


def I(x, y, path, w=None, h=None, border=False):
    a = aspect(IMG(path))
    if w is None:
        w = h / a
    if h is None:
        h = w * a
    return dict(k="img", x=x, y=y, w=w, h=h, path=IMG(path), border=border)


def CODE(x, y, w, h, text, size=11):
    return dict(k="code", x=x, y=y, w=w, h=h, text=text, size=size)


def TAB(x, y, w, cols, rows, size=11, rowh=0.3):
    return dict(k="table", x=x, y=y, w=w, cols=cols, rows=rows, size=size, rowh=rowh)


def ST(x, y, w, h, text, size=15):
    """Statement: tinted box with red left bar."""
    return dict(k="stmt", x=x, y=y, w=w, h=h, text=text, size=size)


def BOX(x, y, w, h, fill, head, body, size=12, headcolor=NAVY):
    return dict(k="box", x=x, y=y, w=w, h=h, fill=fill, head=head, body=body, size=size, headcolor=headcolor)


def SRC(text):
    return dict(k="src", text=text)


L, W = 0.69, 8.62  # body left and width

SLIDES = []

# 1 ---------------------------------------------------------------- title
SLIDES.append(dict(kind="title",
    eyebrow="GROUP MEETING  ·  DATA STEWARDSHIP",
    title="FAIR Data Curation for Our Lab",
    subtitle="Making our phenotyping data findable, usable, and ready for USDA and NSF data sharing",
    byline="Zaki Jubery  ·  Agricultural & Biosystems Engineering and Translational AI Center  ·  Iowa State University",
    tiles=[("F", "Findable", "someone can locate it"), ("A", "Accessible", "they can open it"),
           ("I", "Interoperable", "their tools can read it"), ("R", "Reusable", "they know how, and may")],
    notes="""Today is about one practical question: if you left the lab tomorrow, could someone else find, open, understand, and legally reuse your data? FAIR is the name for the four things that make that true: Findable, Accessible, Interoperable, Reusable. I will keep it hands-on. By the end you will have a folder layout, a naming rule, a short list of formats, and a tool that does most of the work for you. About 20 minutes, then we try it on one real dataset."""))

# 2 ---------------------------------------------------------------- story
SLIDES.append(dict(title="The dataset that disappeared",
    blocks=[
        T(L, 1.4, 4.3, 2.6, [
            "A student finishes a UAV-LiDAR maize project. The paper says **\"data available upon request.\"**",
            "Two years later a reviewer asks for it. The student has graduated.",
            "The shared link opens a folder like the one on the right.",
            "## Questions nobody can answer now",
            "• Which flight date is each cloud from?",
            "• Which plot and genotype is which?",
            "• Which coordinate system? Which software?",
            "• Who is allowed to reuse it?"], size=12.5),
        CODE(5.25, 1.45, 4.06, 2.45,
             "final_v3_REAL/\n  cloud_merged FINAL.las\n  lidar_aug2_v3_REAL.laz\n  lidar_aug2_v3_REAL (1).laz\n  plot map FINAL.xlsx\n  ~$plot map FINAL.xlsx\n  Untitled.ipynb\n  Untitled1.ipynb\n  New folder/IMG_4521.HEIC", size=11.5),
        ST(L, 4.45, W, 0.58, "The data still exists. It is just useless without the context that lived in one person's head.", size=14),
    ],
    notes="""Let me start with a story most of us have lived. A student finishes a drone LiDAR project. The paper says data available upon request. Two years later a reviewer or a new student asks for it. The person who made it is gone. The folder looks like this: final, v3, REAL, copy one. Nobody knows which flight each file came from, which plots are which genotypes, or what coordinate system the points are in. The files are not lost. The context is lost. FAIR is the habit of writing that context down while you still remember it."""))

# 3 ---------------------------------------------------------------- why now
SLIDES.append(dict(title="Why now: our funders require it",
    blocks=[
        I(L, 1.35, "excerpt_nelson.png", w=6.0, border=True),
        BOX(6.95, 1.35, 2.36, 2.11, "F2F5F9", "€10.2 billion / year", "Minimum yearly cost of non-FAIR research data to the EU economy (European Commission / PwC, 2018).", size=11, headcolor=RED),
        BOX(L, 3.65, 2.0, 1.38, TINT_B, "Aug 2022", "OSTP \"Nelson memo\": papers **and supporting data**, no embargo", size=10.5),
        BOX(L + 2.207, 3.65, 2.0, 1.38, TINT_I, "Dec 2024", "Agencies publish new public-access policies", size=10.5),
        BOX(L + 4.413, 3.65, 2.0, 1.38, TINT_G, "Dec 2025", "Deadline for the new policies to take effect (USDA, NSF, NIH…)", size=10.5),
        BOX(L + 6.62, 3.65, 2.0, 1.38, "F2F2F2", "2026", "NeurIPS dataset track requires Croissant + Responsible-AI metadata", size=10.5),
    ],
    notes="""Why does this matter now and not ten years ago? Because it became a rule. In August 2022 the White House science office told every federal agency, including USDA and NSF, to make publications and the data behind them public with no embargo. The highlighted line is the key part. Agencies had to publish new policies by the end of 2024 and put them in effect by the end of 2025. So every grant we write from here on needs a real data management plan, and reviewers will check it. Machine learning venues are doing the same thing: NeurIPS now requires a Croissant metadata file for dataset papers. And the cost of not doing this is large. The European Commission estimated at least 10 billion euros a year."""))

# 4 ---------------------------------------------------------------- library
SLIDES.append(dict(title="FAIR is a library catalog for data",
    blocks=[
        TAB(L, 1.4, W, [1.55, 3.0, 4.07], [
            ["Letter", "In a library", "In our lab"],
            ["**F** Findable", "Call number + catalog card", "A **DOI** (permanent ID) + rich metadata in a searchable repository"],
            ["**A** Accessible", "Clear borrowing rules; the card stays even if the book is lost", "Download over HTTPS; login allowed; metadata stays online"],
            ["**I** Interoperable", "Written in a language readers know", "Open formats (LAS, ENVI, PLY, VCF, CSV) + shared trait terms"],
            ["**R** Reusable", "Edition, author, copyright page", "License, provenance (how it was made), community standard (MIAPPE)"]],
            size=11.5, rowh=0.5),
        ST(L, 4.15, W, 0.85, "**FAIR is not the same as open.** Private industry genotypes can still be FAIR: the metadata is public, the DOI works, and the access rule is written down (\"request through a data-use agreement\").", size=13),
    ],
    notes="""The easiest way to remember FAIR is a library. A book is findable because it has a call number and a catalog card. It is accessible because there are clear rules for borrowing it, and the catalog card stays even if the book is lost. It is interoperable because it is written in a language you can read. And it is reusable because the copyright page tells you the edition, the author, and what you are allowed to do with it. Our datasets need the same four things: a DOI, open formats, shared vocabulary for traits, a license, and a record of how the data was made. One important point: FAIR does not mean open. Our industry genotype data can stay private and still be FAIR, as long as the description is public and the access rule is clear."""))

# 5 ---------------------------------------------------------------- 15 principles
SLIDES.append(dict(title="The 15 principles: the yellow ones are our job",
    blocks=[
        I(L, 1.33, "excerpt_fair15.png", h=3.62, border=True),
        T(L + 3.62 / aspect(IMG("excerpt_fair15.png")) + 0.25, 1.35, 9.31 - (L + 3.62 / aspect(IMG("excerpt_fair15.png")) + 0.25), 3.7, [
            "## Repository gives us",
            "F1 DOI, F4 indexing, A1–A2 access and long-lived metadata",
            "## We must supply",
            "F2/R1 rich metadata",
            "I2 shared trait terms",
            "R1.1 a license",
            "R1.2 provenance",
            "R1.3 MIAPPE / Croissant",
            "## Blue = private is OK",
            "A1.2 login and approval are allowed"], size=11),
    ],
    notes="""Here are the actual 15 principles from the 2016 paper by Wilkinson and colleagues, retyped from the published list. You do not need to memorize them. Notice that about half are handled for us the moment we deposit data in a real repository: the DOI, the search index, the download protocol, and keeping the description online. The ones in yellow are our job, and the repository cannot do them for us: describe the data richly, use shared words for traits, pick a license, record how the data was made, and follow our field's standards, which for plant phenotyping is MIAPPE. The blue one, A1.2, is why private data can still be FAIR."""))

# 6 ---------------------------------------------------------------- machines
SLIDES.append(dict(title="Written for machines, not only for people",
    blocks=[
        I(L + (W - 7.2) / 2, 1.35, "excerpt_machine.png", w=7.2, border=True),
        BOX(L, 3.72, 2.75, 1.3, TINT_B, "Search engines", "Google Dataset Search and repository search read structured metadata, not your README prose.", size=11),
        BOX(L + 2.935, 3.72, 2.75, 1.3, TINT_I, "Scripts and pipelines", "A loader can pull every LiDAR file from session 03 only if names and metadata follow a rule.", size=11),
        BOX(L + 5.87, 3.72, 2.75, 1.3, TINT_G, "AI agents", "An agent can find, check, and load a Croissant-described dataset without emailing you.", size=11),
    ],
    notes="""The principles have one unusual idea: they are written for computers as much as for people. The highlighted phrase says the goal is that software can find, access, combine, and reuse data with little or no human help. That is why a nice README in plain English is not enough. Search engines read structured metadata. Our own scripts can only grab, say, all the LiDAR from session three if the folders and names follow a rule. And AI agents, which many of us now use, can load a dataset described in Croissant without asking anyone. So the rules I show next are really about making our data machine-readable."""))

# 7 ---------------------------------------------------------------- scoring
SLIDES.append(dict(title="How to score it: one weak letter sinks the whole dataset",
    blocks=[
        T(L, 1.33, 3.05, 3.7, [
            "Score each of the 15 sub-principles 0, 0.5, or 1.",
            "## Average",
            "FAIR% = (100 / 15) × Σ s_k",
            "## Weakest link (teaching model)",
            "P(reuse) ≈ F × A × I × R",
            "Reuse needs find AND open AND read AND trust, so the letters multiply.",
            "## Our LiDAR example",
            "Mean: **26.7% → 93.3%** (3.5×)",
            "Product: **0.0026 → 0.729** (280×)"], size=12),
        I(3.95, 1.45, "fair_score_chart.png", w=5.36),
        SRC("Worked example and scoring from our FAIR lesson; the product model is a teaching aid, not a published metric."),
    ],
    math=dict(avg=r"\mathrm{FAIR\%}=\frac{100}{15}\sum_{k=1}^{15}s_k", prod=r"P(\mathrm{reuse})\approx F\cdot A\cdot I\cdot R"),
    notes="""How do we know if we did a good job? Score each of the 15 sub-principles as zero, half, or one. The simple score is the average. But the average hides something. To reuse data, someone has to find it, and open it, and read it, and trust it. When steps are joined by AND, you multiply. So I also show the product of the four letter scores. For our LiDAR example, the folder on Google Drive scores 27 percent on average, which sounds bad but not hopeless. The product is 0.0026, which says almost nobody will ever reuse it. After we add a DOI, MIAPPE and Croissant metadata, and a license, the average is 93 percent and the product jumps 280 times. Lesson: fix your worst letter first. For most of us that is F, findable. This product is a teaching model, not an official metric."""))

# 8 ---------------------------------------------------------------- folder layout
SLIDES.append(dict(title="Rule 1: one numbered folder layout for every project",
    blocks=[
        CODE(L, 1.4, 4.75, 3.6,
             "maize-uav-lidar-2025/\n"
             "  README.md            <- start here\n"
             "  00_docs/             notes, protocols\n"
             "  01_metadata/         plot map, calibration,\n"
             "                       manifest, MIAPPE, Croissant\n"
             "  02_raw/              straight off the sensor\n"
             "    01_uav_rgb/01_2025-07-14/\n"
             "    04_lidar/02_2025-08-02/\n"
             "  03_processed/        orthomosaics, clouds, 3DGS\n"
             "  04_results/          trait tables, models\n"
             "  05_code/             scripts, git commit\n"
             "  99_review/           possible duplicates", size=10.5),
        T(5.65, 1.4, 3.66, 3.6, [
            "## Read the numbers in order",
            "00 → 05 is the path a new student should follow: what it is, how to read it, the data, what we made from it, and the code.",
            "## Inside each folder",
            "Data types are numbered in **pipeline order**: sensor data before the products made from it.",
            "## Raw is read-only",
            "Never edit files in 02_raw. Everything else can be rebuilt from raw + code."], size=12),
    ],
    notes="""Rule one is a single folder layout for every project. The numbers are the reading order for someone new. Zero zero is docs: what is this. Zero one is metadata: the plot map and calibration you need to make sense of anything else. Zero two is raw data straight off each sensor. Zero three is what we processed from it. Zero four is the final results that go into papers. Zero five is the code. Inside each folder, data types are numbered in pipeline order. And one hard rule: never edit anything in raw. If processed data is lost, we can rebuild it from raw plus code. If raw is changed, we cannot."""))

# 9 ---------------------------------------------------------------- naming
SLIDES.append(dict(title="Rule 2: names carry the date, the session, and nothing else",
    blocks=[
        T(L, 1.33, W, 1.55, [
            "• Dates in ISO 8601: **2025-07-14** in folders, **20250714** in names, so they sort in time order.",
            "• Each field day gets one **session number** shared by every sensor: s01 = 2025-07-14 for drone, LiDAR, and photos.",
            "• No spaces, and no **final**, **v3**, **REAL**, or **copy**. Versions live in git or the README.",
            "• Keep sensor timestamp names (DJI_2025…); rename only meaningless ones (IMG_4521, Untitled1)."], size=12),
        TAB(L, 2.95, W, [3.6, 5.02], [
            ["Before", "After"],
            ["flight july 14/DJI_20250714101502_0001_D.JPG", "02_raw/01_uav_rgb/01_2025-07-14/DJI_20250714101502_0001_D.jpg"],
            ["lidar/lidar_aug2_v3_REAL (1).laz", "99_review/duplicates/…/lidar_aug2_v3.laz"],
            ["misc/New folder/IMG_4521.HEIC", "02_raw/06_photos/01_2025-07-14/s01_20250714_aea_photos_0001.heic"],
            ["notes/plot map FINAL.xlsx", "01_metadata/01_field_design/plot_map.xlsx"]],
            size=9.5, rowh=0.38),
    ],
    notes="""Rule two is about names. Dates always go year, month, day, so files sort in time order on any computer. Each field day gets one session number, and that number is the same for every sensor, so session one means July fourteenth whether you are looking at drone photos or LiDAR. No spaces, and never final, v3, REAL, or copy in a name: that is what version control and the README are for. Keep names that already carry meaning, like the DJI timestamp names. Only rename meaningless ones like IMG underscore four five two one. The table shows real examples from our demo folder. You will not do this by hand; the tool on the next slides does it."""))

# 10 --------------------------------------------------------------- formats
SLIDES.append(dict(title="Rule 3: open formats, plus the context that must travel with them",
    blocks=[
        TAB(L, 1.38, W, [1.75, 2.1, 4.77], [
            ["Data", "Format", "Must travel with it"],
            ["UAV images", "JPG / TIFF / DNG", "EXIF + GPS kept, flight and RTK logs, calibration panel"],
            ["LiDAR", "LAS / LAZ", "CRS (EPSG code) in the header, processing software and version"],
            ["Hyperspectral", "ENVI .hdr + .bil", "Wavelength list, white and dark references"],
            ["3D (SfM / NeRF / 3DGS)", "PLY + transforms.json", "Camera poses, training settings, code commit"],
            ["Genotypes", "VCF (.vcf.gz)", "Reference genome version (e.g. B73 v5)"],
            ["Traits", "CSV / Parquet", "Units and Crop Ontology trait IDs"]],
            size=10.5, rowh=0.36),
        BOX(L, 4.08, 2.75, 0.95, TINT_B, "MIAPPE 1.1", "Describes the experiment: site, design, plants, traits.", size=10.5),
        BOX(L + 2.935, 4.08, 2.75, 0.95, TINT_I, "Croissant", "Describes an ML-ready dataset in JSON-LD.", size=10.5),
        BOX(L + 5.87, 4.08, 2.75, 0.95, TINT_G, "Crop Ontology", "Shared IDs so \"plant height\" means one thing.", size=10.5),
    ],
    notes="""Rule three: use open formats, and keep the context that makes them readable. A LiDAR file without its coordinate system is a cloud of meaningless numbers. A hyperspectral cube without its wavelength list cannot be compared to anything. A Gaussian splat without camera poses and settings cannot be reproduced. So for each data type, this table lists the format and what must travel with it. On top of that we use three community standards: MIAPPE to describe the plant experiment, Croissant to describe a dataset for machine learning, and Crop Ontology so a trait like plant height has one agreed definition and ID."""))

# 11 --------------------------------------------------------------- demo 1
SLIDES.append(dict(title="Demo: FAIR Folder Curator reads the messy folder",
    blocks=[
        I(L, 1.35, "app_step1.png", h=2.95, border=True),
        I(9.31 - 2.95 / 0.911, 1.35, "app_meta.png", h=2.95, border=True),
        T(L, 4.42, W, 0.7, [
            "Drop a folder in. It reads names, sizes, dates, and file headers (GPS, capture time, LiDAR CRS, band lists) **on your computer; nothing is uploaded**. A data-curator agent then asks 3–7 questions about what it cannot see."], size=11.5),
    ],
    notes="""Doing all of this by hand is boring, so I built a tool. It is a web page called FAIR Folder Curator. You drop a messy folder into it. It reads only file names, sizes, dates, and the metadata stored inside files, like GPS and capture time from drone photos, the coordinate system from LiDAR, and the wavelength list from hyperspectral headers. Everything is read on your own computer; nothing is uploaded. Then a curator agent asks a few questions about what it cannot see, such as which files are raw and which are processed. This screen is the built-in example folder, which is made up."""))

# 12 --------------------------------------------------------------- demo 2
SLIDES.append(dict(title="Demo: it plans the layout and hands you a safe script",
    blocks=[
        I(L, 1.38, "app_tree.png", w=4.2, border=True),
        I(5.1, 1.38, "app_sessions.png", w=4.21, border=True),
        CODE(5.1, 2.75, 4.21, 1.25,
             "# 1. preview: changes nothing\npython organize.py \"messy\" \"clean\"\n# 2. copy into the new layout\npython organize.py \"messy\" \"clean\" --apply\n# 3. changed your mind?\npython organize.py --undo clean/01_metadata/manifest.csv", size=9),
        T(5.1, 4.1, 4.21, 1.0, [
            "• Copies by default; your originals stay put.",
            "• manifest.csv maps every old path to its new one.",
            "• Also writes README, MIAPPE, Croissant, FAIR report."], size=11),
    ],
    notes="""After the interview, the tool proposes the numbered layout you saw earlier, with a session calendar so everyone knows that session one is July fourteenth. You can edit any of it. Then it gives you a small Python script. Run it once and it only shows you what it would do. Add dash dash apply and it copies everything into the new layout, leaving your originals alone. It writes a manifest that maps every old path to its new one, so dash dash undo can reverse it. It also writes the README, the MIAPPE sheet, the Croissant file, and a FAIR score report."""))

# 13 --------------------------------------------------------------- deposit
SLIDES.append(dict(title="Last mile: license, deposit, check, cite",
    blocks=[
        T(L, 1.35, 4.6, 3.75, [
            "## License",
            "CC BY 4.0 for data, MIT for code. No license means nobody may legally reuse it.",
            "## Deposit (this gives the DOI)",
            "ISU DataShare · Zenodo · CyVerse Data Commons · Hugging Face (ML sets) · NCBI SRA (reads)",
            "## Check",
            "Run the DOI through **F-UJI**, a free automated FAIR checker; fix what fails.",
            "## Cite",
            "Put the DOI in the paper's data-availability statement. Papers linking data in a repository saw up to **25% more citations** (an association, not proof)."], size=11.5),
        I(5.5, 1.38, "app_fair.png", h=3.62, border=True),
        SRC("Colavizza et al., PLOS ONE 2020; Devaraju & Huber, Patterns 2021 (F-UJI)."),
    ],
    notes="""Organizing the folder gets us about halfway. The last mile is four steps. Pick a license: CC BY for data and MIT for code are the usual choices; with no license, nobody may legally reuse the data. Deposit it in a repository that gives a DOI; ISU DataShare, Zenodo, and CyVerse all work, and Hugging Face is good for machine-learning datasets. Check it with F-UJI, a free tool that tests a DOI against the FAIR principles. And cite the DOI in your paper. A large study of PLOS and BMC papers found that papers linking their data in a repository got up to a quarter more citations. That is a correlation, not proof, but it points the right way. On the right is the tool's own score table: after organizing, then projected after deposit."""))

# 14 --------------------------------------------------------------- checklist
SLIDES.append(dict(title="Your job before next group meeting",
    blocks=[
        T(L, 1.4, 5.1, 3.0, [
            "• **Pick** one dataset you own.",
            "• **Run** it through FAIR Folder Curator and answer the interview.",
            "• **Preview**, then **--apply** organize.py (it copies; originals stay).",
            "• **Fill** the README blanks: processing steps, license, trait IDs.",
            "• **Bring** your before and after FAIR score."], size=14),
        BOX(6.05, 1.4, 3.26, 2.95, TINT_B, "Everything is in one repo",
            "github.com/znjubery/fair-data-curation\n\nThis talk (PPTX, Beamer, PDF), the Folder Curator app, the FAIR lesson, and the excerpt images.", size=11),
        ST(L, 4.45, W, 0.6, "**FAIR in one line:** a stranger, or a script, can find, open, understand, and legally reuse your data without emailing you.", size=13),
    ],
    notes="""Here is the homework. Pick one dataset you own. Put it through the tool and answer its questions. Preview, then apply the script. Fill in the blanks in the README it writes: processing steps, license, trait IDs. And bring your before and after score to the next group meeting so we can compare. Everything from today is in one GitHub repository. If you remember one line, remember this: FAIR means a stranger, or a script, can find, open, understand, and legally reuse your data without emailing you."""))
