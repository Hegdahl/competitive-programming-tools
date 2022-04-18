#pragma once

#include <sum_stack.hpp>

template<class T, class Op>
struct SumQueue {

  const Op &op_;
  SumStack<T, Op> in, out;

  SumQueue(const T &identity, const Op &op)
    : op_(op), in(identity, op), out(identity, op) {}

  void push(const T &x) {
    in.push(x);
  }

  void pop() {
    shift();
    out.pop();
  }

  T query() {
    return op_(in.query(), out.query());
  }

  int size() const {
    return in.size() + out.size();
  }

  void shift() {
    if (out.size()) return;

    while (in.size())
      out.push(in.pop());
  }

};
