#include <modnum.hpp>

#include <cassert>
#include <iostream>

using mint = static_mint<>;

int main() {
  mint v = 1;
  for (int i = 0; i < 1e7; ++i) {
    v *= 2;
    assert(v/v == 1);
  }
  std::cout << "ok\n";
}
