#include <bits/stdc++.h>

using ll = long long;

/*BEGIN_SNIPPET*/
template<class S, class F = std::nullptr_t>
struct SegTree {
  static constexpr bool is_lazy = !std::is_same<F, std::nullptr_t>::value;

  int n, offset;
  std::vector<S> values;
  std::vector<F> lazy;

  SegTree(int n_) : n(n_), offset(2<<std::__lg(n-1)) {
    values.resize(2*offset);
    if constexpr (is_lazy) lazy.resize(offset);
  }
  SegTree(int n_, S) : SegTree(n_) {}
  SegTree(int n_, S, F) : SegTree(n_) {}

  struct RangeReference {
    SegTree &st;
    const int i, j;

    RangeReference(SegTree &st_, int i_, int j_) : st(st_), i(i_), j(j_) {}

    template<typename Container>
    auto &operator=(const Container &s) {
      if constexpr (is_lazy) st.push_all(i, j, 1, 0, st.offset-1);

      int k = i;
      auto it = begin(s);
      while (it != end(s))
        st.values[st.offset + k++] = *it++;
      assert(k == j+1);

      int I = i+st.offset, J = j+st.offset;
      while ((I /= 2) && (J /= 2))
        for (k = I; k <= J; ++k)
          st.values[k].pull(st.values[2*k], st.values[2*k+1]);

      return *this;
    }

    auto &operator=(S s) {
      if constexpr (is_lazy) st.push_all(i, j, 1, 0, st.offset-1);
      for (int k = i; k <= j; ++k)
        st.values[st.offset+k] = s;

      int I = i+st.offset, J = j+st.offset;
      while ((I /= 2) && (J /= 2))
        for (int k = I; k <= J; ++k)
          st.values[k].pull(st.values[2*k], st.values[2*k+1]);

      return *this;
    }

    auto &operator*=(F f) {
      static_assert(is_lazy);
      st.upd(i, j, f, 1, 0, st.offset-1);
      return *this;
    }

    S operator*() {
      return st.qry(i, j, 1, 0, st.offset-1);
    }

    struct SHolder {
      S value;
      S *operator->() {
        return &value;
      }
    };

    auto operator->() {
      return SHolder{**this};
    }
  };

  auto operator()(int i) {
    return RangeReference(*this, i, i);
  }
  auto operator()(int i, int j) {
    return RangeReference(*this, i, j);
  }

  int push(int I, int l, int r) {
    static_assert(is_lazy);
    assert(I > 0);
    assert(I < offset);

    lazy[I].apply(values[2*I]);
    lazy[I].apply(values[2*I+1]);
    if (2*I < offset) {
      lazy[I].apply(lazy[2*I]);
      lazy[I].apply(lazy[2*I+1]);
    }
    lazy[I] = F();

    return l + (r-l+1)/2;
  }

  void push_all(int i, int j, int I, int l, int r) {
    static_assert(is_lazy);
    if (l == r) return;

    int mid = push(I, l, r);
    if (i < mid) push_all(i, j, 2*I, l, mid-1);
    if (j >= mid) push_all(i, j, 2*I+1, mid, r);
  }

  S qry(int i, int j, int I, int l, int r) {
    assert(!(i > r || j < l));

    if (i <= l && j >= r) return values[I];

    int mid;
    if constexpr (is_lazy) mid = push(I, l, r);
    else mid = l + (r-l+1)/2;

    S res; res.pull(
        (i < mid ? qry(i, j, 2*I, l, mid-1) : S()),
        (j >= mid ? qry(i, j, 2*I+1, mid, r) : S())
    );
    return res;
  }

  void upd(int i, int j, F f, int I, int l, int r) {
    static_assert(is_lazy);
    assert(!(i > r || j < l));
    if (i <= l && j >= r && f.can_lazy(values[I])) {
      f.apply(values[I]);
      if (I < offset)
        f.apply(lazy[I]);
      return;
    }

    assert(l != r);
    int mid = push(I, l, r);
    
    if (i < mid) upd(i, j, f, 2*I, l, mid-1);
    if (j >= mid) upd(i, j, f, 2*I+1, mid, r);
    values[I].pull(values[2*I], values[2*I+1]);
  }

