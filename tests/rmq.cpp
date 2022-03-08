#pragma GCC optimize("Ofast,unroll-loops")

#define FAST_CIN_BUFFER_SIZE (int)(5e5*(10+14)+100)
#define FAST_COUT_BUFFER_SIZE (int)(5e5*10+100)
#include <fastio.hpp>
#include <rmq.hpp>
#include <vector>

int main() {
  int n, q;
  std::cin >> n >> q;
  std::vector<unsigned> a(n);
  for (unsigned &x : a)
    std::cin >> x;

  RMQ rmq(a);

  for (int qq = 0; qq < q; ++qq) {
    int i, j;
    std::cin >> i >> j;
    --i, --j;
    std::cout << rmq(i, j) << '\n';
  }
}
