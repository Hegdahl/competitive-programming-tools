#pragma once

#include <impyster/range.hpp>
#include <impyster/zip.hpp>

#include <limits>

namespace impyster {

template<class T>
auto enumerate(T &&iterable) {
  return zip(
    range(std::numeric_limits<long long>::max()),
    std::forward<T>(iterable)
  );
}

} // namespace impyster
