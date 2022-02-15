#pragma once

#include <impyster/containers.hpp>

#include <iterator>
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
    auto begin_impl(std::integer_sequence<std::size_t, indices...>) const {
      return std::make_tuple(std::get<indices>(iterables_).begin()...);
    }

    template<std::size_t...indices>
    auto end_impl(std::integer_sequence<std::size_t, indices...>) const {
      return std::make_tuple(std::get<indices>(iterables_).end()...);
    }

    template<std::size_t...indices>
    auto get_iter_value(std::integer_sequence<std::size_t, indices...> seq) const {
      return tie_or_copy(*std::get<indices>(begin_impl(seq))...);
    }

  public:
    zip_impl(T iterables)
      : iterables_(std::move(iterables)) {}

    class iterator
      : public std::iterator<std::input_iterator_tag,
          decltype(std::declval<zip_impl>().get_iter_value(all_indices{}))> {

      public:
        iterator() {}
        template<class U>
        iterator(U iterators) : iterators_(std::move(iterators)) {}

        auto operator*() {
          return deref_impl(all_indices{});
        }

        auto operator*() const {
          return deref_impl(all_indices{});
        }

        friend auto operator!=(const iterator &l, const iterator &r) {
          return neq_impl(l, r, all_indices{});
        }

        friend auto operator==(const iterator &l, const iterator &r) {
          return !neq_impl(l, r, all_indices{});
        }

        auto &operator++() {
          incr_impl(all_indices{});
          return *this;
        }

        auto operator++(int) {
          auto cpy = *this;
          incr_impl(all_indices{});
          return cpy;
        }

      private:
        decltype(std::declval<zip_impl>().begin_impl(all_indices{})) iterators_;

        template<std::size_t...indices>
        auto deref_impl(std::integer_sequence<std::size_t, indices...>) {
          return tie_or_copy(*std::get<indices>(iterators_)...);
        }

        template<std::size_t...indices>
        auto deref_impl(std::integer_sequence<std::size_t, indices...>) const {
          return tie_or_copy(*std::get<indices>(iterators_)...);
        }

        template<std::size_t...indices>
        void incr_impl(std::integer_sequence<std::size_t, indices...>) {
          std::ignore = eat{(++std::get<indices>(iterators_), 0)...};
        }

        template<std::size_t...indices>
        static bool neq_impl(const iterator &l, const iterator &r,
            std::integer_sequence<std::size_t, indices...>) {
          return (true && ... && (std::get<indices>(l.iterators_) != std::get<indices>(r.iterators_)));
        }
    };

    auto begin() const {
      return iterator(begin_impl(all_indices{}));
    }

    auto end() const {
      return iterator(end_impl(all_indices{}));
    }
};

} // namespace internal

template<class...Args>
auto zip(Args&&...args) {
  return internal::zip_impl(tie_or_copy(std::forward<Args>(args)...));
}

} // namespace impyster
