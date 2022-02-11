// https://codeforces.com/contest/939/problem/F
#include <sum_queue.hpp>

#include <array>
#include <iostream>
#include <vector>

void set_min(int &place, int v) {
  if (v < place) place = v;
}

constexpr int INF = 1e9;

int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  int n, k;
  std::cin >> n >> k;
  const int S = 2 * n + 1;

  std::array<std::vector<int>, 2> dp {
    std::vector<int>(S, INF),
    std::vector<int>(S, INF),
  };

  std::array<std::vector<int>, 2> ndp {
    std::vector<int>(S, INF),
    std::vector<int>(S, INF),
  };

  dp[1][0] = 0;

  auto advance = [&](int len) {
    for (int i = S - 1; i - len >= 0; i--)
      dp[1][i] = dp[1][i - len];
    for (int i = 0; i < len; i++)
      dp[1][i] = INF;
  };

  auto update = [&](int len) {
    for (int i = 0; i < S; i++)
      ndp[0][i] = dp[0][i];
    for (int i = S - 1; i - len >= 0; i--)
      ndp[1][i] = dp[1][i - len];
    for (int i = 0; i < len; i++)
      ndp[1][i] = INF;

    for (int b = 0; b <= 1; b++) {
      SumQueue vals(INF, [](int x, int y) { return std::min(x, y); });
      for (int i = 0; i < S; i++) {
        vals.push(1 + dp[1 ^ b][i]);
        vals.push(2 + dp[b][i]);

        if (i - len - 1 >= 0) {
          vals.pop();
          vals.pop();
        }

        set_min(ndp[b][i], vals.query());
      }
    }

    std::swap(dp, ndp);
  };

  int t = 0;
  for (int i = 0; i < k; i++) {
    int l, r;
    std::cin >> l >> r;

    advance(l - t);
    t = l;
    update(r - t);
    t = r;
  }
  advance(2 * n - t);

  int ans = std::min(dp[0][n], dp[1][n]);
  if (ans == INF)
    std::cout << "Hungry\n";
  else
    std::cout << "Full\n" << ans << '\n';
}
