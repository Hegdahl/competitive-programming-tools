#pragma once

#include <vector>

template<class Container = std::vector<int>, bool path_compression = true>
struct UFDS {
  Container a;

  UFDS(int n) : a(n, -1) {}

  int find(int i) {
    if constexpr (path_compression) {
      return a[i] < 0 ? i : a[i] = find(a[i]);
    } else {
      while (a[i] >= 0) i = a[i];
      return i;
    }
  }

  bool unite(int i, int j) {
    i = find(i), j = find(j);
    if (i == j) return false;
    if (-a[i] < -a[j])
      std::swap(i, j);
    a[i] += a[j];
    a[j] = i;
    return true;
  }

};
