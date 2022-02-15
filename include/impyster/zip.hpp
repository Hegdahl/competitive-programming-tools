#pragma once

#include <tuple>
#include <utility>

namespace impyster {

namespace internal {

template<class T>
class zip_impl {
  private:
    T iterables_;

    using all_indices = decltype(std::make_index_sequence<std::tuple_size_v<T>>());
    using eat = int[];

    template<std::size_t...indices>
      auto begin_impl(std::integer_sequence<std::size_t, indices...>) {
        return std::make_tuple(get<indices>(iterables_).begin()...);
      }

    template<std::size_t...indices>
      auto end_impl(std::integer_sequence<std::size_t, indices...>) {
        return std::make_tuple(get<indices>(iterables_).end()...);
      }

  public:
    zip_impl(T iterables)
      : iterables_(std::move(iterables)) {}

    class iterator {
      public:
        iterator(auto iterators) : iterators_(iterators) {}

        auto operator*() {
          return deref_impl(all_indices{});
        }

        friend auto operator!=(const iterator &l, const iterator &r) {
          return neq_impl(l, r, all_indices{});
        }

        auto operator++() {
          incr_impl(all_indices{});
          return *this;
        }

      private:
        decltype(std::declval<zip_impl>().begin_impl(all_indices{})) iterators_;

        template<std::size_t...indices>
        auto deref_impl(std::integer_sequence<std::size_t, indices...>) {
          return std::make_tuple(*get<indices>(iterators_)...);
        }

        template<std::size_t...indices>
        void incr_impl(std::integer_sequence<std::size_t, indices...>) {
          std::ignore = eat{(++get<indices>(iterators_), 0)...};
        }

        template<std::size_t...indices>
        static bool neq_impl(const iterator &l, const iterator &r,
            std::integer_sequence<std::size_t, indices...>) {
          return (true && ... && (get<indices>(l.iterators_) != get<indices>(r.iterators_)));
        }
    };

    auto begin() {
      return iterator(begin_impl(all_indices{}));
    }

    auto end() {
      return iterator(end_impl(all_indices{}));
    }
};

} // namespace internal

template<class...Args>
auto zip(Args&&...args) {
  return internal::zip_impl(std::tuple<Args...>(std::forward<Args>(args)...));
}

} // namespace impyster
