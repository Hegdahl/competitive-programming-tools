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
using remove_cvref_t = std::remove_cv_t<std::remove_reference_t<T>>;

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
template<class T>
constexpr bool is_already_outputable_v = is_already_outputable<T>::value;

template<class T, class = void>
struct is_iterable : std::false_type {};
template<class T>
struct is_iterable<T, std::void_t<decltype(std::declval<T>().begin())>> : std::true_type {};
template<class T>
constexpr bool is_iterable_v = is_iterable<T>::value;

template<int I, class...Ts>
void read_tuple(std::istream &is, std::tuple<Ts...> &t) {
  if constexpr (I < sizeof...(Ts)) {
    is >> std::get<I>(t);
    read_tuple<I+1>(is, t);
  }
}

template<int I, class...Ts>
void read_tuple(std::istream &is, const std::tuple<Ts...> &t) {
  if constexpr (I < sizeof...(Ts)) {
    is >> std::get<I>(t);
    read_tuple<I+1>(is, t);
  }
}

template<int I, class...Ts>
void print_tuple(std::ostream &os, const std::tuple<Ts...> &t) {
  if constexpr (I < sizeof...(Ts)) {
    if constexpr (I)
      os << ' ';
    os << std::get<I>(t);
    print_tuple<I+1>(os, t);
  }
}

} // namespace internal

template<class T, class = std::enable_if_t<
internal::is_iterable_v<T> && !internal::is_already_inputable_v<internal::remove_cvref_t<T>>>>
std::istream &operator>>(std::istream &is, T &&container) {
  for (auto &&v : container)
    is >> v;
  return is;
}

template<class T, class = std::enable_if_t<
internal::is_iterable_v<T> && !internal::is_already_outputable_v<internal::remove_cvref_t<T>>>>
std::ostream &operator<<(std::ostream &os, T &&container) {
  for (auto &&v : container)
    os << v << ' ';
  return os;
}

template<class...Ts>
std::istream &operator>>(std::istream &is, std::tuple<Ts...> &t) {
  internal::read_tuple<0>(is, t);
  return is;
}

template<class...Ts>
std::istream &operator>>(std::istream &is, const std::tuple<Ts...> &t) {
  internal::read_tuple<0>(is, t);
  return is;
}

template<class...Ts>
std::ostream &operator<<(std::ostream &os, const std::tuple<Ts...> &t) {
  internal::print_tuple<0>(os, t);
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
