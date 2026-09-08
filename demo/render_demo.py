from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEMO = Path(__file__).resolve().parent
FRAMES = DEMO / "slides"
OUTPUT = DEMO / "neighboraid-queue-demo.mp4"
WIDTH, HEIGHT = 1280, 720
FPS = 30
TRANSITION = 1.0

COLORS = {
    "bg": "#07111F",
    "panel": "#10243A",
    "panel2": "#15314C",
    "teal": "#47E6C1",
    "blue": "#60A5FA",
    "amber": "#F9C74F",
    "red": "#FF718B",
    "text": "#F4F8FC",
    "muted": "#AFC2D4",
    "grid": "#1C3852",
}


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        ["C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/lucon.ttf"]
        if mono
        else (["C:/Windows/Fonts/seguisb.ttf", "C:/Windows/Fonts/arialbd.ttf"] if bold else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"])
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)


F_TITLE = font(50, bold=True)
F_H1 = font(36, bold=True)
F_H2 = font(25, bold=True)
F_BODY = font(23)
F_SMALL = font(18)
F_MONO = font(20, mono=True)
F_MONO_SMALL = font(17, mono=True)


def base(index: int, section: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg"])
    d = ImageDraw.Draw(img)
    for x in range(0, WIDTH, 80):
        d.line((x, 0, x, HEIGHT), fill=COLORS["grid"], width=1)
    for y in range(0, HEIGHT, 80):
        d.line((0, y, WIDTH, y), fill=COLORS["grid"], width=1)
    d.rectangle((0, 0, WIDTH, 8), fill=COLORS["teal"])
    d.text((55, 28), "NEIGHBORAID QUEUE", font=F_SMALL, fill=COLORS["teal"])
    d.text((WIDTH - 55, 28), section.upper(), font=F_SMALL, fill=COLORS["muted"], anchor="ra")
    d.text((55, HEIGHT - 36), "Captioned local demo • synthetic data only • no external actions", font=F_SMALL, fill=COLORS["muted"])
    d.text((WIDTH - 55, HEIGHT - 36), f"{index}/11", font=F_SMALL, fill=COLORS["muted"], anchor="ra")
    return img, d


def title(d: ImageDraw.ImageDraw, text: str, subtitle: str = "") -> None:
    d.text((60, 90), text, font=F_H1, fill=COLORS["text"])
    if subtitle:
        d.text((62, 140), subtitle, font=F_BODY, fill=COLORS["muted"])


def panel(d: ImageDraw.ImageDraw, box: tuple[int, int, int, int], heading: str, lines: list[str], accent: str = "teal", mono: bool = False) -> None:
    d.rounded_rectangle(box, radius=20, fill=COLORS["panel"], outline=COLORS[accent], width=2)
    x1, y1, x2, _ = box
    d.text((x1 + 25, y1 + 20), heading, font=F_H2, fill=COLORS[accent])
    y = y1 + 67
    face = F_MONO_SMALL if mono else F_BODY
    for line in lines:
        wrapped = wrap(line, width=72 if mono else max(20, int((x2 - x1) / 13))) or [""]
        for chunk in wrapped:
            d.text((x1 + 25, y), chunk, font=face, fill=COLORS["text"])
            y += 29 if mono else 34
        y += 5


def save_slide(index: int, section: str, draw_fn) -> Path:
    img, d = base(index, section)
    draw_fn(d)
    path = FRAMES / f"slide-{index:02d}.png"
    img.save(path, optimize=True)
    return path


def run_checked(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(command)}\n{completed.stdout}\n{completed.stderr}")
    return completed


def main() -> None:
    DEMO.mkdir(parents=True, exist_ok=True)
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir()

    python = ROOT / ".venv" / "Scripts" / "python.exe"
    cli = ROOT / ".venv" / "Scripts" / "neighboraid.exe"
    if not python.exists() or not cli.exists():
        raise FileNotFoundError("Run the documented local installation first; .venv executables are missing")

    cli_command = [str(cli), "--requests", "examples/requests.json", "--inventory", "examples/inventory.json", "--output", "demo-output.json"]
    cli_result = run_checked(cli_command, ROOT)
    cli_text = cli_result.stdout.strip()
    (DEMO / "cli-output.txt").write_text(cli_text + "\n", encoding="utf-8")

    test_command = [str(python), "-m", "pytest", "-q"]
    test_result = run_checked(test_command, ROOT)
    test_text = test_result.stdout.strip()
    (DEMO / "test-output.txt").write_text(test_text + "\n", encoding="utf-8")

    demo_result = json.loads((ROOT / "demo-output.json").read_text(encoding="utf-8"))
    requests = json.loads((ROOT / "examples" / "requests.json").read_text(encoding="utf-8"))
    inventory = json.loads((ROOT / "examples" / "inventory.json").read_text(encoding="utf-8"))
    summary = {key: demo_result[key] for key in ("processed", "auto_ready", "human_review", "blocked")}
    records = demo_result["records"]
    outcomes = {request["request_id"]: record["status"] for request, record in zip(requests, records)}
    remaining = demo_result["remaining_inventory"]
    audits_safe = all(not row["external_action_taken"] for row in records)

    slides: list[Path] = []

    def s1(d):
        d.text((60, 170), "NeighborAid Queue", font=F_TITLE, fill=COLORS["text"])
        d.text((62, 238), "Privacy-first food-bank request triage", font=F_H1, fill=COLORS["teal"])
        d.rounded_rectangle((60, 340, 1220, 500), radius=24, fill=COLORS["panel"])
        d.text((95, 378), "Routine requests move forward.", font=F_H1, fill=COLORS["text"])
        d.text((95, 430), "Urgent, incomplete, or constrained cases reach a person.", font=F_BODY, fill=COLORS["muted"])
        d.text((62, 555), "Built with the Strands Agents SDK • Good Neighbor Agents", font=F_H2, fill=COLORS["blue"])
    slides.append(save_slide(1, "Opening", s1))

    def s2(d):
        title(d, "The problem", "Small community organizations lose scarce volunteer time to repetitive reconciliation.")
        panel(d, (60, 210, 410, 555), "01  INTAKE", ["Check consent", "Check item names", "Reject unnecessary personal data"], "blue")
        panel(d, (465, 210, 815, 555), "02  INVENTORY", ["Compare requests with stock", "Prevent over-allocation", "Spot shortages"], "amber")
        panel(d, (870, 210, 1220, 555), "03  ESCALATE", ["Surface same-day needs", "Explain constraints", "Keep final decisions human"], "teal")
    slides.append(save_slide(2, "Problem", s2))

    def s3(d):
        title(d, "Inspectable architecture", "A Strands Agent registers three deterministic typed tools.")
        labels = [(70, "Minimized\nrequest JSON", "blue"), (330, "validate_request", "teal"), (585, "plan_allocation", "amber"), (840, "create_audit_record", "teal"), (1080, "Local\nresult", "blue")]
        for i, (x, label, accent) in enumerate(labels):
            w = 180 if i in {0, 4} else 205
            d.rounded_rectangle((x, 270, x + w, 430), radius=18, fill=COLORS["panel"], outline=COLORS[accent], width=3)
            lines = label.split("\n")
            for j, line in enumerate(lines):
                d.text((x + w / 2, 322 + j * 34), line, font=F_H2 if j == 0 else F_BODY, fill=COLORS["text"], anchor="mm")
            if i < 4:
                d.line((x + w + 10, 350, labels[i + 1][0] - 10, 350), fill=COLORS["muted"], width=4)
                d.polygon([(labels[i + 1][0] - 12, 342), (labels[i + 1][0] - 2, 350), (labels[i + 1][0] - 12, 358)], fill=COLORS["muted"])
        d.text((70, 510), "No model provider, cloud service, or credential is required for this local prototype.", font=F_BODY, fill=COLORS["muted"])
    slides.append(save_slide(3, "Architecture", s3))

    sample = requests[0]
    def s4(d):
        title(d, "Synthetic, minimized input", "The demo never uses names, addresses, email, phone numbers, or real beneficiary data.")
        lines = json.dumps(sample, indent=2).splitlines()
        panel(d, (70, 200, 720, 580), "examples/requests.json", lines, "blue", mono=True)
        panel(d, (760, 200, 1210, 580), "Starting inventory", [f"{key}: {value}" for key, value in inventory.items()], "amber", mono=True)
    slides.append(save_slide(4, "Input", s4))

    def s5(d):
        title(d, "Real local CLI execution", "The render script reran the packaged command and captured its real stdout.")
        command = "neighboraid --requests examples/requests.json --inventory examples/inventory.json --output demo-output.json"
        panel(d, (60, 210, 1220, 520), "$ command", [command, "", cli_text], "teal", mono=True)
        d.text((65, 555), "Exit code: 0", font=F_H2, fill=COLORS["teal"])
    slides.append(save_slide(5, "Working demo", s5))

    def s6(d):
        title(d, "Three requests, three explainable outcomes", "The generated demo-output.json contains each status and its audit record.")
        cards = [
            ("DEMO-001", outcomes["DEMO-001"], "Stocked routine request", "teal"),
            ("DEMO-002", outcomes["DEMO-002"], "Same-day + baby-food shortage", "amber"),
            ("DEMO-003", outcomes["DEMO-003"], "Consent not provided", "red"),
        ]
        for i, (rid, status, reason, accent) in enumerate(cards):
            x = 60 + i * 400
            d.rounded_rectangle((x, 220, x + 360, 535), radius=24, fill=COLORS["panel"], outline=COLORS[accent], width=3)
            d.text((x + 25, 250), rid, font=F_H2, fill=COLORS["muted"])
            d.text((x + 25, 320), status, font=F_H2, fill=COLORS[accent])
            for j, line in enumerate(wrap(reason, 25)):
                d.text((x + 25, 390 + j * 34), line, font=F_BODY, fill=COLORS["text"])
        d.text((60, 570), f"Machine summary: processed={summary['processed']} • auto_ready={summary['auto_ready']} • human_review={summary['human_review']} • blocked={summary['blocked']}", font=F_SMALL, fill=COLORS["muted"])
    slides.append(save_slide(6, "Outcomes", s6))

    def s7(d):
        title(d, "Inventory-safe and auditable", "Allocation is bounded by available stock; every external-action flag remains false.")
        panel(d, (60, 210, 610, 555), "Remaining inventory", [f"{key:<16} {value}" for key, value in remaining.items()], "amber", mono=True)
        panel(d, (660, 210, 1220, 555), "Safety checks", [f"Non-negative stock: {all(v >= 0 for v in remaining.values())}", f"All audits external_action_taken=false: {audits_safe}", "No messages sent", "No reservations or eligibility decisions"], "teal", mono=True)
    slides.append(save_slide(7, "Auditability", s7))

    def s8(d):
        title(d, "Tests pass", "The render script reran the project test suite before making this frame.")
        panel(d, (60, 210, 1220, 500), "$ python -m pytest -q", test_text.splitlines(), "teal", mono=True)
        d.text((65, 540), "Exit code: 0", font=F_H2, fill=COLORS["teal"])
        d.text((65, 580), "Coverage includes Strands tool registration, state transitions, PII blocking, inventory reconciliation, and audit output.", font=F_SMALL, fill=COLORS["muted"])
    slides.append(save_slide(8, "Validation", s8))

    def s9(d):
        title(d, "Safety is a product feature", "NeighborAid Queue automates clerical work—not sensitive human judgment.")
        panel(d, (60, 210, 610, 565), "AUTOMATED LOCALLY", ["Schema and consent validation", "Allowed-item enforcement", "Inventory-bounded allocation", "Minimal audit generation"], "teal")
        panel(d, (660, 210, 1220, 565), "HUMAN / EXTERNAL GATE", ["Urgent or constrained cases", "Eligibility and fairness decisions", "Outbound communication", "Purchases, reservations, or publication"], "red")
    slides.append(save_slide(9, "Safety", s9))

    def s10(d):
        title(d, "Designed for practical impact", "Quiet automation returns attention to people-facing support.")
        metrics = [("1", "routine case\nauto-ready", "teal"), ("1", "constrained case\nreviewed by a person", "amber"), ("0", "external actions\ntaken", "blue")]
        for i, (number, label, accent) in enumerate(metrics):
            x = 80 + i * 400
            d.rounded_rectangle((x, 230, x + 330, 515), radius=24, fill=COLORS["panel"], outline=COLORS[accent], width=3)
            d.text((x + 165, 300), number, font=font(72, bold=True), fill=COLORS[accent], anchor="mm")
            for j, line in enumerate(label.split("\n")):
                d.text((x + 165, 400 + j * 34), line, font=F_H2 if j == 0 else F_BODY, fill=COLORS["text"], anchor="mm")
        d.text((80, 560), "Local-first today • AgentCore-ready tool contracts for a future authorized deployment", font=F_H2, fill=COLORS["muted"])
    slides.append(save_slide(10, "Impact", s10))

    def s11(d):
        d.text((60, 175), "NeighborAid Queue", font=F_TITLE, fill=COLORS["text"])
        d.text((62, 245), "Routine work moves. Human judgment stays human.", font=F_H1, fill=COLORS["teal"])
        d.rounded_rectangle((60, 345, 1220, 500), radius=24, fill=COLORS["panel"])
        d.text((95, 385), "Strands Agents SDK  •  Local-first  •  Privacy-first  •  MIT licensed", font=F_H2, fill=COLORS["text"])
        d.text((95, 440), "Good Neighbor Agents", font=F_H1, fill=COLORS["blue"])
        d.text((62, 555), "End of local captioned demo", font=F_BODY, fill=COLORS["muted"])
    slides.append(save_slide(11, "Close", s11))

    durations = [10, 10, 12, 11, 12, 12, 11, 10, 11, 11, 9]
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise FileNotFoundError("ffmpeg not found on PATH")

    command: list[str] = [ffmpeg, "-y"]
    for slide, duration in zip(slides, durations):
        command += ["-loop", "1", "-framerate", str(FPS), "-t", str(duration), "-i", str(slide)]

    filters: list[str] = []
    prior = "[0:v]"
    offset = durations[0] - TRANSITION
    for idx in range(1, len(slides)):
        out = f"[v{idx}]"
        filters.append(f"{prior}[{idx}:v]xfade=transition=fade:duration={TRANSITION}:offset={offset:.3f}{out}")
        prior = out
        offset += durations[idx] - TRANSITION
    filters.append(f"{prior}fps={FPS},format=yuv420p[vout]")
    command += [
        "-filter_complex", ";".join(filters),
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-movflags", "+faststart", "-an", str(OUTPUT),
    ]
    (DEMO / "ffmpeg-command.txt").write_text(subprocess.list2cmdline(command) + "\n", encoding="utf-8")
    render = run_checked(command, ROOT)
    (DEMO / "ffmpeg-render-log.txt").write_text(render.stderr, encoding="utf-8")

    manifest = {
        "title": "NeighborAid Queue — captioned local demo",
        "output": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "synthetic_data_only": True,
        "narration": "omitted; complete captions are burned into every scene",
        "resolution": [WIDTH, HEIGHT],
        "fps": FPS,
        "slide_durations_seconds": durations,
        "transition_seconds": TRANSITION,
        "expected_duration_seconds": sum(durations) - TRANSITION * (len(durations) - 1),
        "cli_command": ".venv/Scripts/neighboraid.exe --requests examples/requests.json --inventory examples/inventory.json --output demo-output.json",
        "cli_exit_code": cli_result.returncode,
        "cli_stdout": cli_text,
        "test_command": ".venv/Scripts/python.exe -m pytest -q",
        "test_exit_code": test_result.returncode,
        "test_stdout": test_text,
        "external_actions_taken": [],
    }
    (DEMO / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"video": str(OUTPUT), "slides": len(slides), "duration_expected": manifest["expected_duration_seconds"], "cli_exit": 0, "tests_exit": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
