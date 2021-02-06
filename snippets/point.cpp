#include <bits/stdc++.h>

using namespace std;
using ll = long long;
using ld = long double;

/*BEGIN_SNIPPET*/
struct Point {
  ll x, y;
  Point() : x(0), y(0) {}
  Point(ll x, ll y) : x(x), y(y) {}

  Point &operator+=(const Point &o) { x += o.x, y += o.y; return *this; }
  Point &operator-=(const Point &o) { x -= o.x, y -= o.y; return *this; }
  Point operator+(const Point &o) const { Point r = *this; r += o; return r; }
  Point operator-(const Point &o) const { Point r = *this; r -= o; return r; }

  friend bool operator==(const Point &a, const Point &b) { return a.x==b.x && a.y==b.y; }
  friend bool operator!=(const Point &a, const Point &b) { return a.x!=b.x && a.y!=b.y; }

  friend ll cross(const Point &a, const Point &b) { return a.x*b.y - b.x*a.y; }
  friend ll dot(const Point &a, const Point &b) { return a.x*b.x + b.y*a.y; }
  ll curl(const Point &a, const Point &b) const { return cross(a-*this, b-*this); }

  ll mag_sq() const { return x*x + y*y; }
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
  // TODO: make tests
}
