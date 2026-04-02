"""One-shot generator for submissions/*/main.c — run from repo: python build_fixture_sources.py then remove if desired."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent / "submissions"


def helpers_c() -> str:
    parts: list[str] = []
    for hi in range(1, 21):
        mult = hi
        mod = hi + 3
        parts.append(
            f"""
static int helper{hi}(int ax) {{
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {{
    asum += (ai * {mult}) % ({mod});
  }}
  return asum;
}}"""
        )
    return "".join(parts)


H = helpers_c()

ALICE = f"""#include <stdio.h>

#define N 40

static int sum_even(const int *values) {{
  int total = 0;
  for (int i = 0; i < N; i++) {{
    if (values[i] % 2 == 0) {{
      total += values[i];
    }}
  }}
  return total;
}}

static int weighted(const int *values) {{
  int total = 0;
  for (int i = 0; i < N; i++) {{
    total += values[i] * (i + 1);
  }}
  return total;
}}

static int *rotate_left(int *values) {{
  if (N == 0) return values;
  int first = values[0];
  for (int i = 0; i < N - 1; i++) {{
    values[i] = values[i + 1];
  }}
  values[N - 1] = first;
  return values;
}}
{H}

int main(void) {{
  int values[N];
  for (int i = 0; i < N; i++) {{
    values[i] = (i * 3 + 7) % 19;
  }}
  int total = sum_even(values);
  int w = weighted(values);
  int *rotated = rotate_left(values);
  printf("%d\\n", total + w + rotated[0]);
  return 0;
}}
"""

BOB = f"""#include <stdio.h>

#define N 40

static int sum_even_terms(const int *dataset) {{
  int accumulator = 0;
  for (int i = 0; i < N; i++) {{
    if (dataset[i] % 2 == 0) {{
      accumulator += dataset[i];
    }}
  }}
  return accumulator;
}}

static int weighted_score(const int *dataset) {{
  int accumulator = 0;
  for (int i = 0; i < N; i++) {{
    accumulator += dataset[i] * (i + 1);
  }}
  return accumulator;
}}

static int *shift_left(int *dataset) {{
  if (N == 0) return dataset;
  int first = dataset[0];
  for (int i = 0; i < N - 1; i++) {{
    dataset[i] = dataset[i + 1];
  }}
  dataset[N - 1] = first;
  return dataset;
}}
{H}

int main(void) {{
  int dataset[N];
  for (int i = 0; i < N; i++) {{
    dataset[i] = (i * 3 + 7) % 19;
  }}
  int accumulator = sum_even_terms(dataset);
  int w = weighted_score(dataset);
  int *shift_leftd = shift_left(dataset);
  printf("%d\\n", accumulator + w + shift_leftd[0]);
  return 0;
}}
"""


def carol_c() -> str:
    seqs: list[str] = []
    for n in range(1, 45):
        lim = 5 + n
        seqs.append(
            f"""
static int sequence{n}(int x) {{
  int value = x;
  for (int i = 0; i < {lim}; i++) {{
    value = (value * 33 + i + 0) % 920;
  }}
  return value;
}}"""
        )
    seq_block = "".join(seqs)
    body = f"""#include <stdio.h>

static int gcd(int a, int b) {{
  while (b != 0) {{
    int t = b;
    b = a % b;
    a = t;
  }}
  return a;
}}

static int lcm(int a, int b) {{
  return (a / gcd(a, b)) * b;
}}
{seq_block}

int main(void) {{
  int output = 0;
  for (int i = 1; i < 50; i++) {{
    output += sequence1(i) + sequence2(i);
  }}
  printf("%d\\n", output + lcm(88, 36));
  return 0;
}}
"""
    return body


def main() -> None:
    for name, content in (
        ("Alice", ALICE),
        ("Bob", BOB),
        ("Carol", carol_c()),
    ):
        d = ROOT / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "main.c").write_text(content, encoding="utf-8")
    print("Wrote", ROOT / "Alice" / "main.c", "etc.")


if __name__ == "__main__":
    main()
