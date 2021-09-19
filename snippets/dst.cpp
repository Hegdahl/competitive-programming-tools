#pragma GCC optimize("Ofast,unroll-loops")
#pragma GCC target("avx,avx2,sse,sse2,ssse3,sse4,mmx,fma,popcnt")
#include <bits/stdc++.h>
#define ar array

using namespace std;
using ll = long long;

/*BEGIN_SNIPPET*/
template<class S>
struct DisjointSparseTable {

  int n, height, width;
  vector<vector<S>> content;

  template<class Src>
  DisjointSparseTable(Src &&src)
  : n((int)src.size()), height(__lg(n-1)+1), width(1<<height),
    content{forward<Src>(src)} {

    content.resize(height);
    for (auto &row : content)
      row.resize(width);

    for (int lvl = 1; lvl < height; ++lvl) {
      int block_width = 2<<lvl;
      int offset = 1<<lvl;

      for (int start = 0; start < width; start += block_width) {
        int center = start+offset;
        int outside = start+block_width;

        content[lvl][center-1] = content[0][center-1];
        content[lvl][center] = content[0][center];

        for (int i = center-2; i >= start; --i)
          content[lvl][i].pull(content[0][i], content[lvl][i+1]);
        for (int i = center+1; i < outside; ++i)
          content[lvl][i].pull(content[lvl][i-1], content[0][i]);
      }

    }

  }

  S operator()(int i, int j) const {
    if (i > j) return {};
    assert(0 <= i);
    assert(j < n);

    if (i == j) return content[0][i];

    int lvl = __lg(i^j);
    S res;
    res.pull(content[lvl][i], content[lvl][j]);
    return res;
  }
};

struct S {
  ll cnt = 0, sum = 0, width = 0;

  void pull(S l, S r) {
    cnt = l.cnt + r.cnt;
    sum = l.sum + r.sum + l.cnt * r.width;
    width = l.width + r.width;
  }
};
/*END_SNIPPET*/

/* https://atcoder.jp/contests/arc126/tasks/arc126_c
int main() {
  cin.tie(0)->sync_with_stdio(0);

  int n; ll k;
  cin >> n >> k;
  vector<int> a(n);
  for (int &x : a) cin >> x;

  ll s = accumulate(a.begin(), a.end(), 0LL);
  int mx = *max_element(a.begin(), a.end());
  ll equalize_cost = (ll)mx*n - s;

  if (k >= equalize_cost) {
    cout << mx + (k-equalize_cost)/n << '\n';
    return 0;
  }


  vector<S> src(2*(mx+1), S{0,0,1});
  for (int x : a) ++src[x].cnt;
  DisjointSparseTable<S> dst(src);

  int ans;
  for (ans = mx-1; ans > 1; --ans) {
    ll cost = 0;

    for (int f = 0; f < mx; f += ans)
      cost += dst(f+1, f+ans).sum;

    if (cost <= k)
      break;
  }

  cout << ans << '\n';
} // */

//* https://cses.fi/problemset/view/1647/

struct SMin {
  ll v = 1LL<<60;

  void pull(SMin l, SMin r) {
    v = min(l.v, r.v);
  }
};

int main() {
  cin.tie(0)->sync_with_stdio(0);

  int n, q;
  cin >> n >> q;
  vector<SMin> src(n);
  for (SMin &s : src)
    cin >> s.v;

  DisjointSparseTable<SMin> dst(move(src));
  for (int qq = 0; qq < q; ++qq) {
    int i, j;
    cin >> i >> j;
    --i, --j;
    cout << dst(i, j).v << '\n';
  }
}
