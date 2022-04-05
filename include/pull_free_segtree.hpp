#pragma once

#include <type_traits>
#include <vector>

template<class V>
struct PullFreeSegTree {
  
  const int offset;
  std::vector<V> values;

  PullFreeSegTree(int n, V init) : offset(2<<std::__lg((n-1)|1)), values(2*offset, init) {}
  PullFreeSegTree(int n) : PullFreeSegTree(n, V{}) {}

  template<class F>
  void operator()(int i, int j, F &&f) {
    for (i += offset-1, j += offset+1; i+1 < j; i /= 2, j /= 2) {
      if (i%2 == 0) f(values[i+1]);
      if (j%2 == 1) f(values[j-1]);
    }
  }

  template<class F>
  void operator()(int i, F &&f) {
    for (i += offset; i; i /= 2)
      f(values[i]);
  }

  template<class Push, class Pop, class Callback>
  void dfs(Push &&push, Pop &&pop, Callback &&callback, int I = 1, int l = -1, int r = -1) {
    if (l == -1 && r == -1)
      l = 0, r = offset;

    push(values[I], l, r-1);
    if (I < offset) {
      int mid = l + (r-l)/2;
      dfs(push, pop, callback, 2*I, l, mid);
      dfs(push, pop, callback, 2*I+1, mid, r);
    } else {
      callback(I-offset, l, r-1);
    }
    pop(values[I], l, r-1);
  }

};
