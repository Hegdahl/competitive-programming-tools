// https://judge.yosupo.jp/problem/enumerate_primes
#include <sieve.hpp>

#include <algorithm>
#include <iostream>

Sieve<int(5e8)> sieve;

int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  int N, A, B;
  std::cin >> N >> A >> B;
  auto it = std::upper_bound(
    sieve.primes.begin(),
    sieve.primes.end(),
    N
  );

  int cnt = int(it-sieve.primes.begin());

  std::vector<int> ans;
  for (int i = B; i < cnt; i += A)
    ans.push_back(sieve.primes[i]);

  std::cout << cnt << ' ' << ans.size() << '\n';
  for (int p : ans)
    std::cout << p << ' ';
  std::cout << '\n';
}
