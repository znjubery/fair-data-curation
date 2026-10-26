from playwright.sync_api import sync_playwright
import base64,os
F=os.path.expanduser("~/.fonts/")
def ff(name,file): return f"@font-face{{font-family:'{name}';src:url(data:font/ttf;base64,{base64.b64encode(open(F+file,'rb').read()).decode()})}}"
FONTS=ff("MW","Merriweather-Regular.ttf")+ff("MWB","Merriweather-Bold.ttf")+ff("OS","OpenSans-Regular.ttf")+ff("OSB","OpenSans-Bold.ttf")+ff("OSI","OpenSans-Italic.ttf")
CSS=FONTS+"""
body{margin:0;background:#fff}
.page{width:1100px;padding:44px 56px 30px;background:#fdfcf8;border:1px solid #d9d4c7;box-shadow:0 6px 18px rgba(0,0,0,.12);font:23px/1.55 MW,serif;color:#222}
.kick{font:15px OSB,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#6E6259;margin-bottom:14px}
h3{font:26px/1.3 MWB,serif;margin:0 0 16px;color:#222}
mark{background:#ffe45c;padding:1px 3px;border-radius:2px}
mark.b{background:#cfe3ff}
ol,ul{margin:0;padding-left:30px} li{margin:2px 0}
.grp{font:17px OSB,sans-serif;color:#C8102E;margin:14px 0 2px;letter-spacing:.06em}
.r{display:grid;grid-template-columns:62px 1fr;break-inside:avoid}.id{font:18px OSB,sans-serif;color:#1B3A5C;padding-top:2px}.grp{break-after:avoid}
.src{margin-top:22px;padding-top:10px;border-top:1px solid #d9d4c7;font:15px OSI,sans-serif;color:#6E6259}
"""
pages={
"excerpt_nelson":"""<div class=kick>Excerpt · OSTP memorandum, Aug 25 2022 ("Nelson memo")</div>
<p style="margin:0 0 10px">OSTP recommends that federal agencies, to the extent consistent with applicable law:</p>
<ol><li><mark>Update their public access policies as soon as possible, and no later than December 31st, 2025, to make publications and their supporting data resulting from federally funded research publicly accessible without an embargo</mark> on their free and public release;</li>
<li>Establish transparent procedures that ensure scientific and research integrity is maintained in public access policies; and,</li>
<li>Coordinate with OSTP to ensure equitable delivery of federally funded research results and data.</li></ol>
<div class=src>"Ensuring Free, Immediate, and Equitable Access to Federally Funded Research," White House OSTP (public domain). Retyped excerpt; highlight added.</div>""",
"excerpt_fair15":"""<div class=kick>Excerpt · The FAIR Guiding Principles (Wilkinson et al. 2016)</div>
<div style="columns:2;column-gap:44px;font-size:19px;line-height:1.45">
<div class=grp>TO BE FINDABLE</div>
<div class=r><span class=id>F1</span><span><mark>(Meta)data are assigned a globally unique and persistent identifier</mark></span></div>
<div class=r><span class=id>F2</span><span><mark>Data are described with rich metadata</mark> (defined by R1 below)</span></div>
<div class=r><span class=id>F3</span><span>Metadata clearly and explicitly include the identifier of the data they describe</span></div>
<div class=r><span class=id>F4</span><span>(Meta)data are registered or indexed in a searchable resource</span></div>
<div class=grp>TO BE ACCESSIBLE</div>
<div class=r><span class=id>A1</span><span>(Meta)data are retrievable by their identifier using a standardised communications protocol</span></div>
<div class=r><span class=id>A1.1</span><span>The protocol is open, free, and universally implementable</span></div>
<div class=r><span class=id>A1.2</span><span>The protocol allows for an <mark class=b>authentication and authorisation procedure, where necessary</mark></span></div>
<div class=r><span class=id>A2</span><span>Metadata are accessible, even when the data are no longer available</span></div>
<div class=grp>TO BE INTEROPERABLE</div>
<div class=r><span class=id>I1</span><span>(Meta)data use a formal, accessible, shared, and broadly applicable language for knowledge representation</span></div>
<div class=r><span class=id>I2</span><span>(Meta)data use <mark>vocabularies that follow FAIR principles</mark></span></div>
<div class=r><span class=id>I3</span><span>(Meta)data include qualified references to other (meta)data</span></div>
<div class=grp>TO BE REUSABLE</div>
<div class=r><span class=id>R1</span><span>(Meta)data are richly described with a plurality of accurate and relevant attributes</span></div>
<div class=r><span class=id>R1.1</span><span><mark>(Meta)data are released with a clear and accessible data usage license</mark></span></div>
<div class=r><span class=id>R1.2</span><span><mark>(Meta)data are associated with detailed provenance</mark></span></div>
<div class=r><span class=id>R1.3</span><span><mark>(Meta)data meet domain-relevant community standards</mark></span></div>
</div>
<div class=src>Wilkinson et al., Sci Data 3:160018 (2016), CC BY 4.0; wording as listed at go-fair.org. Retyped; yellow = what our lab acts on, blue = why private data can still be FAIR.</div>""",
"excerpt_machine":"""<div class=kick>Excerpt · GO FAIR, "FAIR Principles"</div>
<p style="margin:0;font-size:27px;line-height:1.55">The principles emphasise <mark>machine-actionability</mark> (i.e., <mark>the capacity of computational systems to find, access, interoperate, and reuse data with none or minimal human intervention</mark>) because humans increasingly rely on computational support to deal with data as a result of the increase in volume, complexity, and creation speed of data.</p>
<div class=src>go-fair.org/fair-principles (CC BY 4.0). Retyped excerpt; highlight added.</div>"""}
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(device_scale_factor=2)
    for k,v in pages.items():
        pg.set_content(f"<style>{CSS}</style><div class=page id=p>{v}</div>"); pg.wait_for_timeout(300)
        pg.locator("#p").screenshot(path=f"../../figures/{k}.png"); print(k)
    b.close()
