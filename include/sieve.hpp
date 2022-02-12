#pragma once

#include <algorithm>
#include <cmath>
#include <vector>

template<int N>
struct Sieve {
  static constexpr int sqrt = std::ceil(std::sqrt(N+1));
  std::vector<int> primes;

  Sieve() {
    primes.clear();

    char is_composite[sqrt]{};

    for (int i = 2; i < sqrt; ++i) {
      if (is_composite[i]) {
        is_composite[i] = false;
        continue;
      }
      primes.push_back(i);
      for (int j = 2*i; j < sqrt; j += i)
        is_composite[j] = true;
    }

    std::vector<int> small_primes = primes;

    for (int start = sqrt; start <= N; start += sqrt) {
      int stop = std::min(start+sqrt, N+1);

      for (int p : small_primes) {
        for (int i = (start+p-1)/p*p; i < stop; i += p)
          is_composite[i-start] = true;
      }

      for (int i = start; i < stop; ++i)
        if (!is_composite[i-start])
          primes.push_back(i);
        else
          is_composite[i-start] = false;
    }
  }

  int next_prime(int x) {
    auto it = std::upper_bound(primes.begin(), primes.end(), x);
    if (it == primes.end()) return -1;
    return *it;
  }

  int prev_prime(int x) {
    auto it = std::lower_bound(primes.begin(), primes.end(), x);
    if (it == primes.begin()) return -1;
    return *--it;
  }

  bool is_prime(int x) {
    return next_prime(x-1) == x;
  }
};
