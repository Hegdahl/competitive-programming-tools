#pragma once

#include <iostream>
#include <tuple>

namespace impyster {

namespace internal {

template<class T>
class print_impl {
  public:
    print_impl(T args)
      : args_(std::move(args)), sep_(" "), end_("\n") {}
    ~print_impl() {
      print_tail<0>();
      std::cout << end_;
    }

    template<class S>
    void sep(S &&new_sep) {
      sep_ = std::forward<S>(new_sep);
    }

    template<class S>
    void end(S &&new_end) {
      end_ = std::forward<S>(new_end);
    }

  private:
    template<int I>
    void print_tail() {
      if constexpr (I)
        std::cout << sep_;
      std::cout << get<I>(args_);
      if constexpr (I+1 < std::tuple_size_v<T>)
        print_tail<I+1>();
    }

    T args_;
    std::string sep_, end_;
};

} // namespace internal

template<class...Args>
auto print(Args&&...args) {
  return internal::print_impl(std::tuple<Args...>(std::forward<Args>(args)...));
}

} // namespace impyster
