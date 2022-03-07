#pragma once

#include <cassert>
#include <vector>

template<class S>
struct DisjointSparseTable {

  int n, height, width;
  std::vector<std::vector<S>> content;

  template<class Src>
  DisjointSparseTable(Src &&src)
  : n((int)src.size()), height(std::__lg(n-1)+1), width(1<<height),
    content{std::forward<Src>(src)} {

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

    int lvl = std::__lg(i^j);
    S res;
    res.pull(content[lvl][i], content[lvl][j]);
    return res;
  }
};

template<class S>
DisjointSparseTable(const std::vector<S> &) -> DisjointSparseTable<S>;
template<class S>
DisjointSparseTable(std::vector<S> &&) -> DisjointSparseTable<S>;
