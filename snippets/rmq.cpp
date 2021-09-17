#include <bits/stdc++.h>
#define ar array

using namespace std;
using ll = long long;

/*BEGIN_SNIPPET*/
template<class T, class Cmp>
struct RMQ {
  static constexpr int MAX_LENGTH = 1e6;

  int n, lvls;
  T identity;

  vector<T> data[__lg(MAX_LENGTH)+1];

  RMQ(int n_, const T &identity_)
    : n(n_), identity(identity_) {
    for (lvls = 0; n - (1<<lvls) + 1 > 0; ++lvls)
      data[lvls].resize(n - (1<<lvls) + 1, identity);
  }

  auto begin() { return data[0].begin(); }
  auto end() { return data[0].end(); }

  T &operator[](int i) {
    return data[0][i];
  }

  void build() {
    for (int lvl = 0; lvl < lvls-1; ++lvl) {
      int w = 1<<lvl;
      for (int i = 0; i+2*w <= n; ++i)
        data[lvl+1][i] = pick(data[lvl][i], data[lvl][i+w]);
    }
  }

  T operator()(int i, int j) {
    if (i > j) return identity;
    i = max(i, 0);
    j = min(j, n-1);
    int w = j-i+1;
    int lvl = __lg(w);
    w = 1<<lvl;
    return pick(data[lvl][i], data[lvl][j-w+1]);
  }

  static T pick(const T &a, const T &b) {
    return Cmp{}(a, b) ? a : b;
  }

};

template<class T = ll>
struct RMinQ : public RMQ<T, less<T>> {
  RMinQ(int n_) : RMQ<T, less<T>>(n_, numeric_limits<T>::max()) {}
  RMinQ(int n_, const T &identity_) : RMQ<T, less<T>>(n_, identity_) {}
};
template<class T = ll>
struct RMaxQ : public RMQ<T, greater<T>> {
  RMaxQ(int n_) : RMQ<T, greater<T>>(n_, numeric_limits<T>::min()) {}
  RMaxQ(int n_, const T &identity_) : RMQ<T, greater<T>>(n_, identity_) {}
};
/*END_SNIPPET*/

int main() {
  cin.tie(0)->sync_with_stdio(0);

  int n, q; cin >> n >> q;
  RMinQ<int> rmq(n);
  for (int &x : rmq)
    cin >> x;
  rmq.build();

  for (int qq = 0; qq < q; ++qq) {
    int i, j;
    cin >> i >> j;
    --i, --j;
    cout << rmq(i, j) << '\n';
  }
}
