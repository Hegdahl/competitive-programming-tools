// https://cses.fi/problemset/task/1696/

#include "bipartite_matcher.hpp"

#include <array>
#include <iostream>
#include <vector>

int main() {
  std::cin.tie(0)->sync_with_stdio(0);
 
  int L, R, M;
  std::cin >> L >> R >> M;
  std::vector<std::array<int, 2>> e(M);
  for (auto &[i, j] : e)
    std::cin >> i >> j, --i, --j;
  sort(e.begin(), e.end());
  e.erase(unique(e.begin(), e.end()), e.end());
 
  BipartiteMatcher bm(L, R);
  for (auto [i, j] : e)
    bm.connect(i, j);
 
  auto res = bm.get_matched();
  std::cout << res.size() << '\n';
  for (auto [i, j] : res)
    std::cout << i+1 << ' ' << j+1 << '\n';
}
