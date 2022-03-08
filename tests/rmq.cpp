#include <rmq.hpp>
#include <vector>
#include <iostream>

int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  int n, q;
  std::cin >> n >> q;
  std::vector<long long> a(n);
  for (long long &x : a)
    std::cin >> x;

  RMQ rmq(a);

  for (int qq = 0; qq < q; ++qq) {
    int i, j;
    std::cin >> i >> j;
    --i, --j;
    std::cout << rmq(i, j) << '\n';
  }
}
