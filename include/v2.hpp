#pragma once

#include <cmath>
#include <numeric>
 
template<class T = long long>
struct V2 {
  T x, y;
 
  constexpr friend V2 operator+(const V2 &a, const V2 &b) {
    return {a.x + b.x, a.y + b.y};
  }
 
  constexpr friend V2 operator-(const V2 &a, const V2 &b) {
    return {a.x - b.x, a.y - b.y};
  }
 
  constexpr V2 &operator+=(const V2 &o) {
    return *this = *this + o;
  }
  constexpr V2 &operator-=(const V2 &o) {
    return *this = *this - o;
  }
 
  constexpr V2 operator+() const {
    return {+x, +y};
  }
  constexpr V2 operator-() const {
    return {-x, -y};
  }
 
  constexpr V2 discrete_normalized() const {
    if (x == 0 && y == 0) return {0, 0};
    T f = std::gcd(std::abs(x), std::abs(y));
    return {x/f, y/f};
  }
 
  constexpr friend T cross(const V2 &a, const V2 &b) {
    return a.x * b.y - a.y * b.x;
  }

  constexpr T centered_cross(const V2 &a, const V2 &b) const {
    return cross(a-*this, b-*this);
  }
 
  constexpr friend T dot(const V2 &a, const V2 &b) {
    return a.x * b.x + a.y * b.y;
  }
  
  constexpr T mag2() const {
    return x*x + y*y;
  }

  constexpr T mag() const {
    return std::sqrt(mag2());
  }
 
  constexpr int quadrant() const {
    //        ^ +y
    //      1 | 0
    // -x --- -1 ---> +x
    //      2 | 3
    //        | -y
    if (x > 0 && y >= 0) return 0;
    if (y > 0 && x <= 0) return 1;
    if (x < 0 && y <= 0) return 2;
    if (y < 0 && x >= 0) return 3;
    return -1;
  }
 
  constexpr friend V2 rot90(const V2 &v) {
    return {-v.y, v.x};
  }
 
  constexpr friend V2 rotate_to_quadrant_0(const V2 &v) {
    if (v.x == 0 && v.y == 0) return {0, 0};
    if (v.quadrant() == 0) return v;
    return rotate_to_quadrant_0(rot90(v));
  }
 
  constexpr friend bool operator<(V2 a, V2 b) {
    int aq = a.quadrant();
    int bq = b.quadrant();
    if (aq != bq) return aq < bq;
    a = rotate_to_quadrant_0(a);
    b = rotate_to_quadrant_0(b);
    return a.y * b.x < b.y * a.x;
  }
 
  constexpr friend bool operator==(const V2 &a, const V2 &b) {
    return a.x == b.x && a.y == b.y;
  }
 
  constexpr friend bool operator!=(const V2 &a, const V2 &b) {
    return a.x != b.x || a.y != b.y;
  }
 
  template<class OStream>
  friend OStream &operator<<(OStream &os, const V2 &v) {
    return os << '(' << v.x << ',' << v.y << ')';
  }

  template<class IStream>
  friend IStream &operator>>(IStream &is, V2 &v) {
    return is >> v.x >> v.y;
  }

};
