#include <bits/stdc++.h>

using namespace std;
using ll = long long;

/*BEGIN_SNIPPET*/
template<class S, class F>
struct SegTreeBase {
  
  vector<S> values;
  vector<F> queued;
  int lg2, offset;

  SegTreeBase(const vector<S> &src)
    : lg2(ceil(log2(src.size()))), offset(1<<(int)ceil(log2(src.size()))) {
    values.reserve(2*offset);
    values.resize(offset);
    values.insert(values.end(), src.begin(), src.end());
    values.resize(2*offset);
    queued.resize(offset);
    for (int i = offset-1; i > 0; --i)
      values[i] = values[2*i] * values[2*i+1];
  }

  void push(int I) {
    assert(I > 0 && I < offset);
    values[2*I] = queued[I] * values[2*I];
    values[2*I+1] = queued[I] * values[2*I+1];
    if (2*I < offset) {
      queued[2*I] = queued[I] * queued[2*I];
      queued[2*I+1] = queued[I] * queued[2*I+1];
    }
    queued[I] = F();
  }

  void push_col(int I) {
    assert(I >= offset && I < 2*offset);
    for (int lvl = lg2-1; lvl >= 0; --lvl)
      push((I>>lvl)/2);
  }

  void push_range(int I, int J) {
    assert(I+1 >= offset && I+1 < 2*offset);
    assert(J-1 >= offset && J-1 < 2*offset);
    assert(I < J);
    for (int lvl = lg2-1; lvl >= 0; --lvl) {
      int i = I>>lvl, j = J>>lvl;
      if (!(i+1 < j)) continue;
      if ((i&1)==0) push((i+1)/2);
      if ((j&1)==1) push((j-1)/2);
    }
  }

  void upd_node(int I, const F &f) {
    values[I] = f * values[I];
    if (I < offset) queued[I] = f * queued[I];
  }

  void upd(int i, const F &f) {
    i += offset;
    push_col(i, f);
    upd_node(i, f);
  }
  void upd(int i, int j, const F &f) {
    i += offset-1;
    j += offset+1;
    push_range(i, j);
    while (i+1 < j) {
      if ((i&1)==0) upd_node(i+1, f);
      if ((j&1)==1) upd_node(j-1, f);
      i >>= 1, j >>= 1;
    }
  }

  S qry(int i) {
    i += offset;
    push_col(i);
    return values[i];
  }
  S qry(int i, int j) {
    i += offset-1;
    j += offset+1;
    push_range(i, j);
    S ls, rs;
    while (i+1 < j) {
      if ((i&1)==0) ls = ls * values[i+1];
      if ((j&1)==1) rs = values[j-1] * rs;
      i >>= 1, j >>= 1;
    }
    return ls * rs;
  }

};

struct S {
  ll w = 1;
  ll s = 0;
  S operator*(const S &rhs) const {
    return {w+rhs.w, s+rhs.s};
  }
};

struct F {
  bool change_to = false;
  ll s = 0;
  F operator*(const F &rhs) const {
    if (change_to) return *this;
    return {rhs.change_to, rhs.s+s};
  }
  S operator*(const S &rhs) const {
    if (change_to) return {rhs.w, s * rhs.w};
    return {rhs.w, rhs.s + s * rhs.w};
  }
};

using SegTree = SegTreeBase<S, F>;
/*END_SNIPPET*/

int main() {
  // solution for https://cses.fi/problemset/task/1651/ is used as a test
  // TODO: should find something that uses more feautures
  ios::sync_with_stdio(0);cin.tie(0);

  int n, q; cin >> n >> q;
  vector<S> a(n);
  for (int i = 0; i < n; ++i)
    cin >> a[i].s;

  SegTree st(a);

  for (int qq = 0; qq < q; ++qq) {
    char c; cin >> c;
    if (c == '1') {
      int i, j; ll u;
      cin >> i >> j >> u; --i, --j;
      st.upd(i, j, {false, u});
    } else if (c == '2') {
      int i; cin >> i; --i;
      cout << st.qry(i).s << '\n';
    } else assert(0);
  }

}
