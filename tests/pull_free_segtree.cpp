#include <pull_free_segtree.hpp>

#include <iostream>
#include <cassert>

/* Solution for https://cses.fi/problemset/task/1648/
int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  int n, q;
  std::cin >> n >> q;

  std::vector<int> a(n);
  for (int &x : a)
    std::cin >> x;

  PullFreeSegTree<long long> st(n);
  for (int i = 0; i < n; ++i)
    st(i, [&](long long &x) { x += a[i]; });

  for (int qq = 0; qq < q; ++qq) {
    int t;
    std::cin >> t;
    if (t == 1) {
      int i, v;
      std::cin >> i >> v;
      --i;
      st(i, [&](long long &x) { x += v-a[i]; });
      a[i] = v;
    } else if (t == 2) {
      int i, j;
      std::cin >> i >> j;
      --i, --j;
      long long ans = 0;
      st(i, j, [&](long long x) { ans += x; });
      std::cout << ans << '\n';
    } else assert(0);
  }
}
// */

//* Solution for https://cses.fi/problemset/task/1651
int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  int n, q;
  std::cin >> n >> q;

  PullFreeSegTree<long long> st(n);
  for (int i = 0; i < n; ++i)
    std::cin >> st.values[st.offset+i];

  for (int qq = 0; qq < q; ++qq) {
    int t;
    std::cin >> t;
    if (t == 1) {
      int i, j, v;
      std::cin >> i >> j >> v;
      --i, --j;
      st(i, j, [=](long long &x) { x += v; });
    } else if (t == 2) {
      int i;
      std::cin >> i;
      --i;
      long long ans = 0;
      st(i, [&](long long x) { ans += x; });
      std::cout << ans << '\n';
    } else assert(0);
  }
}
// */
