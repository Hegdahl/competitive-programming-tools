#include <bits/stdc++.h>

using namespace std;
using ll = long long;

/*BEGIN_SNIPPET*/
template<typename T>
struct modnum {
  using Int = typename T::type;
  using Int2 = typename T::prod_type;
  Int val;

  modnum() = default;
  modnum(const Int &_val) : val((_val%T::MOD+T::MOD)%T::MOD) {}

  modnum &operator++() { if (++val == T::MOD) val = 0; return *this; }
  modnum &operator--() { if (val-- == 0) val += T::MOD; return *this; }
  modnum &operator++(int) { auto ret = *this; ++*this; return ret; }
  modnum &operator--(int) { auto ret = *this; --*this; return ret; }

  modnum &operator+=(const modnum &o) { if ((val += o.val) >= T::MOD) val -= T::MOD; return *this; }
  modnum &operator-=(const modnum &o) { if ((val -= o.val) < 0) val += T::MOD; return *this; }
  modnum &operator*=(const modnum &o) { val = Int((Int2)val*o.val%T::MOD); return *this; }
  modnum &operator/=(const modnum &o) { *this *= o.inv(); return *this; }

  friend modnum operator+(const modnum &a, const modnum &b) { auto ret = a; return ret += b; }
  friend modnum operator-(const modnum &a, const modnum &b) { auto ret = a; return ret -= b; }
  friend modnum operator*(const modnum &a, const modnum &b) { auto ret = a; return ret *= b; }
  friend modnum operator/(const modnum &a, const modnum &b) { auto ret = a; return ret /= b; }

  friend bool operator==(const modnum &a, const modnum &b) { return a.val == b.val; }
  friend bool operator!=(const modnum &a, const modnum &b) { return a.val != b.val; }

  modnum pow(ll e) const {
    modnum b = *this, a = 1;
    while (e) {
      if (e&1) a *= b;
      b *= b;
      e >>= 1;
    }
    return a;
  }

  modnum inv() const { return pow(T::MOD-2); }

  friend istream &operator>>(istream &is, modnum &x) { Int v; is >> v; x = v; return is; }
  friend ostream &operator<<(ostream &os, const modnum &x) { return os << x.val; }
};

struct _static_mod_t {
  using type = int;
  using prod_type = ll;
  static constexpr type MOD = 1'000'000'007;
};

struct _var_mod_t {
  using type = int;
  using prod_type = ll;
  static type MOD;
};
typename _var_mod_t::type _var_mod_t::MOD = 1;
//typename _var_mod_t::type &MOD = _var_mod_t::MOD;

using mint = modnum<_static_mod_t>;
/*END_SNIPPET*/

int main() {
  using namespace chrono;
  auto START = high_resolution_clock::now();

  mint res = 0;
  for(auto rep = 0; rep < 5'000'000'0; ++ rep){
    res += mint(1) / 2;
  }

  cout << duration<double>(high_resolution_clock::now() - START).count() << "\n";
  cout << res << "\n";
  START = high_resolution_clock::now();

  res = 0;
  for(auto rep = 0; rep < 5'000'000'0; ++ rep){
    res += mint(2)._inverse_egcd();
  }

  cout << duration<double>(high_resolution_clock::now() - START).count() << "\n";
  cout << res << "\n";

  mint v = 1;
  for (int i = 0; i < 1e7; ++i) {
    v *= 2;
    assert(v/v == 1);
  }
  cout << "ok\n";

  cout << (4_M == 4) << '\n';
  cout << (4 == 4_M) << '\n';
  cout << (4_M == 3) << '\n';
  cout << (4 == 4_M) << '\n';
  cout << (-4 == -4_M) << '\n';
  cout << (-4 == +4_M) << '\n';
  cout << (+4 == -4_M) << '\n';
}
