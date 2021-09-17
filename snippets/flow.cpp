#pragma GCC optimize("Ofast,unroll-loops")
#include <bits/stdc++.h>
#define ar array

using namespace std;
using ll = long long;

/*BEGIN_SNIPPET*/
struct Dinics {
  struct Edge {
    int to;
    ll remain;
    Edge *flipped;
  };

  const int n;
  vector<map<int, ll>> tmp_graph;
  vector<vector<Edge>> graph;
  vector<vector<Edge*>> level_graph;
  vector<int> dist, q;
  vector<int> dead, vis_list;

  Dinics(int n_) : n(n_), tmp_graph(n), graph(n), level_graph(n), dist(n, -1), dead(n) {
    q.reserve(n);
    vis_list.reserve(2*n);
  }

  // O(log E)
  void connect(int i, int j, ll w) {
    tmp_graph[i][j] += w;
    tmp_graph[j][i] += 0;
  }

  // O(V + E log E)
  void init_graph() {
    for (int i = 0; i < n; ++i)
      graph[i].resize(tmp_graph[i].size());

    vector<int> sz(n);
    for (int i = 0; i < n; ++i) {
      for (const auto &[j, w] : tmp_graph[i]) {
        if (i > j) continue;
        Edge &ij = graph[i][sz[i]++];
        Edge &ji = graph[j][sz[j]++];
        ij.to = j;
        ji.to = i;
        ij.remain = w;
        ji.remain = tmp_graph[j][i];
        ij.flipped = &ji;
        ji.flipped = &ij;
      }
    }

    for (int i = 0; i < n; ++i)
      level_graph[i].reserve(graph[i].size());
  }

  // O(V' + E')
  bool init_level_graph() {
    for (int i : q) {
      dist[i] = -1;
      level_graph[i].clear();
    }

    q.clear();
    q.push_back(0);
    dist[0] = 0;
    for (int qq = 0; qq < (int)q.size(); ++qq) {
      int i = q[qq];

      for (const Edge &e : graph[i]) {
        if (!e.remain) continue;
        if (dist[e.to] != -1) continue;
        dist[e.to] = dist[i] + 1;
        q.push_back(e.to);
        if (e.to == n-1) break;
      }

      if (dist[n-1] != -1) break;
    }

    if (dist[n-1] == -1) return false;

    for (int i : q) {
      for (Edge &e : graph[i]) {
        if (!e.remain) continue;
        if (dist[i] >= dist[e.to]) continue;
        if (e.to != n-1 && dist[e.to] >= dist[n-1]) continue;
        level_graph[i].push_back(&e);
      }
    }

    return true;
  }

  // O(N'+E')
  ll dfs(int cur, ll mn) {
    vis_list.push_back(cur);

    if (cur == n-1) return 1LL<<60;

    for (int I = (int)level_graph[cur].size()-1; I >= 0; --I) {
      Edge *e = level_graph[cur][I];
      if (!e->remain || dead[e->to]) {
        level_graph[cur].pop_back();
        continue;
      }
      ll nxt = min(mn, dfs(e->to, min(e->remain, mn)));
      if (nxt) {
        e->remain -= nxt;
        e->flipped->remain += nxt;
        if (!e->remain) {
          level_graph[cur].pop_back();
          if (level_graph[cur].size() == 0)
            dead[cur] = 1;
        }
        return nxt;
      }
      level_graph[cur].pop_back();
    }

    dead[cur] = 1;
    return 0;
  }

  // O(V'E')
  // O(E') for unit weights
  ll blocking_flow() {
    ll ans = 0;

    ll mn = dfs(0, 1LL<<60);
    while (mn) {
      ans += mn;
      mn = dfs(0, 1LL<<60);
    }

    for (int i : vis_list)
      dead[i] = 0;
    vis_list.clear();

    return ans;
  }

  // O(V^2 E)
  // O(VE) for unit weights
  // O(V^.5 E) for bipartite with unit weights
  ll solve() {
    init_graph();
    ll ans = 0;
    while (init_level_graph())
      ans += blocking_flow();
    return ans;
  }
};

struct BipartiteMatching {
  int n, m;
  Dinics dinics;
  BipartiteMatching(int n_, int m_) : n(n_), m(m_), dinics(2+n+m) {
    for (int i = 0; i < n; ++i)
      dinics.connect(0, i+1, 1);
    for (int j = 0; j < m; ++j)
      dinics.connect(j+1+n, 1+n+m, 1);
  }

  void connect(int i, int j) {
    dinics.connect(i+1, j+1+n, 1);
  }

  int solve() {
    return (int)dinics.solve();
  }

  vector<ar<int, 2>> get_matched() {
    solve();
    vector<ar<int, 2>> res;
    for (int i = 0; i < n; ++i) {
      for (auto &e : dinics.graph[i+1]) {
        if (e.remain) continue;
        if (e.to < 1+n) continue;
        if (e.to >= 1+n+m) continue;
        res.push_back({i, e.to-1-n});
      }
    }
    return res;
  }
};
/*END_SNIPPET*/

/* https://cses.fi/problemset/task/1696/
int main() {
  cin.tie(0)->sync_with_stdio(0);

  int L, R, M; cin >> L >> R >> M;
  vector<ar<int, 2>> e(M);
  for (auto &[i, j] : e)
    cin >> i >> j, --i, --j;
  sort(e.begin(), e.end());
  e.erase(unique(e.begin(), e.end()), e.end());

  BipartiteMatching bm(L, R);
  for (auto [i, j] : e)
    bm.connect(i, j);

  auto res = bm.get_matched();
  cout << res.size() << '\n';
  for (auto [i, j] : res)
    cout << i+1 << ' ' << j+1 << '\n';
}
// */

//* https://judge.yosupo.jp/problem/bipartitematching

const int mxM = 2e5;
char IBUF[14*mxM], OBUF[14*mxM];
int II = -1, OI = 0;

int read() {
  int x = 0;
  while (++II, IBUF[II] >= '0' && IBUF[II] <= '9')
    x = 10*x + IBUF[II]-'0';
  return x;
}

void write(int x) {
  int w = 1;
  {
    int tmp = x;
    do { ++w; } while (tmp /= 10);
  }

  OI += w;
  w = 1;
  do {
    OBUF[OI - ++w] = char(x%10 + '0');
  } while (x /= 10);
  OBUF[OI-1] = ' ';
}

int main() {
  fread(IBUF, 1, sizeof(IBUF), stdin);
  int L = read(), R = read(), M = read();

  BipartiteMatching bm(L, R);
  for (int mm = 0; mm < M; ++mm) {
    int i = read(), j = read();
    bm.connect(i, j);
  }

  auto res = bm.get_matched();
  write((int)res.size());
  for (auto [i, j] : res)
    write(i), write(j);

  fputs(OBUF, stdout);
}
// */
