#include <tensor.hpp>

#include <iostream>
#include <string>

int main() {
  auto x = make_tensor(std::string("abc"), 2, 3);

  for (int i = 0; i < 2; ++i)
    for (int j = 0; j < 3; ++j)
      x(i, j) = std::to_string(i) + '_' + std::to_string(j);

  for (int i = 0; i < 2; ++i) {
    for (int j = 0; j < 3; ++j)
      std::cerr << x(i, j) << ' ';
    std::cerr << '\n';
  }
}
