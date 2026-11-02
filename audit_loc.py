"""LOC Audit Script - Programmatically calculates Total and Code lines for all source files."""

files = [
    ("frontend/index.html", "HTML"),
    ("frontend/style.css", "CSS"),
    ("frontend/hero.css", "CSS"),
    ("frontend/components.css", "CSS"),
    ("frontend/modals.css", "CSS"),
    ("frontend/footer.css", "CSS"),
    ("frontend/data.js", "JavaScript"),
    ("frontend/app.js", "JavaScript"),
    ("frontend/cart.js", "JavaScript"),
    ("backend/database.py", "Python"),
    ("backend/main.py", "Python"),
    ("run.py", "Python"),
    ("test_app.py", "Python"),
]

print(f"| {'File':<24} | {'Language':<11} | {'Total Lines':<11} | {'Code Lines':<11} |")
print("|" + "-" * 26 + "|" + "-" * 13 + "|" + "-" * 13 + "|" + "-" * 13 + "|")

total_lines_sum = 0
code_lines_sum = 0
by_lang = {}
largest_file = ("", 0)
over_200 = []
over_400 = []

for fpath, lang in files:
    with open(fpath, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
    total = len(all_lines)
    code = 0
    for line in all_lines:
        s = line.strip()
        if not s:
            continue
        if lang in ("CSS", "JavaScript") and s.startswith("/*") and s.endswith("*/"):
            continue
        if lang == "HTML" and s.startswith("<!--") and s.endswith("-->"):
            continue
        if lang == "Python" and s.startswith("#"):
            continue
        code += 1

    total_lines_sum += total
    code_lines_sum += code
    by_lang[lang] = by_lang.get(lang, 0) + total
    if total > largest_file[1]:
        largest_file = (fpath, total)
    if total > 200:
        over_200.append((fpath, total))
    if total > 400:
        over_400.append((fpath, total))

    print(f"| {fpath:<24} | {lang:<11} | {total:<11} | {code:<11} |")

print("\n--- Summary ---")
print(f"Total manually written source files: {len(files)}")
print(f"Total source LOC: {total_lines_sum} (Code lines: {code_lines_sum})")
for l, cnt in by_lang.items():
    print(f"{l} LOC: {cnt}")
print(f"Largest source file: {largest_file[0]} ({largest_file[1]} lines)")
print(f"Any file exceeding 400 LOC: {'None (All files strictly <= 400 lines)' if not over_400 else over_400}")
print(f"Any file exceeding 200 LOC: {[f[0] + ' (' + str(f[1]) + ')' for f in over_200]}")
