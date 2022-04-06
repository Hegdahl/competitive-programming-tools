#pragma once

#include <impyster/zip.hpp>

namespace impyster {

namespace internal {

template<class F, class T>
class map_impl {

  F func_;
  T iterable_;

 public:
  map_impl(F &&func, T &&iterable)
    : func_(std::forward<F>(func)), iterable_(std::forward<T>(iterable)) {}

  using inner_iterator = decltype(iterable_.begin());

  struct iterator : public inner_iterator {
    std::remove_reference_t<F> *func_ = nullptr;
    auto operator*() {
      return (*func_)(inner_iterator::operator*());
    }
  };

  auto begin() {
    iterator it{iterable_.begin()};
    it.func_ = &func_;
    return it;
  }

  auto end() {
    iterator it{iterable_.end()};
    it.func_ = &func_;
    return it;
  }

};

} // namespace internal

template<class F, class...Ts>
auto map(F &&func, Ts&&...iterables) {
  static_assert(sizeof...(Ts));

  if constexpr (sizeof...(Ts) == 1)
    return internal::map_impl<F, Ts...>(std::forward<F>(func), std::forward<Ts>(iterables)...);
  else
    return internal::map_impl(
      [f=std::forward<F>(func)](auto t) { return std::apply(f, t); },
      zip(std::forward<Ts>(iterables)...)
    );
}

} // namespace impyster
