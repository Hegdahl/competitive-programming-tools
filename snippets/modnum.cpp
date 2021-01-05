#include <bits/stdc++.h>

using namespace std;
using ll = long long;
using lll = __int128;

/*BEGIN_SNIPPET*/
#define INVERSE_CUTOFF int(1e6)
//#define USE_EGCD
template<typename Int, Int MOD>struct modnum {
  Int v;
  modnum() : v(0) {}
  modnum(Int v) : v(v>=MOD?v%MOD:v<0?v%MOD+MOD:v) {}

  modnum &operator++() { if (++v == MOD) v = 0; return *this; }
  modnum &operator--() { if (v == 0) v = MOD; --v; return *this; }
  modnum operator++(int) { modnum r = *this; ++*this; return r; }
  modnum operator--(int) { modnum r = *this; --*this; return r; }

  modnum &operator+=(const modnum &o) { v -= MOD-o.v; if (v<0) v += MOD; return *this; }
  modnum &operator-=(const modnum &o) { v -= o.v; if (v<0) v += MOD; return *this; }
  modnum &operator*=(const modnum &o) { v *= o.v; if (v>=MOD) v %= MOD; return *this; }
  modnum &operator/=(const modnum &o) { *this *= o.inverse(); return *this; }

  friend modnum operator+(modnum l, const modnum &r) { return l += r; }
  friend modnum operator-(modnum l, const modnum &r) { return l -= r; }
  friend modnum operator*(modnum l, const modnum &r) { return l *= r; }
  friend modnum operator/(modnum l, const modnum &r) { return l /= r; }

  modnum pow(Int e) const {
    modnum ans = 1, base = v;
    while (e) {
      if (e&1) ans *= base;
      base *= base;
      e >>= 1;
    }
    return ans;
  }

  static vector<modnum> _inverses;
  static auto _init_inverses() {
    vector<modnum> inv(INVERSE_CUTOFF);
    inv[1] = 1;
    for (int i = 2; i <= INVERSE_CUTOFF; ++i)
      inv[i] = MOD - (MOD/i) * inv[MOD%i];
    return inv;
  }
  auto inverse() const {
    if (v <= INVERSE_CUTOFF) return _inverses[v];
    return _inverse();
  }

#ifdef USE_EGCD
  modnum _inverse() const {
#else
  modnum _inverse_egcd() const {
#endif
    Int pr = v, r = MOD;
    Int ps = 1, s = 0;
    while (r) {
      Int q = pr/r;
      pr -= q*r; swap(r, pr);
      ps -= q*s; swap(s, ps);
    }
    return ps;
  }
#ifndef USE_EGCD
  modnum _inverse() const {
#else
  modnum _inverse_bexp() const {
#endif
    return pow(MOD-2);
  }

  friend bool operator==(const modnum &l, const modnum &r) { return l.v == r.v; }
  friend bool operator!=(const modnum &l, const modnum &r) { return l.v != r.v; }

  explicit operator Int() const { return v; }

  friend ostream &operator<<(ostream &os, const modnum x) { return os << x.v; }
  friend ostream &operator>>(ostream &os, modnum &x) { Int v; os >> v; x = modnum(v); return os; }
};
using mint = modnum<ll, ll(1e9)+7>;
//using mint = modnum<ll, (1LL<<23)*7*17+1>;
template<> vector<mint> mint::_inverses = mint::_init_inverses();
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

  cout << (mint(4) == 4) << '\n';
  cout << (4 == mint(4)) << '\n';
  cout << (mint(4) == 3) << '\n';
  cout << (4 == mint(3)) << '\n';
}
