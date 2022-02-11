// https://codeforces.com/contest/552/problem/D

#include <v2.hpp>

#include <iostream>
#include <vector>
 
int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  int n;
  std::cin >> n;

  std::vector a(n, V2{}), b(n, V2{});
  for (auto &[x, y] : a)
    std::cin >> x >> y;

  sort(a.begin(), a.end(), [](auto u, auto v) {
    if (u.x != v.x) return u.x < v.x;
    return u.y < v.y;
  });

  long long ans = (long long)n*(n-1)*(n-2)/6;

  for (int i = 0; i+2 < n; ++i) {
    b.resize(n-i-1);
    for (int j = i+1; j < n; ++j)
      b[j-i-1] = a[j] - a[i];

    sort(b.begin(), b.end());

    /*
    std::cerr << "[";
    for (auto [x, y] : b)
      std::cerr << '(' << x << ',' << y << "),";
    std::cerr << "\b]\n";
    // */

    for (int j = 0, k = 0; j < (int)b.size(); j = k) {
      while (k < (int)b.size() && cross(b[j], b[k]) == 0) ++k;
      ans -= (k-j) * (k-j-1) / 2;
    }
  }

  std::cout << ans << '\n';
}

