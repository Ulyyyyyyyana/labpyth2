# sports_team/report.py
from docx import Document
from sports_team.team import Team


def save_team_report_docx(team: Team, filename: str):
    """
    Создаёт отчёт о команде и сохраняет его в формате .docx
    """
    doc = Document()
    doc.add_heading(f"Отчёт о команде: {team.name}", level=1)

    stats = team.to_dict()
    doc.add_paragraph(f"Количество игроков: {stats['Количество игроков']}")
    doc.add_paragraph(f"Общие голы: {stats['Общие голы']}")
    doc.add_paragraph(f"Общие передачи: {stats['Общие передачи']}")
    doc.add_paragraph(f"Средние матчи на игрока: {stats['Средние матчи на игрока']}")

    doc.add_heading("Состав команды", level=2)
    table = doc.add_table(rows=1, cols=4)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Имя"
    hdr_cells[1].text = "Номер"
    hdr_cells[2].text = "Позиция"
    hdr_cells[3].text = "Голы"

    for player in team.players:
        row = table.add_row().cells
        row[0].text = player.name
        row[1].text = str(player.number)
        row[2].text = player.position
        row[3].text = str(player.goals)

    doc.add_paragraph()
    top = team.top_scorer()
    if top:
        doc.add_paragraph(f"Лучший бомбардир: {top.name} ({top.goals} голов)")

    doc.save(filename)
    print(f"📄 Отчёт сохранён: {filename}")
