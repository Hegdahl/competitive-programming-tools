#pragma once

#include <vector>

template<class V>
struct PullFreeSegTree {
  
  const int offset;
  std::vector<V> values;

  PullFreeSegTree(int n) : offset(2<<std::__lg((n-1)|1)), values(2*offset) {}

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
  void dfs(Push &&push, Pop &&pop, Callback &&callback, int I = 1) {
    push(values[I]);
    if (I < offset) {
      dfs(push, pop, callback, 2*I);
      dfs(push, pop, callback, 2*I+1);
    } else {
      callback(I-offset);
    }
    pop(values[I]);
  }

};