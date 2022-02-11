#pragma once

#include <utility>
#include <vector>

template<class T, class Op>
struct SumStack {

  const Op &op_;
  std::vector<std::pair<T, T>> data;

  SumStack(const T &identity, const Op &op)
    : op_(op), data{std::make_pair(identity, identity)} {}

  void push(const T &x) {
    data.push_back(std::make_pair(x, op_(data.back().second, x)));
  }

  T pop() {
    T last = data.back().first;
    data.pop_back();
    return last;
  }

  T query() const {
    return data.back().second;
  }

  int size() const {
    return (int)data.size() - 1;
  }

};
