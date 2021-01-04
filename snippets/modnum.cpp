#include <bits/stdc++.h>

using namespace std;
using ll = long long;
using lll = __int128;

/*BEGIN_SNIPPET*/
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

  modnum operator+(const modnum &o) const { modnum r = *this; r += o; return r; }
  modnum operator-(const modnum &o) const { modnum r = *this; r -= o; return r; }
  modnum operator*(const modnum &o) const { modnum r = *this; r *= o; return r; }
  modnum operator/(const modnum &o) const { modnum r = *this; r /= o; return r; }

//#define USE_EGCD
#ifdef USE_EGCD
  modnum inverse() const {
    Int pr = v, r = MOD;
    Int ps = 1, s = 0;
    while (r) {
      Int q = pr/r;
      pr -= q*r; swap(r, pr);
      ps -= q*s; swap(s, ps);
    }
    return ps;
  }
#else
  modnum inverse() const {
    modnum a(1);
    Int e = MOD-2;
    modnum b = *this;
    while (e) {
      if (e&1) a *= b;
      b *= b;
      e >>= 1;
    }
    return a;
  }
#endif

  bool operator==(const modnum &o) const { return v == o.v; }
  bool operator!=(const modnum &o) const { return v != o.v; }

  explicit operator Int() const { return v; }

  friend ostream &operator<<(ostream &os, const modnum x) { return os << x.v; }
  friend ostream &operator>>(ostream &os, modnum &x) { Int v; os >> v; x = modnum(v); return os; }
};
using mint = modnum<ll, ll(1e9)+7>;
//using mint = modnum<ll, (1LL<<23)*7*17+1>;
/*END_SNIPPET*/

int main() {
  const int N = 1e7;

  mint v(1);
  for (int i = 0; i < N; ++i) {
    v *= 2;
    assert(v/v == 1);
  }
}
