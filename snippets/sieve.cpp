#pragma GCC optimize("Ofast,unroll-loops")
#pragma GCC target("avx,avx2,sse,sse2,ssse3,sse4,mmx,popcnt")
#include <bits/stdc++.h>
#define ar array

using namespace std;
using ll = long long;

/*BEGIN_SNIPPET*/
template<int N>
struct Sieve {
  using W = uint64_t;
  static constexpr int WBITS = sizeof(W)*8;
  static constexpr int SQRT = (int)sqrt(N);
  static constexpr int BSQRT = SQRT/WBITS;
  static constexpr int SHIFT = __lg(WBITS);
  static constexpr int MASK = WBITS-1;

  vector<int> primes;
  
  W blocks[(N+WBITS)/WBITS];

  Sieve() {
    primes.reserve(int(1.2 * N / log(N-1)));

    memset(blocks, -1, sizeof(blocks));
    blocks[0] &= ~(W(1)<<0);
    blocks[0] &= ~(W(1)<<1);

    for (int block = 0; block <= BSQRT; ++block) {
      while (blocks[block]) {
        int p = __builtin_ctzll(blocks[block])
          + (block * 64);
        primes.push_back(p);
        blocks[block] ^= W(1) << p;
        for (int m = p*p; m < N; m += p) {
          int b = m >> SHIFT;
          int o = m & MASK;
          blocks[b] &= ~(W(1)<<o);
        }
      }
    }

    for (int block = BSQRT+1; block < (int)(sizeof(blocks)/sizeof(W)); ++block) {
      while (blocks[block]) {
        int p = __builtin_ctzll(blocks[block])
          + (block * 64);
        if (p >= N) break;
        primes.push_back(p);
        blocks[block] ^= W(1) << p;
      }
    }
  }
};
Sieve<int(5e8)> sieve;
/*END_SNIPPET*/

int main() {
  cin.tie(0)->sync_with_stdio(0);

  int N, A, B;
  cin >> N >> A >> B;
  auto it = upper_bound(sieve.primes.begin(), sieve.primes.end(), N);
  int cnt = int(it-sieve.primes.begin());

  vector<int> ans;
  for (int i = B; i < cnt; i += A)
    ans.push_back(sieve.primes[i]);

  cout << cnt << ' ' << ans.size() << '\n';
  for (int p : ans)
    cout << p << ' ';
  cout << '\n';
}
