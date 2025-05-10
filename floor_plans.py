"""
floor_plans_css_mm.py
────────────────────────────────────────────────────────
• Put your CSVs (rez.csv, etage.csv, …) in ./data/
• Run:  python floor_plans_css_mm.py
• Open each generated HTML in Chrome  →  Print
  - Paper size : A4 portrait
  - Margins    : None
  - Scale      : 100 %
The printed span from x = –1 m to x = 12 m is exactly 13 cm.
"""

import csv
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go

# ────── USER SETTINGS ──────
data_dir   = Path("data")
csv_files  = ["rez.csv", "etage.csv"]        # filenames inside data/
BOX_W_MM   = 130                             # physical width of drawing box 180
BOX_H_MM   = 130                             # physical height of drawing box 250
AX_MIN, AX_MAX = -1, 12                      # limits for both axes
PAGE_W_MM, PAGE_H_MM = 210, 297             # A4 portrait

# ────── CSS (centres the box & stretches plot) ──────
CSS = f"""
<style>
@media print {{
  @page {{ size:A4 portrait; margin:0; }}
  body  {{ margin:0; }}
}}
body {{
  width:{PAGE_W_MM}mm; height:{PAGE_H_MM}mm;
  position:relative;
}}
#plot-box {{
  position:absolute;
  top:50%; left:50%;
  width:{BOX_W_MM}mm; height:{BOX_H_MM}mm;
  transform:translate(-50%,-50%);
}}
/* Force Plotly’s inner div to fill the mm-sized box */
#plot-box .plotly-graph-div {{
  width:100% !important;
  height:100% !important;
}}
</style>
"""

# ────── Build one figure from a CSV ──────
def build_fig(csv_path: Path) -> go.Figure:
    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = [{k.strip().lower(): v for k, v in r.items()}
                for r in csv.DictReader(f)]

    fig = go.Figure()

    for r in rows:
        try:
            x0, y0 = float(r["org x"]), float(r["org y"])
            w,  h  = float(r["x"]),     float(r["y"])
        except Exception:
            continue                      # skip non-numeric / blank rows

        label = r.get("utilisation", "").strip()
        if r.get("area"):
            try:
                label += f"<br>{float(r['area']):.1f}\u202Fm²"
            except ValueError:
                pass

        fig.add_shape(type="rect",
                      x0=x0, y0=y0, x1=x0 + w, y1=y0 + h,
                      line=dict(color="black"))
        fig.add_annotation(x=x0 + w/2, y=y0 + h/2, text=label,
                           showarrow=False, xanchor="center",
                           yanchor="middle", font=dict(size=12))

    # fixed frame (–1,–1 … 12,12)
    fig.update_xaxes(range=[AX_MIN, AX_MAX],
                     showticklabels=False, ticks="")
    fig.update_yaxes(range=[AX_MIN, AX_MAX],
                     showticklabels=False, ticks="",
                     scaleanchor="x", scaleratio=1)

    # let Plotly fill the CSS-controlled box
    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="white",
        plot_bgcolor="lightskyblue",
        title=dict(
            text=f"{csv_path.stem} – échelle 1 : 100",
            x=0.5, xanchor="center",
            y=0.96, yanchor="top",
            font=dict(size=18)
        ),
        showlegend=False
    )
    return fig

# ────── Generate HTMLs ──────
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
for fname in csv_files:
    p = data_dir / fname
    if not p.exists():
        print("⚠️ missing:", p)
        continue

    fig = build_fig(p)
    html_core = fig.to_html(full_html=False,
                            include_plotlyjs="cdn",
                            config=dict(responsive=True))

    out = data_dir / f"{p.stem}_{stamp}_A4.html"
    out.write_text(CSS + f"<div id='plot-box'>{html_core}</div>",
                   encoding="utf-8")
    print("✅ saved", out)

print("\nPrint each HTML → A4 portrait · margins none · 100 % scale – "
      "blue box is 180 mm × 250 mm, so 1 cm on paper = 1 m in reality.")
