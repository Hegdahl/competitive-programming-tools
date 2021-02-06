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

using ld = long double;

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

struct hsh {
  size_t operator()(uint64_t x) const {
    static const uint64_t FIXED_RANDOM = chrono::steady_clock::now().time_since_epoch().count();
    x += FIXED_RANDOM;
    x += 0x9e3779b97f4a7c15;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9;
    x = (x ^ (x >> 27)) * 0x94d049bb133111eb;
    return x ^ (x >> 31);
  }
};

int main() {
  ios::sync_with_stdio(0);cin.tie(0);

  GETI(T); REP(TT, T) {

  }

}
