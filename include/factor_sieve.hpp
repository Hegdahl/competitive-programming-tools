#pragma once

#include <vector>

template<int N>
struct FactorSieve {
  static constexpr int max_primes = int(1.6 * N / (int)std::__lg(N+1))+ 10;
  static int smallest_factor[N+1];
  static int primes[max_primes+1];
  int prime_cnt = 0;

  constexpr FactorSieve(int) {
    for (int i=2; i <= N; ++i) {
      if (smallest_factor[i] == 0) {
        smallest_factor[i] = i;
        primes[prime_cnt++] = i;
      }
      for (int j=0; j < prime_cnt && primes[j] <= smallest_factor[i] && i*primes[j] <= N; ++j)
        smallest_factor[i * primes[j]] = primes[j];
    }
  }

  FactorSieve() : FactorSieve(0) {}

  std::vector<int> factor(int x) {
    std::vector<int> res;
    while (x > 1) {
      res.push_back(smallest_factor[x]);
      x /= res.back();
    }
    return res;
  }
};

template<int N>
int FactorSieve<N>::smallest_factor[N+1];
template<int N>
int FactorSieve<N>::primes[FactorSieve<N>::max_primes+1];
