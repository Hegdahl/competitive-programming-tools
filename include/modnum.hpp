#pragma once

template<typename T>
struct modnum {
  using Int = typename T::type;
  using Int2 = typename T::prod_type;
  Int val;

  modnum() = default;
  modnum(const Int2 &_val) : val(Int((_val%T::MOD+T::MOD)%T::MOD)) {}

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

  modnum pow(long long e) const {
    modnum b = *this, a = 1;
    while (e) {
      if (e&1) a *= b;
      b *= b;
      e >>= 1;
    }
    return a;
  }

  modnum inv() const { return pow(T::MOD-2); }

  template<class IStream>
  friend IStream &operator>>(IStream &is, modnum &x) { Int v; is >> v; x = v; return is; }
  template<class OStream>
  friend OStream &operator<<(OStream &os, const modnum &x) { return os << x.val; }
};

template<long long M>
struct static_mod_t {
  using type = int;
  using prod_type = long long;
  static constexpr type MOD = M;
};

template<int ID>
struct var_mod_t {
  using type = long long;
  using prod_type = __int128_t;
  static type MOD;
};
template<int ID>
typename var_mod_t<ID>::type var_mod_t<ID>::MOD = 1;

template<int MOD = (int)1e9+7>
using static_mint = modnum<static_mod_t<MOD>>;

template<int ID = 0>
using var_mint = modnum<var_mod_t<ID>>;
