// https://open.kattis.com/problems/gondolas

#include "dcdp.hpp"

#include <algorithm>
#include <iostream>
#include <vector>

int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  int n, t, g;
  std::cin >> n >> t >> g;

  std::vector<int> a(n);
  for (int &x : a) {
    std::cin >> x;
    x %= 2*t;
  }
  std::sort(a.begin(), a.end());

  {
    std::vector<int> cpy = a;
    for (int &x : cpy)
      x += 2*t;
    a.insert(a.end(), cpy.begin(), cpy.end());
  }

  std::vector<int> pre(a.size()+1);
  for (int i = 0; i < (int)a.size(); ++i)
    pre[i+1] = pre[i] + a[i];

  int ans = 1e9;
  for (int offset = 0; offset < n; ++offset) {

    auto cost = [&](int i, int j){
      int sum = pre[j+1+offset] - pre[i+offset];
      return (j-i+1)*a[j+offset] - sum;
    };

    DivideAndConquerDP dcdp(cost);
    int here = dcdp.solve(n, g);
    ans = std::min(ans, here);
  }

  std::cout << ans << '\n';
}
// */
