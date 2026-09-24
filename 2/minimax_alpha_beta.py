import random
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class Node:
    """Узел игрового дерева."""
    value: Optional[int] = None
    children: Optional[list] = None

    def is_leaf(self):
        return self.children is None


def build_tree(depth: int, width: int = 2, rng=None) -> Node:
    """Создаёт полное дерево заданной глубины и ширины.
    Листья получают целые значения. Часть листьев намеренно имеет одинаковые значения.
    """
    if rng is None:
        rng = random.Random(42)

    if depth == 0:
        # Диапазон небольшой, поэтому одинаковые значения встречаются достаточно часто.
        return Node(value=rng.randint(-10, 10))

    children = [build_tree(depth - 1, width, rng) for _ in range(width)]
    return Node(children=children)


def collect_leaves(node: Node):
    """Возвращает список всех листьев."""
    if node.is_leaf():
        return [node]

    leaves = []
    for child in node.children:
        leaves.extend(collect_leaves(child))
    return leaves


def make_equal_leaves(root: Node, count: int = 20, value: int = 5):
    """Делает часть листьев одинаковыми, чтобы проверить равенство значений."""
    leaves = collect_leaves(root)
    for leaf in leaves[:min(count, len(leaves))]:
        leaf.value = value


def minimax(node: Node, maximizing: bool, stats: dict) -> int:
    """Обычный рекурсивный Minimax."""
    stats["nodes"] += 1

    if node.is_leaf():
        return node.value

    values = [
        minimax(child, not maximizing, stats)
        for child in node.children
    ]

    return max(values) if maximizing else min(values)


def alpha_beta(node: Node, maximizing: bool, alpha: float, beta: float, stats: dict) -> int:
    """Рекурсивный Minimax с альфа-бета отсечением."""
    stats["nodes"] += 1

    if node.is_leaf():
        return node.value

    if maximizing:
        best = float("-inf")

        for child in node.children:
            value = alpha_beta(child, False, alpha, beta, stats)
            best = max(best, value)
            alpha = max(alpha, best)

            if beta <= alpha:
                stats["cutoffs"] += 1
                break

        return int(best)

    else:
        best = float("inf")

        for child in node.children:
            value = alpha_beta(child, True, alpha, beta, stats)
            best = min(best, value)
            beta = min(beta, best)

            if beta <= alpha:
                stats["cutoffs"] += 1
                break

        return int(best)


def run_algorithm(function, *args):
    stats = {"nodes": 0, "cutoffs": 0}

    start = time.perf_counter()
    result = function(*args, stats)
    elapsed = time.perf_counter() - start

    return result, stats, elapsed


def main():
    DEPTH = 7
    WIDTH = 2
    SEED = 42

    rng = random.Random(SEED)
    root = build_tree(DEPTH, WIDTH, rng)

    # Часть листьев имеет одинаковое значение.
    make_equal_leaves(root, count=30, value=5)

    minimax_result, mm_stats, mm_time = run_algorithm(
        minimax, root, True
    )

    alpha_beta_result, ab_stats, ab_time = run_algorithm(
        alpha_beta, root, True, float("-inf"), float("inf")
    )

    assert minimax_result == alpha_beta_result, (
        "Результаты Minimax и Alpha-Beta должны совпадать."
    )

    saved = 0
    if mm_stats["nodes"]:
        saved = (1 - ab_stats["nodes"] / mm_stats["nodes"]) * 100

    print("=" * 55)
    print("МИНИ-МАКС И АЛЬФА-БЕТА ОТСЕЧЕНИЕ")
    print("=" * 55)
    print(f"Глубина дерева: {DEPTH}")
    print(f"Ширина дерева: {WIDTH}")
    print(f"Количество листьев: {WIDTH ** DEPTH}")
    print(f"Seed генератора: {SEED}")
    print("Часть листьев имеет одинаковое значение: 5")
    print()

    print("Обычный Minimax:")
    print(f"  Результат: {minimax_result}")
    print(f"  Проверено узлов: {mm_stats['nodes']}")
    print(f"  Время: {mm_time:.8f} сек")
    print()

    print("Minimax с Alpha-Beta:")
    print(f"  Результат: {alpha_beta_result}")
    print(f"  Проверено узлов: {ab_stats['nodes']}")
    print(f"  Отсечений: {ab_stats['cutoffs']}")
    print(f"  Время: {ab_time:.8f} сек")
    print()

    print(f"Сокращение количества проверенных узлов: {saved:.2f}%")
    print(f"Результаты совпадают: {minimax_result == alpha_beta_result}")


if __name__ == "__main__":
    main()
