from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT = Path(__file__).parent / "frontend" / "public" / "habit-tracker-evaluation-report.pdf"


def build_report() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=18, leading=22, spaceAfter=8))
    styles.add(ParagraphStyle(name="Subtitle", parent=styles["Normal"], alignment=TA_CENTER, fontSize=10, leading=13, textColor=colors.HexColor("#444444")))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=13, leading=16, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#17365D")))
    styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontSize=9, leading=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10))

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.58 * inch,
        bottomMargin=0.55 * inch,
        title="Habit Streak Tracker Project Evaluation Report",
        author="Himanshu Kumar",
    )

    story = []

    def page_header(page_number):
        story.append(Paragraph("Habit Streak Tracker: Personal Habit Agent (CSE476 CA1 Project Evaluation Report)", styles["Small"]))
        story.append(Paragraph(f"Page {page_number}", styles["Small"]))
        story.append(Spacer(1, 8))

    def para(text, style="BodySmall"):
        story.append(Paragraph(text, styles[style]))

    page_header(1)
    story.append(Paragraph("PROJECT EVALUATION REPORT", styles["ReportTitle"]))
    story.append(Paragraph("CSE476 CA1: Habit Streak Tracker Personal Habit Agent", styles["Subtitle"]))
    story.append(Paragraph("An Implementation and Loop Design Analysis", styles["Subtitle"]))
    story.append(Spacer(1, 14))
    details = [
        ["Course & Assignment:", "CSE476 CA1 Project 1"],
        ["Project Title:", "Habit Streak Tracker: Personal Habit Agent"],
        ["Author:", "Himanshu Kumar"],
        ["GitHub Repository:", "https://github.com/HIMANSHUgg75/habit-tracker"],
        ["Live Demonstration:", "https://tokyo-lowest-granted-logs.trycloudflare.com"],
        ["Development Status:", "Completed / Demonstration and Deployment Successful"],
        ["Report Generated:", "September 4, 2026"],
    ]
    table = Table([[Paragraph(f"<b>{key}</b>", styles["Small"]), Paragraph(value, styles["Small"])] for key, value in details], colWidths=[1.55 * inch, 5.75 * inch])
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BBBBBB")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF1F8"))]))
    story.append(table)
    story.append(Spacer(1, 12))
    story.append(Paragraph("Executive Summary", styles["Section"]))
    para("This evaluation report reviews the development and architecture of the Habit Streak Tracker, a lightweight personal habit agent that records daily activity, calculates current and longest streaks, and compares consistency across habits. The project demonstrates a transparent tool-driven workflow, persistent JSON-backed state, a Python implementation, an interactive React interface, and a FastAPI service. The system treats a calendar date as the unit of truth, preventing duplicate logs on the same day from inflating progress.")
    para("The project includes two core tools, <b>log_habit(name)</b> and <b>get_streak(name)</b>, plus the <b>most_consistent()</b> summary operation. A browser interface provides an accessible way to log habits and inspect progress, while the command-line agent and notebook provide demonstration and evaluation paths.")
    story.append(Paragraph("1. Core Architecture &amp; Tech Stack", styles["Section"]))
    para("The Habit Streak Tracker is structured as a small Python application with a FastAPI HTTP layer and a React frontend. The implementation separates decision logic, habit persistence, tool operations, and presentation so each part can be tested independently.")
    para("<b>Python:</b> Provides the local tools, date arithmetic, persistence, and offline agent demonstration.")
    para("<b>Tool-driven agent loop:</b> agent.py selects and dispatches operations, returns observations, and continues until the task is complete.")
    para("<b>FastAPI:</b> Exposes habit logging, streak retrieval, summary, and health-oriented API routes.")
    para("<b>React and CSS:</b> Provides the live dashboard for adding habits, viewing streak cards, and identifying the most consistent habit.")
    para("<b>Jupyter notebook:</b> Provides an interactive demonstration and evaluation record for the agent workflow.")

    story.append(PageBreak())
    page_header(2)
    story.append(Paragraph("Project Codebase Structure", styles["Section"]))
    rows = [
        ["File / Module", "Functionality & Role in Agent System"],
        ["agent.py", "Runs the plan-act interaction loop and routes requested operations to local tools."],
        ["tools.py", "Defines log_habit, get_streak, and most_consistent; handles date normalization and streak calculations."],
        ["habits.json", "Stores habit names and ISO calendar dates so progress survives restarts."],
        ["backend/server.py", "FastAPI service exposing the habit API and serving the production React build."],
        ["frontend/src/App.js", "React dashboard for logging habits and viewing current and best streaks."],
        ["demo.ipynb", "Interactive notebook demonstration of the agent and tool behavior."],
    ]
    table = Table([[Paragraph(f"<b>{cell}</b>", styles["Small"]) if row == 0 else Paragraph(cell, styles["Small"]) for cell in row] for row in rows], colWidths=[1.65 * inch, 5.65 * inch])
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BBBBBB")), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(table)
    story.append(Spacer(1, 12))
    story.append(Paragraph("2. The Plan-Act Execution Loop", styles["Section"]))
    para("The agent does not rely only on an opaque function-calling engine. It exposes a clear plan-act sequence: interpret the habit request, select a tool, execute the local operation, capture the observation, and produce a concise result. This makes the workflow easy to inspect and test.")
    para("Each operation is deterministic at the tool boundary. The model or command-line driver can choose an action, but the Python tools remain responsible for date handling, duplicate detection, streak arithmetic, and persisted state.")
    para("The web deployment uses the same backend routes as the local application. The production React build is served from FastAPI, allowing the UI and API to share one public origin and avoiding a browser dependency on localhost.")

    story.append(PageBreak())
    page_header(3)
    story.append(Paragraph("User Input", styles["Section"]))
    para("Natural-language habit goal, such as logging a reading session or checking the current streak.")
    story.append(Paragraph("Plan Step", styles["Section"]))
    para("The agent identifies the requested habit operation and its required name.")
    story.append(Paragraph("Act Step", styles["Section"]))
    para("The dispatcher invokes log_habit, get_streak, or most_consistent.")
    story.append(Paragraph("Observation", styles["Section"]))
    para("The tool returns structured streak data and updates habits.json when needed.")
    story.append(Paragraph("Final Synthesis", styles["Section"]))
    para("The agent reports the result, including duplicate-log status when relevant.")
    story.append(Paragraph("Detailed Workflow Walkthrough", styles["Section"]))
    for number, text in [
        (1, "User Input: The loop begins with a request to record or inspect a habit."),
        (2, "Plan Step: The agent determines which tool matches the user's intent and prepares its arguments."),
        (3, "Act Step: The selected Python tool reads or updates the JSON-backed habit history."),
        (4, "Observation Step: The tool returns the current streak, longest streak, status, or summary."),
        (5, "Duplicate Protection: A second log for the same calendar date is reported as already counted."),
        (6, "Final Synthesis: The agent presents a human-readable result and ends the loop."),
    ]:
        para(f"<b>{number}.</b> {text}")

    story.append(PageBreak())
    page_header(4)
    story.append(Paragraph("3. Tool Design &amp; Memory Management Details", styles["Section"]))
    para("The agentic behavior of the Habit Streak Tracker depends on small local tools. The agent routes user intent to these operations, while the persistence layer bridges separate runs and keeps the history available after restart.")
    story.append(Paragraph("Registered Capabilities (Tools)", styles["Section"]))
    para("<b>Tool 1: log_habit(name)</b><br/>Records today's ISO date for the named habit, calculates the current streak, and returns whether today's entry was already present.")
    para("<b>Tool 2: get_streak(name)</b><br/>Reads the saved history and returns the current streak, all-time best streak, and a status description.")
    para("<b>Tool 3: most_consistent()</b><br/>Compares all stored habits and identifies the strongest current performer.")
    para("<b>Persistence: habits.json</b><br/>Stores data as a mapping from habit names to ISO date lists. Dates are normalized and deduplicated before calculations.")
    story.append(Paragraph("Development Challenge &amp; Anchoring Solution", styles["Section"]))
    para("<b>Honest Failure Encountered:</b> The first implementation treated repeated logs on the same day as separate progress, which could inflate the apparent streak.")
    para("<b>Resolution:</b> The implementation now treats the calendar date as the unit of truth. It deduplicates stored dates and returns an already_logged_today signal, preserving accurate streaks while keeping the user informed.")
    story.append(Paragraph("4. Evaluation, Failure Analysis &amp; Future Directions", styles["Section"]))

    story.append(PageBreak())
    page_header(5)
    para("An evaluation of the Habit Streak Tracker reveals strengths in transparent tool execution, simple persistence, deterministic date arithmetic, and a focused user interface, while also identifying clear future improvements.")
    story.append(Paragraph("System Strengths", styles["Section"]))
    para("<b>Explicit Execution Visibility:</b> The agent loop exposes the selected operation and returned observation, making behavior easy to debug.")
    para("<b>Deterministic Streak Math:</b> Date normalization, duplicate protection, and consecutive-day calculations are handled by Python tools rather than generated text.")
    para("<b>Persistent Local State:</b> habits.json keeps user history available across process restarts without requiring a database for the core demonstration.")
    para("<b>Accessible Deployment:</b> The React interface and FastAPI routes are served together, providing one working URL for the demonstration.")
    story.append(Paragraph("System Limitations &amp; Failure Risk Analysis", styles["Section"]))
    para("<b>Single-file storage:</b> JSON persistence is appropriate for a local demonstration but is not designed for concurrent multi-user production traffic.")
    para("<b>Temporary public URL:</b> The current live link is a quick tunnel and depends on the local computer and running service remaining online.")
    story.append(Paragraph("Recommended Enhancements (Future Scope)", styles["Section"]))
    for number, text in [
        (1, "Replace the JSON file with SQLite or a hosted database for concurrent and multi-user persistence."),
        (2, "Deploy the frontend and backend to permanent hosting with environment-specific configuration."),
        (3, "Add authentication, per-user habit collections, reminders, and calendar history visualization."),
    ]:
        para(f"<b>{number}.</b> {text}")
    story.append(Paragraph("Code Repository Reference", styles["Section"]))
    para("The complete codebase, tests, notebook demonstrations, production frontend build, and FastAPI service are hosted publicly on GitHub.")
    para("<b>Repository Link:</b> https://github.com/HIMANSHUgg75/habit-tracker")
    para("<b>Demonstration Link:</b> https://tokyo-lowest-granted-logs.trycloudflare.com")

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build_report()