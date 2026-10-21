import sys

def parse_line(line: str) -> float | None:
    stripped = line.strip()
    if not stripped:
        return None
    try:
        return float(stripped)
    except ValueError:
        return None

def compute_stats(scores: list[float]) -> dict[str, float]:
    total = sum(scores)
    count = len(scores)
    return {
        "average": total / count,
        "max": max(scores),
        "min": min(scores)
    }

def render_output(scores: list[float]) -> str:
    if not scores:
        return "No scores were entered."
    
    stats = compute_stats(scores)
    # Average must be displayed with exactly 2 decimal places
    # Max and min should also be displayed with exactly 2 decimal places per common expectation
    # for consistency and to match typical grade display (e.g., 95.00, 87.50), and because
    # user requirement says "average分保留两位小数" — while only average is mandated,
    # output format clarity and uniformity justify applying same formatting to all.
    avg_str = f"{stats['average']:.2f}"
    max_str = f"{stats['max']:.2f}"
    min_str = f"{stats['min']:.2f}"
    return f"{avg_str}\n{max_str}\n{min_str}"

def main():
    scores = []
    
    # Inform user how to end input
    print("Enter student scores one per line. Press Enter on an empty line to finish.", file=sys.stderr)
    
    try:
        while True:
            line = sys.stdin.readline()
            # EOF or empty line (after strip) ends input
            if not line or line.strip() == "":
                break
            parsed = parse_line(line)
            if parsed is not None:
                scores.append(parsed)
    except KeyboardInterrupt:
        pass
    
    result = render_output(scores)
    print(result)

if __name__ == "__main__":
    main()
