#pragma once
#include <iostream>
#include <cxxabi.h>
#include <utility>

#define DEBUG(...) dbg_::debugger(__LINE__, __VA_ARGS__)
#define ASSERT(...) do {                    \
  DEBUG("ASSERTION FAILED: ", __VA_ARGS__); \
  exit(1);                                  \
} while (!dbg_::get_head(__VA_ARGS__))

namespace dbg_ {

template<class T, class ...Ts>
auto get_head(T &&head, Ts &&...) {
  return std::forward<T>(head);
}

struct debugger {

  template<class ...Ts>
  debugger(Ts &&...args) {}

};

} /* namespace dbg */
