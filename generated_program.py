def read_scores():
    scores = []
    while True:
        line = input().strip()
        if line == "":
            break
        try:
            score = float(line)
            scores.append(score)
        except ValueError:
            # 忽略非法输入，不提示、不中断
            continue
    return scores

def compute_statistics(scores):
    if not scores:
        return None
    avg = sum(scores) / len(scores)
    return {
        'avg': avg,
        'max': max(scores),
        'min': min(scores)
    }

def format_output(stats):
    if stats is None:
        return "No scores entered."
    # 平均分保留两位小数（格式化显示，非仅数值四舍五入）
    avg_str = f"{stats['avg']:.2f}"
    return f"Average: {avg_str}\nMaximum: {stats['max']}\nMinimum: {stats['min']}"

def main():
    scores = read_scores()
    stats = compute_statistics(scores)
    print(format_output(stats))

if __name__ == "__main__":
    main()
