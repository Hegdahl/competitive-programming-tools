#include <segtree.hpp>

#include <cassert>
#include <iostream>

struct S {
  long long s = 0;
  int w = 0;
  void pull(S l, S r) {
    s = l.s + r.s;
    w = l.w + r.w;
  }
};

struct F {
  bool assign = false;
  long long add = 0;
  void apply(F &f) {
    if (assign) f = *this;
    else f.add += add;
  }
  void apply(S &s) {
    if (assign) s.s = s.w * add;
    else s.s += s.w * add;
  }
};

int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  int n, q;
  std::cin >> n >> q;
  SegTree st(n, S{}, F{});

  static_assert(st.is_beats == false);

  {
    std::vector<S> init(n, {0, 1});
    for (S &s : init)
      std::cin >> s.s;
    st(0, n-1) = init;
  }

  for (int qq = 0; qq < q; ++qq) {
    int t, i, j;
    std::cin >> t >> i >> j;
    --i, --j;
    if (t == 1) {
      int x;
      std::cin >> x;
      st(i, j) *= {false, x};
    } else if (t == 2) {
      int x;
      std::cin >> x;
      st(i, j) *= {true, x};
    } else if (t == 3) {
      std::cout << st(i, j)->s << '\n';
    } else assert(0);
  }
}
