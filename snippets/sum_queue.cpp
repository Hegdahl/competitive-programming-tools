#include <algorithm>
#include <iostream>
#include <utility>
#include <vector>

/*BEGIN_SNIPPET*/
template<class T, class Op>
struct sum_stack {

  const Op &op_;
  std::vector<std::pair<T, T>> data;

  sum_stack(const T &identity, const Op &op)
    : op_(op), data{std::make_pair(identity, identity)} {}

  void push(const T &x) {
    data.push_back(std::make_pair(x, op_(data.back().second, x)));
  }

  T pop() {
    T last = std::move(data.back().first);
    data.pop_back();
    return last;
  }

  T query() const {
    return data.back().second;
  }

  int size() const {
    return (int)data.size() - 1;
  }

};

template<class T, class Op>
struct sum_queue {

  const Op &op_;
  sum_stack<T, Op> in, out;

  sum_queue(const T &identity, const Op &op)
    : op_(op), in(identity, op), out(identity, op) {}

  void push(const T &x) {
    in.push(x);
  }

  void pop() {
    shift();
    out.pop();
  }

  T query() {
    return op_(in.query(), out.query());
  }

  int size() const {
    return in.size() + out.size();
  }

  void shift() {
    if (out.size()) return;

    while (in.size())
      out.push(in.pop());
  }

};
/*END_SNIPPET*/

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
      sum_queue vals(INF, [](int a, int b) { return std::min(a, b); });
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
