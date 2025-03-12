import os
import requests
from datetime import datetime, timedelta
import calendar
import json
import matplotlib.pyplot as plt
import pandas as pd

# Configuració d'entorn
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "usuario/repositorio")
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPOSITORY}"

headers = {"Accept": "application/vnd.github.v4+json"}
if GITHUB_TOKEN:
    headers["Authorization"] = f"token {GITHUB_TOKEN}"

def get_devops_phases():
    """Obtén les fases DevOps definides a GitHub o per defecte."""
    try:
        response = requests.get(f"{GITHUB_API_URL}/labels", headers=headers)
        response.raise_for_status()
        labels = response.json()
        return [label["name"] for label in labels if label["name"] in ["Plan", "Code", "Build", "Test", "Release", "Deploy", "Operate", "Monitor"]]
    except Exception:
        return ["Plan", "Code", "Build", "Test", "Release", "Deploy", "Operate", "Monitor"]

def get_completed_issues_by_week(phase, start_date, end_date):
    """Consulta el nombre de issues tancats per setmana."""
    try:
        query = f"repo:{GITHUB_REPOSITORY} label:\"{phase}\" closed:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
        response = requests.get("https://api.github.com/search/issues", headers=headers, params={"q": query})
        response.raise_for_status()
        return response.json().get("total_count", 0)
    except Exception:
        return 0

def generate_month_checklist(year, month):
    """Genera les dades de la checklist mensual."""
    devops_phases = get_devops_phases()
    first_day, last_day = datetime(year, month, 1), datetime(year, month, calendar.monthrange(year, month)[1])
    weeks = [(first_day + timedelta(days=i*7), first_day + timedelta(days=min((i+1)*7-1, (last_day-first_day).days))) for i in range(4)]

    checklist_data = {"month": first_day.strftime('%B %Y'), "phases": {}}
    for phase in devops_phases:
        phase_data = {f"week{i+1}": {"completed": False, "issues_count": get_completed_issues_by_week(phase, weeks[i][0], weeks[i][1])} for i in range(4)}
        phase_data["total_issues"] = sum(week["issues_count"] for week in phase_data.values())
        checklist_data["phases"][phase] = phase_data
    return checklist_data

def save_checklist_to_json(checklist_data, output_file="checksheet_data.json"):
    """Guarda les dades en format JSON."""
    with open(output_file, 'w') as file:
        json.dump(checklist_data, file, indent=2)
    print(f"Checklist guardada a {output_file}")

def generate_check_sheet_png(checklist_data):
    """Genera una imatge PNG amb la taula de la checklist."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)  # Assegura que la carpeta existeix
    output_path = os.path.join(output_dir, "checksheet_table.png")

    month = checklist_data["month"]
    data = [{"Phase": phase, "Week 1": phase_data["week1"]["issues_count"], "Week 2": phase_data["week2"]["issues_count"],
             "Week 3": phase_data["week3"]["issues_count"], "Week 4": phase_data["week4"]["issues_count"], "Total": phase_data["total_issues"]}
            for phase, phase_data in checklist_data["phases"].items()]
    df = pd.DataFrame(data)

    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    ax.axis("off")

    table = ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)

    plt.title(f'DevOps Check Sheet - {month}', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Check sheet generada: {output_path}")

def main():
    now = datetime.now()
    checklist_data = generate_month_checklist(now.year, now.month)
    save_checklist_to_json(checklist_data)
    generate_check_sheet_png(checklist_data)
    print("Generació de check sheet completada.")

if __name__ == "__main__":
    main()
