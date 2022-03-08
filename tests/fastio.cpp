#include <fastio.hpp>
#include <string>

int main() {
  std::string s;
  std::getline(std::cin, s);
  std::cout << s << '\n';

  __int128_t x;
  std::cin >> x;
  std::cout << -x << '\n';
}
