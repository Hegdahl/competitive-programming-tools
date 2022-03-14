#pragma once

#include <algorithm>
#include <limits>
#include <map>
#include <vector>

template<class T = long long>
struct Flow {
  static constexpr T INF = std::numeric_limits<T>::max() / 2;

  struct Edge {
    int to;
    T remain;
    Edge *flipped;
  };

  const int n;
  std::vector<std::map<int, T>> tmp_graph;
  std::vector<std::vector<Edge>> graph;
  std::vector<std::vector<Edge*>> level_graph;
  std::vector<int> dist, q;
  std::vector<int> dead, vis_list;

  Flow(int n_) : n(n_), tmp_graph(n), graph(n), level_graph(n), dist(n, -1), dead(n) {
    q.reserve(n);
    vis_list.reserve(2*n);
  }

  // O(log E)
  void connect(int i, int j, T w) {
    tmp_graph[i][j] += w;
    tmp_graph[j][i] += 0;
  }

  // O(V + E log E)
  void init_graph() {
    for (int i = 0; i < n; ++i)
      graph[i].resize(tmp_graph[i].size());

    std::vector<int> sz(n);
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

  // O(V'+E')
  T dfs(int cur, T mn) {
    vis_list.push_back(cur);

    if (cur == n-1) return mn;

    for (int I = (int)level_graph[cur].size()-1; I >= 0; --I) {
      Edge *e = level_graph[cur][I];
      if (!e->remain || dead[e->to]) {
        level_graph[cur].pop_back();
        continue;
      }
      T nxt = std::min(mn, dfs(e->to, std::min(e->remain, mn)));
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
  T blocking_flow() {
    T ans = 0;

    T mn = dfs(0, INF);
    while (mn) {
      ans += mn;
      mn = dfs(0, INF);
    }

    for (int i : vis_list)
      dead[i] = 0;
    vis_list.clear();

    return ans;
  }

  // O(V^2 E)
  // O(VE) for unit weights
  // O(V^.5 E) for bipartite with unit weights
  T solve() {
    init_graph();
    T ans = 0;
    while (init_level_graph())
      ans += blocking_flow();
    return ans;
  }
};
