#include <ufds.hpp>

#include <iostream>
#include <string>

int main() {
  std::cin.tie(0)->sync_with_stdio(0);
 
  int n, q;
  std::cin >> n >> q;

  UFDS ufds(n);
 
  for (int qq = 0; qq < q; ++qq) {
    std::string s;
    int i, j;
    std::cin >> s >> i >> j;
    --i, --j;

    if (s[0] == 'u') ufds.unite(i, j);
    else std::cout << (ufds.find(i)==ufds.find(j)? "YES" : "NO") << '\n';
  }
}
