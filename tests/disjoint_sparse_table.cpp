// https://atcoder.jp/contests/arc126/tasks/arc126_c

#include <disjoint_sparse_table.hpp>

#include <algorithm>
#include <iostream>
#include <numeric>
#include <vector>

struct S {
  long long cnt = 0, sum = 0, width = 0;

  void pull(S l, S r) {
    cnt = l.cnt + r.cnt;
    sum = l.sum + r.sum + l.cnt * r.width;
    width = l.width + r.width;
  }
};

int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  int n;
  long long k;
  std::cin >> n >> k;
  std::vector<int> a(n);
  for (int &x : a)
    std::cin >> x;

  long long s = accumulate(a.begin(), a.end(), 0LL);
  int mx = *max_element(a.begin(), a.end());
  long long equalize_cost = (long long)mx*n - s;

  if (k >= equalize_cost) {
    std::cout << mx + (k-equalize_cost)/n << '\n';
    return 0;
  }

  std::vector<S> src(2*(mx+1), S{0,0,1});
  for (int x : a) ++src[x].cnt;
  DisjointSparseTable<S> dst(src);

  int ans;
  for (ans = mx-1; ans > 1; --ans) {
    long long cost = 0;
    for (int f = 0; f < mx; f += ans)
      cost += dst(f+1, f+ans).sum;
    if (cost <= k)
      break;
  }

  std::cout << ans << '\n';
}