  // returns max j such that cond([i, j]) = true
  template<class Cond>
  std::pair<S, int> walk_pre(int i, const Cond &cond) {
    auto [s, j] = walk_pre_impl(i, cond, {}, 1, 0, offset-1);
    return {s, std::min(j, n-1)};
  }

  // returns min i such that cond([i, j]) = true
  template<class Cond>
  std::pair<S, int> walk_suf(int j, const Cond &cond) {
    return walk_suf_impl(j, cond, {}, 1, 0, offset-1);
  }

  template<class Cond>
  std::pair<S, int> walk_pre_impl(int i, const Cond &cond, S pre, int I, int l, int r) {
    assert(i <= r);

    if (i <= l) {
      S s;
      s.pull(pre, values[I]);

      if (cond(s))
        return {s, r};

      if (l == r)
        return {pre, l-1};
    }

    int mid = push(I, l, r);

    if (i < mid) {
      auto [lv, l_after] = walk_pre_impl(i, cond, pre, 2*I, l, mid-1);
      if (l_after != mid-1) return {lv, l_after};

      return walk_pre_impl(i, cond, lv, 2*I+1, mid, r);
    }

    return walk_pre_impl(i, cond, pre, 2*I+1, mid, r);
  }

  template<class Cond>
  std::pair<S, int> walk_suf_impl(int j, const Cond &cond, S suf, int I, int l, int r) {
    assert(j >= l);

    if (j >= r) {
      S s;
      s.pull(values[I], suf);

      if (cond(s))
        return {s, l};

      if (l == r)
        return {suf, r+1};
    }

    int mid = push(I, l, r);

    if (j >= mid) {
      auto [rv, r_first] = walk_suf_impl(j, cond, suf, 2*I+1, mid, r);
      if (r_first != mid) return {rv, r_first};

      return walk_suf_impl(j, cond, rv, 2*I, l, mid-1);
    }

    return walk_suf_impl(j, cond, suf, 2*I, l, mid-1);
  }
};

struct S {
  ll w = 0, sum = 0; 
  std::array<ll, 2> mx = {-(1LL<<60), 0}, mx2 = {-(1LL<<60), 0};

  S() {}
  S(ll v) : w(1), sum(v), mx({v, 1}) {}

  void pull(S l, S r) {
    w = l.w + r.w;
    sum = l.sum + r.sum;

    std::array v {l.mx, l.mx2, r.mx, r.mx2};
    sort(v.rbegin(), v.rend());
    for (int i = 2; i >= 0; --i)
      if (v[i][0] == v[i+1][0]) v[i][1] += v[i+1][1], v[i+1] = {-(1LL<<60), 0};
    sort(v.rbegin(), v.rend());

    mx = v[0], mx2 = v[1];
  }
};

struct F {
  ll add = 0, mn = 1LL<<60;

  bool can_lazy(S s) {
    return mn > s.mx2[0] + add;
  }

  void apply(F &f) {
    f.add += add;
    f.mn += add;
    f.mn = std::min(mn, f.mn);
  }

  void apply(S &s) {
    assert(s.mx2[0]+add < mn);

    s.sum += add * s.w;
    s.mx[0] += add;
    s.mx2[0] += add;

    if (mn > s.mx[0]) return;

    ll d = s.mx[0] - mn;
    s.sum -= d * s.mx[1];
    s.mx[0] = mn;
  }
};
/*END_SNIPPET*/

int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  int n;
  std::cin >> n;
  std::vector<int> a(n);
  for (int &x : a)
    std::cin >> x;

  SegTree st(n, S{}, F{});
  st(0, n-1) = a;

  int q;
  std::cin >> q;
  for (int qq = 0; qq < q; ++qq) {
    int t, i, j, x;
    std::cin >> t >> i >> j;
    --i, --j;
    if (t != 3)
      std::cin >> x;

    if (t == 1) {
      st(i, j) *= {0, x};
    } else if (t == 2) {
      st(i, j) *= {x, 1LL<<60};
    } else if (t == 3) {
      std::cout << st(i, j)->sum << '\n';
    }
  }
}
