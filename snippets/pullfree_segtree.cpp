#include <algorithm>
#include <cassert>
#include <iostream>
#include <vector>

/*BEGIN_SNIPPET*/
template<class V>
struct PullFreeSegTree {
  
  const int n, offset;
  std::vector<V> values;

  PullFreeSegTree(int n_) : n(n_), offset(2<<std::__lg((n-1)|1)), values(2*offset) {}

  template<class F>
  void operator()(int i, int j, F &&f) {
    for (i += offset-1, j += offset+1; i+1 < j; i /= 2, j /= 2) {
      if (i%2 == 0) f(values[i+1]);
      if (j%2 == 1) f(values[j-1]);
    }
  }

  template<class F>
  void operator()(int i, F &&f) {
    for (i += offset; i; i /= 2)
      f(values[i]);
  }

};
/*END_SNIPPET*/

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
