#pragma once

#include <istream>
#include <ostream>
#include <type_traits>
#include <tuple>
#include <utility>
#include <vector>

namespace impyster {

namespace internal {

template<class T>
struct is_already_inputable : std::false_type {};
template<>
struct is_already_inputable<std::string> : std::true_type {};
template<class T>
constexpr bool is_already_inputable_v = is_already_inputable<T>::value;

template<class T>
struct is_already_outputable : std::false_type {};
template<>
struct is_already_outputable<std::string> : std::true_type {};
template<>
struct is_already_outputable<const std::string> : std::true_type {};
template<class T>
constexpr bool is_already_outputable_v = is_already_outputable<T>::value;

template<class T, class = void>
struct is_iterable : std::false_type {};
template<class T>
struct is_iterable<T, std::void_t<decltype(std::declval<T>().begin())>> : std::true_type {};
template<class T>
constexpr bool is_iterable_v = is_iterable<T>::value;

} // namespace internal

template<class T>
requires (internal::is_iterable_v<T> && !internal::is_already_inputable_v<T>)
std::istream &operator>>(std::istream &is, T &container) {
  for (auto &v : container)
    is >> v;
  return is;
}

template<class T>
requires (internal::is_iterable_v<T> && !internal::is_already_outputable_v<std::remove_reference_t<T>>)
std::ostream &operator<<(std::ostream &os, T &&container) {
  for (auto &&v : container)
    os << v << ' ';
  return os;
}

template<class T>
auto make_vec(T &&iterable) {
  using value_type = std::remove_reference_t<decltype(*std::declval<T>().begin())>;
  return std::vector<value_type>(iterable.begin(), iterable.end());
}

template<class...Args>
auto tie_or_copy(Args&&...args) {
  return std::tuple<Args...>(std::forward<Args>(args)...);
}

} // namespace impyster
