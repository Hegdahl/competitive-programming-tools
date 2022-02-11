#pragma once

#include <flow.hpp>

#include <array>

struct BipartiteMatcher {
  int n, m;
  Flow<int> flow;
  BipartiteMatcher(int n_, int m_) : n(n_), m(m_), flow(2+n+m) {
    for (int i = 0; i < n; ++i)
      flow.connect(0, i+1, 1);
    for (int j = 0; j < m; ++j)
      flow.connect(j+1+n, 1+n+m, 1);
  }

  void connect(int i, int j) {
    flow.connect(i+1, j+1+n, 1);
  }

  int solve() {
    return (int)flow.solve();
  }

  std::vector<std::array<int, 2>> get_matched() {
    solve();
    std::vector<std::array<int, 2>> res;
    for (int i = 0; i < n; ++i) {
      for (auto &e : flow.graph[i+1]) {
        if (e.remain) continue;
        if (e.to < 1+n) continue;
        if (e.to >= 1+n+m) continue;
        res.push_back({i, e.to-1-n});
      }
    }
    return res;
  }
};
