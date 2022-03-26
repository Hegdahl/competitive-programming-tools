#pragma once

#include <algorithm>
#include <numeric>
#include <vector>

unsigned long long modmul(unsigned long long a,
                          unsigned long long b,
                          unsigned long long M) {
  long long ret = a * b - M * (unsigned long long)(1.L / M * a * b);
  return ret + M * (ret < 0) - M * (ret >= (long long)M);
}

unsigned long long modpow(unsigned long long b, unsigned long long e, unsigned long long mod) {
  unsigned long long ans = 1;
  for (; e; b = modmul(b, b, mod), e /= 2)
    if (e & 1) ans = modmul(ans, b, mod);
  return ans;
}

long long steps = 0;
bool isPrime(unsigned long long n) {
  if (n < 2 || n % 6 % 4 != 1) return (n | 1) == 3;
  unsigned long long A[] = {2, 325, 9375, 28178, 450775, 9780504, 1795265022},
                s = __builtin_ctzll(n-1), d = n >> s;
  for (unsigned long long a : A) {   // ^ count trailing zeroes
    unsigned long long p = modpow(a%n, d, n), i = s;
    while (p != 1 && p != n - 1 && a % n && i--)
      p = modmul(p, p, n), ++steps;
    if (p != n-1 && i != s) return 0;
  }
  return 1;
}

unsigned long long pollard(unsigned long long n) {
  auto f = [n](unsigned long long x) { return modmul(x, x, n) + 1; };
  unsigned long long x = 0, y = 0, t = 30, prd = 2, i = 1, q;
  while (t++ % 40 || std::gcd(prd, n) == 1) {
    ++steps;
    if (x == y) x = ++i, y = f(x);
    if ((q = modmul(prd, std::max(x,y) - std::min(x,y), n))) prd = q;
    x = f(x), y = f(f(y));
  }
  return std::gcd(prd, n);
}

std::vector<unsigned long long> factor(unsigned long long n) {
  if (n == 1) return {};
  if (isPrime(n)) return {n};
  unsigned long long x = pollard(n);
  auto l = factor(x), r = factor(n / x);
  l.insert(l.end(), r.begin(), r.end());
  return l;
}
