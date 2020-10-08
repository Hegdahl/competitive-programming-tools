#pragma GCC optimize("Ofast")
#define _USE_MATH_DEFINES
#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

#ifdef ENABLE_DEBUG
#include <debug.h>
#else
#define DEBUG(...) do {} while (0)
#endif

using namespace std;
using namespace __gnu_pbds;

using ll = long long;
using ull = unsigned long long;
using lll = __int128;
using ulll = unsigned __int128;

template<typename T, size_t N> using ar = array<T, N>;

template<typename T, typename Cmp = less<T>>
using iset = tree<T, null_type, Cmp, rb_tree_tag,
		  tree_order_statistics_node_update, allocator<T>>;

#define REPSI(name, start, stop, step) for (ll name = start; name < (ll)stop; name += step)
#define REPS(name, start, stop) REPSI(name, start, stop, 1)
#define REP(name, stop) REPS(name, 0, stop)

#define RREPSI(name, start, stop, step) for (ll name = stop-1; name >= (ll)start; name -= step)
#define RREPS(name, start, stop) RREPSI(name, start, stop, 1)
#define RREP(name, stop) RREPS(name, 0, stop)


template<typename T> void cins(T &first) { cin >> first; }
template<typename T, typename... Ts> void cins(T &first, T &second, Ts&... rest) {
  cin >> first;
  cins(second, rest...);
}

#define GET(type, ...) type __VA_ARGS__; cins(__VA_ARGS__)
#define GETI(...) GET(int, __VA_ARGS__)
#define GETLL(...) GET(ll, __VA_ARGS__)
#define GETS(...) GET(string, __VA_ARGS__)
#define GETD(...) GET(double, __VA_ARGS__)
#define GETC(...) GET(char, __VA_ARGS__)

template<typename T> istream &operator>>(istream &is, vector<T> &a) { for (T &v : a) is >> v; return is; }

int main() {
  ios::sync_with_stdio(false);
  cin.tie(0);

  GETI(T); REP(TT, T) {
  }
}
