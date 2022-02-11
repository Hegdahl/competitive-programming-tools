// https://judge.yosupo.jp/problem/segment_add_get_min

#include <lichao.hpp>

#include <cassert>
#include <iostream>
#include <limits>

struct X {
  long long v;
  X(long long v_) : v(v_) {}
  X(X a, X b) : v((a.v + b.v)/2) {}

  static X lo() { return {-int(1e9)}; }
  static X hi() { return {int(1e9)}; }

  friend bool operator<(const X &a, const X &b) {
    return a.v < b.v;
  }
};

struct F {
  int a = 0;
  long long b = std::numeric_limits<long long>::max();
  long long operator()(X x) {
    return (long long)a*x.v + b;
  }
};

int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  LiChao<F, X> lc;

  int n, q;
  std::cin >> n >> q;

  for (int i = 0; i < n; ++i) {
    int x0, xf, a;
    long long b;
    std::cin >> x0 >> xf >> a >> b;
    lc.update(F{a, b}, {x0}, {xf});
  }

  for (int qq = 0; qq < q; ++qq) {
    int t;
    std::cin >> t;
    if (t == 0) {
      int x0, xf, a;
      long long b;
      std::cin >> x0 >> xf >> a >> b;
      lc.update(F{a, b}, {x0}, {xf});
    } else if (t == 1) {
      int x;
      std::cin >> x;
      long long res = lc.query(x);
      if (res == std::numeric_limits<long long>::max())
        std::cout << "INFINITY\n";
      else
        std::cout << res << '\n';
    } else assert(0);
  }
}
