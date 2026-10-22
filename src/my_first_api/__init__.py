def main() -> None:
    print("Hello from my-first-api!")


def fib2(n):  # 返回斐波那契数组直到 n
    """Return a list containing
    the Fibonacci series
     up to n."""
    result = []
    a, b = 0, 1
    while a < n:
        result.append(a)  # 见下
        a, b = b, a + b
    return result


if __name__ == "__main__":
    help(fib2)