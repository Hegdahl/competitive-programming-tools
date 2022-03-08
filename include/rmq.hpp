#pragma once

#include <cassert>
#include <cstdint>
#include <functional>
#include <utility>
#include <vector>

template<class T, class Cmp = std::less<>, int W = 32, class W_t = uint32_t, class Idx = uint32_t>
class RMQ {
 public:

  template<class Container>
  RMQ(Container &&src, Cmp &&cmp)
  : data(std::forward<Container>(src)), cmp_(std::forward<Cmp>(cmp)) {
    blocks.resize((data.size() + W - 1) / W);
    sparse_table.resize(std::__lg(blocks.size())+1);
    sparse_table[0].resize(blocks.size());

    for (size_t i = 0; i < blocks.size(); ++i)
      sparse_table[0][i] = Idx(blocks[i].init(*this, i * W, std::min(i * W + W, data.size())) + W * i);

    size_t w = 1;
    for (int lvl = 0; lvl+1 < (int)sparse_table.size(); ++lvl, w *= 2) {
      sparse_table[lvl+1].resize(sparse_table[lvl].size() - w);
      for (size_t i = 0; i < sparse_table[lvl+1].size(); ++i)
        sparse_table[lvl+1][i] = Idx(pick_index(sparse_table[lvl][i], sparse_table[lvl][i+w]));
    }
  }

  template<class Container>
  RMQ(Container &&src) : RMQ(std::forward<Container>(src), Cmp{}) {}

  // [i, j]
  const T &operator()(size_t i, size_t j) const {
    const T &ans = data[argmin(i, j)];
    return ans;
  }

  // [i, j]
  size_t argmin(size_t i, size_t j) const {
    assert(i <= j && j < data.size());

    // first relevant block
    size_t block_i = i / W;
    // last relevant block
    size_t block_j = j / W;

    if (block_i == block_j)
      return blocks[block_i](i%W, j%W) + W * block_i;

    size_t sides_ans = pick_index(
      blocks[block_i](i%W, W-1) + W * block_i,
      blocks[block_j](0, j%W)   + W * block_j
    );

    if (block_i+1 == block_j)
      return sides_ans;

    return pick_index(sides_ans, sparse_table_query(block_i+1, block_j-1));
  }

 private:

  struct block {
    W_t snapshots[W];

    // initialize stacks and return argmin [0, W)
    int init(RMQ &rmq, size_t begin, size_t end) {
      static std::vector<int> stack;

      stack.assign(1, 0);
      snapshots[0] = 1;

      int n = (int)(end-begin);

      for (int i = 1; i < n; ++i) {
        snapshots[i] = snapshots[i-1];
        while (snapshots[i] && rmq.compare_indices(begin+i, begin+stack.back())) {
          snapshots[i] ^= W_t(1) << stack.back();
          stack.pop_back();
        }
        snapshots[i] ^= W_t(1) << i;
        stack.push_back(i);
      }

      for (int i = n; i < W; ++i)
        snapshots[i] = snapshots[i-1];

      return ctz(snapshots[W-1]);
    }

    // argmin [i, j]
    int operator()(int i, int j) const {
      return ctz(snapshots[j] & ~((W_t(1)<<i)-1));
    }
  };

  std::vector<T> data;
  Cmp &&cmp_;
  std::vector<block> blocks;
  std::vector<std::vector<Idx>> sparse_table;

  bool compare_indices(size_t i, size_t j) const {
    return cmp_(data[i], data[j]);
  }

  size_t pick_index(size_t i, size_t j) const {
    return compare_indices(i, j) ? i : j;
  }

  size_t sparse_table_query(size_t i, size_t j) const {
    int lvl = sizeof(size_t)*8 - clz(j-i+1) - 1;

    size_t w = size_t(1) << lvl;
    return pick_index(sparse_table[lvl][i], sparse_table[lvl][j-w+1]);
  }

  template<class Int>
  __attribute__((target("lzcnt,bmi,bmi2"))) static constexpr int ctz(Int x) {
    if constexpr (sizeof(Int)*8 > 32)
      return __builtin_ctzll(x);
    else
      return __builtin_ctz(x);
  }

  template<class Int>
  __attribute__((target("lzcnt,bmi,bmi2"))) static constexpr int clz(Int x) {
    if constexpr (sizeof(Int)*8 > 32)
      return __builtin_clzll(x);
    else
      return __builtin_clz(x);
  }
};

template<class S>
RMQ(const std::vector<S> &) -> RMQ<S>;
template<class S>
RMQ(std::vector<S> &&) -> RMQ<S>;
template<class S, class Cmp>
RMQ(const std::vector<S> &, Cmp &&) -> RMQ<S, Cmp>;
template<class S, class Cmp>
RMQ(std::vector<S> &&, Cmp &&) -> RMQ<S, Cmp>;
