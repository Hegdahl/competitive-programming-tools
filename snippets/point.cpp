#include <bits/stdc++.h>

using namespace std;
using ll = long long;
using ld = long double;

/*BEGIN_SNIPPET*/
template<class T = ll>
struct Point {
  T x, y;
  constexpr Point() : x(0), y(0) {}
  constexpr Point(T x_, T y_) : x(x_), y(y_) {}

  constexpr Point &operator+=(const Point &o) { x += o.x, y += o.y; return *this; }
  constexpr Point &operator-=(const Point &o) { x -= o.x, y -= o.y; return *this; }
  constexpr Point operator+(const Point &o) const { Point r = *this; r += o; return r; }
  constexpr Point operator-(const Point &o) const { Point r = *this; r -= o; return r; }

  constexpr friend bool operator==(const Point &a, const Point &b) { return a.x==b.x && a.y==b.y; }
  constexpr friend bool operator!=(const Point &a, const Point &b) { return a.x!=b.x || a.y!=b.y; }

  constexpr friend T cross(const Point &a, const Point &b) { return a.x*b.y - b.x*a.y; }
  constexpr friend T dot(const Point &a, const Point &b) { return a.x*b.x + b.y*a.y; }
  constexpr T curl(const Point &a, const Point &b) const { return cross(a-*this, b-*this); }

  T mag_sq() const { return x*x + y*y; }
  ld mag() const { return sqrt((ld)mag_sq()); }

  friend ostream &operator<<(ostream &os, const Point &p) { return os << p.x << ' ' << p.y; }
  friend istream &operator>>(istream &is, Point &p) { return is >> p.x >> p.y; }

  struct x_then_y { bool operator()(const Point &a, const Point &b) const {
      if (a.x != b.x) return a.x < b.x;
      return a.y < b.y;
  }};
  struct x_then_ry { bool operator()(const Point &a, const Point &b) const {
      if (a.x != b.x) return a.x < b.x;
      return a.y > b.y;
  }};
};
/*END_SNIPPET*/

int main() {
  static_assert(Point().curl(Point(1LL, 0LL), Point(0LL, 1LL)) == 1);
  static_assert(Point().curl(Point(0LL, 1LL), Point(1LL, 0LL)) == -1);
}
