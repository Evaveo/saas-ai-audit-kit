"""
Génère un fichier Excel d'audit SaaS+IA, vide ou pré-rempli avec les résultats
fournis par les sous-agents d'audit.

USAGE :
    # Génération du template vide
    python audit_xlsx.py --output audit_template.xlsx

    # Génération + remplissage avec résultats d'audit
    python audit_xlsx.py --results audit_results.json --output AUDIT_filled.xlsx

Le fichier `themes.json` doit être dans le même dossier que ce script.

Format attendu de audit_results.json :
{
  "audited_repo": "/path/to/repo",
  "audit_date": "2026-05-27",
  "themes": {
    "01_Produit_UX": {
      "1.1": {"status": "OK"|"KO"|"N/A", "evidence": "file:line ou null", "notes": "..."},
      ...
    },
    ...
  }
}
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation


SCRIPT_DIR = Path(__file__).parent


# ─── Styling ─────────────────────────────────────────────────────────────────

BORDER_THIN = Border(
    left=Side(style="thin", color="D0D0D0"),
    right=Side(style="thin", color="D0D0D0"),
    top=Side(style="thin", color="D0D0D0"),
    bottom=Side(style="thin", color="D0D0D0"),
)

HEADER_FILL = PatternFill("solid", fgColor="1F2937")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
TITLE_FONT = Font(name="Calibri", size=18, bold=True, color="0F172A")
SUBTITLE_FONT = Font(name="Calibri", size=11, italic=True, color="64748B")
META_FONT = Font(name="Calibri", size=10, color="475569")
CELL_FONT = Font(name="Calibri", size=11, color="0F172A")
SECTION_HEADER_FONT = Font(name="Calibri", size=12, bold=True, color="0F172A")

CRIT_FILLS = {
    "🔴": PatternFill("solid", fgColor="FEE2E2"),
    "🟡": PatternFill("solid", fgColor="FEF3C7"),
    "🟢": PatternFill("solid", fgColor="DCFCE7"),
}

STATUS_FILLS = {
    "OK": PatternFill("solid", fgColor="BBF7D0"),
    "KO": PatternFill("solid", fgColor="FECACA"),
    "N/A": PatternFill("solid", fgColor="E2E8F0"),
}


def style_header_row(ws, row: int, columns: int) -> None:
    for col in range(1, columns + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = BORDER_THIN


# ─── Build ───────────────────────────────────────────────────────────────────

def build_workbook(themes: list[dict], results: dict | None = None,
                   audited_repo: str | None = None, audit_date: str | None = None) -> Workbook:
    """
    Construit le classeur. Si `results` est fourni, pré-remplit Score + Commentaire.
    """
    wb = Workbook()

    # ── Mode d'emploi ────────────────────────────────────────────────────────
    ws = wb.active
    ws.title = "Mode d'emploi"

    ws["A1"] = "Grille d'audit SaaS + IA"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:E1")

    subtitle = "Audit automatisé via skill Claude — repo : " + (audited_repo or "n/a")
    if audit_date:
        subtitle += f" — date : {audit_date}"
    ws["A2"] = subtitle if results else "Cadre réutilisable pour auditer n'importe quel SaaS qui intègre de l'IA."
    ws["A2"].font = SUBTITLE_FONT
    ws.merge_cells("A2:E2")

    sections = [
        (None, None),
        ("Méthode", None),
        (None, "• Chaque onglet = un thème de l'audit (12 thèmes)."),
        (None, "• Score : OK / KO / N/A (dropdown sur la colonne Score)."),
        (None, "• La feuille 'Synthèse' agrège automatiquement les scores."),
        (None, None),
        ("Légende criticité", None),
        ("🔴", "Bloquant launch — fixer avant ouverture publique"),
        ("🟡", "Important — à corriger sous 30 jours"),
        ("🟢", "Amélioration continue — nice to have"),
        (None, None),
        ("Seuils de décision", None),
        ("> 90%", "Ready to scale — focus growth"),
        ("80-90%", "Ready to launch — fix les 🟡 sous 30j"),
        ("65-80%", "Ready bêta privée — fix tous les 🔴"),
        ("< 65%", "Pas prêt pour la prod"),
        (None, None),
        ("Ordre d'attaque", None),
        ("1.", "Tous les 🔴 d'abord (bloquants)"),
        ("2.", "Légal + Données (risque pénal / régulateur)"),
        ("3.", "Sécurité (risque incident)"),
        ("4.", "IA Coûts + Gouvernance (risque facture / image)"),
        ("5.", "Le reste : amélioration continue"),
    ]
    row = 3
    for label, val in sections:
        if label and not val:
            ws.cell(row=row, column=1, value=label).font = SECTION_HEADER_FONT
        elif label:
            ws.cell(row=row, column=1, value=label).font = META_FONT
            ws.cell(row=row, column=2, value=val).font = META_FONT
        elif val:
            ws.cell(row=row, column=2, value=val).font = META_FONT
        row += 1

    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 70

    # ── Synthèse (placeholder, filled at the end) ────────────────────────────
    synthese_ws = wb.create_sheet("Synthèse")

    # ── Theme sheets ─────────────────────────────────────────────────────────
    score_validation = DataValidation(
        type="list", formula1='"OK,KO,N/A"', allow_blank=True, showDropDown=False,
    )
    score_validation.error = "Valeur attendue : OK, KO ou N/A"
    score_validation.errorTitle = "Score invalide"

    for theme in themes:
        ws = wb.create_sheet(theme["id"])
        theme_results = (results.get("themes", {}).get(theme["id"], {})) if results else {}

        ws["A1"] = theme["name"]
        ws["A1"].font = TITLE_FONT
        ws.merge_cells("A1:F1")

        ws["A2"] = theme["description"]
        ws["A2"].font = SUBTITLE_FONT
        ws.merge_cells("A2:F2")

        headers = ["#", "Point de contrôle", "Comment tester", "Criticité", "Score", "Commentaire"]
        for col, h in enumerate(headers, start=1):
            ws.cell(row=4, column=col, value=h)
        style_header_row(ws, 4, len(headers))

        for i, item in enumerate(theme["items"], start=5):
            ws.cell(row=i, column=1, value=item["id"]).font = CELL_FONT
            ws.cell(row=i, column=2, value=item["label"]).font = CELL_FONT
            ws.cell(row=i, column=3, value=item["how"]).font = CELL_FONT
            crit_cell = ws.cell(row=i, column=4, value=item["crit"])
            crit_cell.font = CELL_FONT
            crit_cell.fill = CRIT_FILLS[item["crit"]]
            crit_cell.alignment = Alignment(horizontal="center", vertical="center")

            # Pre-fill from results if available
            item_result = theme_results.get(item["id"], {})
            score_value = item_result.get("status", "")
            score_cell = ws.cell(row=i, column=5, value=score_value)
            score_cell.alignment = Alignment(horizontal="center", vertical="center")
            score_cell.font = Font(name="Calibri", size=11, bold=True)
            if score_value in STATUS_FILLS:
                score_cell.fill = STATUS_FILLS[score_value]

            # Comment column: notes + evidence
            notes = item_result.get("notes", "") if item_result else ""
            evidence = item_result.get("evidence", "") if item_result else ""
            if evidence and evidence != "null":
                comment = f"{notes}\n📍 {evidence}".strip() if notes else f"📍 {evidence}"
            else:
                comment = notes
            ws.cell(row=i, column=6, value=comment).font = CELL_FONT

            for col in range(1, 7):
                cell = ws.cell(row=i, column=col)
                cell.alignment = Alignment(
                    horizontal=cell.alignment.horizontal or "left",
                    vertical="top",
                    wrap_text=True,
                )
                cell.border = BORDER_THIN

        last_row = 4 + len(theme["items"])
        score_validation.add(f"E5:E{last_row}")

        ws.conditional_formatting.add(
            f"E5:E{last_row}",
            FormulaRule(formula=['E5="OK"'], fill=PatternFill("solid", fgColor="BBF7D0")),
        )
        ws.conditional_formatting.add(
            f"E5:E{last_row}",
            FormulaRule(formula=['E5="KO"'], fill=PatternFill("solid", fgColor="FECACA")),
        )
        ws.conditional_formatting.add(
            f"E5:E{last_row}",
            FormulaRule(formula=['E5="N/A"'], fill=PatternFill("solid", fgColor="E2E8F0")),
        )

        widths = [8, 50, 45, 12, 14, 50]
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.row_dimensions[1].height = 28
        ws.row_dimensions[4].height = 24
        for r in range(5, last_row + 1):
            ws.row_dimensions[r].height = 48

        ws.freeze_panes = "A5"
        ws.add_data_validation(score_validation)

    # ── Synthèse ─────────────────────────────────────────────────────────────
    ws = synthese_ws
    ws["A1"] = "Synthèse de l'audit"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:I1")

    subtitle = "Scores agrégés par thème. Le score = (OK) / (OK + KO) — les N/A et les vides ne comptent pas."
    if audited_repo:
        subtitle = f"Repo : {audited_repo}" + (f"  •  Date : {audit_date}" if audit_date else "")
    ws["A2"] = subtitle
    ws["A2"].font = SUBTITLE_FONT
    ws.merge_cells("A2:I2")

    headers = ["#", "Thème", "🔴 Bloquants", "🟡 Important", "🟢 Polish", "OK", "KO", "N/A", "Score %"]
    for col, h in enumerate(headers, start=1):
        ws.cell(row=4, column=col, value=h)
    style_header_row(ws, 4, len(headers))

    row = 5
    for i, theme in enumerate(themes, start=1):
        sheet_name = theme["id"]
        rng = f"'{sheet_name}'!$E$5:$E$200"
        crit_rng = f"'{sheet_name}'!$D$5:$D$200"
        ws.cell(row=row, column=1, value=i).font = CELL_FONT
        ws.cell(row=row, column=2, value=theme["name"]).font = CELL_FONT
        ws.cell(row=row, column=3, value=f'=COUNTIF({crit_rng},"🔴")').font = CELL_FONT
        ws.cell(row=row, column=4, value=f'=COUNTIF({crit_rng},"🟡")').font = CELL_FONT
        ws.cell(row=row, column=5, value=f'=COUNTIF({crit_rng},"🟢")').font = CELL_FONT
        ws.cell(row=row, column=6, value=f'=COUNTIF({rng},"OK")').font = CELL_FONT
        ws.cell(row=row, column=7, value=f'=COUNTIF({rng},"KO")').font = CELL_FONT
        ws.cell(row=row, column=8, value=f'=COUNTIF({rng},"N/A")').font = CELL_FONT
        score_cell = ws.cell(row=row, column=9)
        score_cell.value = f'=IF((F{row}+G{row})=0,"",F{row}/(F{row}+G{row}))'
        score_cell.number_format = "0%"
        score_cell.font = Font(name="Calibri", size=11, bold=True)

        for col in range(1, 10):
            cell = ws.cell(row=row, column=col)
            cell.alignment = Alignment(
                horizontal="center" if col != 2 else "left",
                vertical="center",
                wrap_text=True,
            )
            cell.border = BORDER_THIN
            if col == 3:
                cell.fill = CRIT_FILLS["🔴"]
            elif col == 4:
                cell.fill = CRIT_FILLS["🟡"]
            elif col == 5:
                cell.fill = CRIT_FILLS["🟢"]

        row += 1

    total_row = row
    ws.cell(row=total_row, column=2, value="TOTAL").font = Font(name="Calibri", size=11, bold=True)
    for col_letter, col_idx in [("C", 3), ("D", 4), ("E", 5), ("F", 6), ("G", 7), ("H", 8)]:
        ws.cell(row=total_row, column=col_idx,
                value=f"=SUM({col_letter}5:{col_letter}{total_row-1})").font = Font(name="Calibri", size=11, bold=True)
    ws.cell(row=total_row, column=9,
            value=f'=IF((F{total_row}+G{total_row})=0,"",F{total_row}/(F{total_row}+G{total_row}))').number_format = "0%"
    ws.cell(row=total_row, column=9).font = Font(name="Calibri", size=12, bold=True, color="0F172A")
    for col in range(1, 10):
        ws.cell(row=total_row, column=col).fill = PatternFill("solid", fgColor="F1F5F9")
        ws.cell(row=total_row, column=col).border = BORDER_THIN

    ws.conditional_formatting.add(
        f"I5:I{total_row}",
        CellIsRule(operator="greaterThanOrEqual", formula=["0.9"], fill=PatternFill("solid", fgColor="BBF7D0")),
    )
    ws.conditional_formatting.add(
        f"I5:I{total_row}",
        CellIsRule(operator="between", formula=["0.65", "0.8999"], fill=PatternFill("solid", fgColor="FEF3C7")),
    )
    ws.conditional_formatting.add(
        f"I5:I{total_row}",
        CellIsRule(operator="lessThan", formula=["0.65"], fill=PatternFill("solid", fgColor="FECACA")),
    )

    widths = [6, 40, 14, 14, 14, 8, 8, 8, 14]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 28
    ws.row_dimensions[4].height = 24

    legend_row = total_row + 3
    ws.cell(row=legend_row, column=2, value="Seuils").font = Font(name="Calibri", size=11, bold=True)
    legends = [
        ("> 90%", "Ready to scale — focus growth", "BBF7D0"),
        ("80-90%", "Ready to launch — fix 🟡 sous 30j", "FEF3C7"),
        ("65-80%", "Ready bêta — fix tous les 🔴", "FEF3C7"),
        ("< 65%", "Pas prêt pour la prod", "FECACA"),
    ]
    for i, (k, v, color) in enumerate(legends, start=1):
        r = legend_row + i
        ws.cell(row=r, column=2, value=k).fill = PatternFill("solid", fgColor=color)
        ws.cell(row=r, column=2).font = Font(name="Calibri", size=10, bold=True)
        ws.cell(row=r, column=2).alignment = Alignment(horizontal="center")
        ws.cell(row=r, column=3, value=v).font = META_FONT
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=9)

    ws.freeze_panes = "A5"

    # Reorder: Mode d'emploi (idx 0), Synthèse (idx 1), then themes
    current_idx = wb.sheetnames.index("Synthèse")
    if current_idx != 1:
        wb.move_sheet("Synthèse", offset=1 - current_idx)

    return wb


# ─── Entrypoint ──────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Build/fill SaaS+AI audit workbook")
    parser.add_argument("--results", type=str, default=None,
                        help="Path to audit_results.json (optional — empty template if omitted)")
    parser.add_argument("--output", type=str, required=True,
                        help="Output .xlsx path")
    parser.add_argument("--themes", type=str, default=str(SCRIPT_DIR / "themes.json"),
                        help="Path to themes.json (default: alongside this script)")
    args = parser.parse_args()

    themes_path = Path(args.themes)
    if not themes_path.exists():
        print(f"ERROR: themes.json not found at {themes_path}", file=sys.stderr)
        return 1

    with themes_path.open("r", encoding="utf-8") as f:
        themes = json.load(f)["themes"]

    results = None
    audited_repo = None
    audit_date = None
    if args.results:
        results_path = Path(args.results)
        if not results_path.exists():
            print(f"ERROR: results file not found at {results_path}", file=sys.stderr)
            return 1
        with results_path.open("r", encoding="utf-8") as f:
            results = json.load(f)
        audited_repo = results.get("audited_repo")
        audit_date = results.get("audit_date")

    wb = build_workbook(themes, results=results, audited_repo=audited_repo, audit_date=audit_date)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    print(f"OK: saved to {output_path}")
    if results:
        # Quick summary
        total_ok, total_ko, total_na = 0, 0, 0
        for theme_id, theme_data in (results.get("themes", {}) or {}).items():
            for _, item in theme_data.items():
                s = item.get("status")
                if s == "OK":
                    total_ok += 1
                elif s == "KO":
                    total_ko += 1
                elif s == "N/A":
                    total_na += 1
        scoring = total_ok / (total_ok + total_ko) if (total_ok + total_ko) > 0 else 0
        print(f"Summary: OK={total_ok}  KO={total_ko}  N/A={total_na}  Score={scoring:.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
