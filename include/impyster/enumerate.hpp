#pragma once

#include <impyster/range.hpp>
#include <impyster/zip.hpp>

#include <limits>

namespace impyster {

template<class T>
auto enumerate(T &&iterable) {
  return zip(
    range(std::numeric_limits<long long>::max()/2),
    std::forward<T>(iterable)
  );
}

template<class T>
auto enumerate_after(T &&iterable) {
  return zip(
    std::forward<T>(iterable),
    range(std::numeric_limits<long long>::max()/2)
  );
}

} // namespace impyster
