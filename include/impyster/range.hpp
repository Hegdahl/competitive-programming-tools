#pragma once

#include <cassert>
#include <iterator>

namespace impyster {

template<class T>
T round_away_from_zero_to_multiple(T val, T div) {
  if (val < 0) return -round_away_from_zero_to_multiple(-val, div);
  if (div < 0) return round_away_from_zero_to_multiple(val, -div);
  return (val + div - 1) / div * div;
}

template<class T>
class range {
  public:
    range(T start, T stop, T step)
      : start_(start), stop_(wrong_direction(start, stop, step) ? start : stop), step_(step) {}
    range(T start, T stop)
      : range(start, stop, 1) {}
    range(T stop)
      : range(0, stop) {}

    class iterator : public std::iterator<std::input_iterator_tag, T> {
      public:
        iterator() : range_(0), current_(0) {}
        iterator(const range * r, T current) : range_(r), current_(current) {}

        T operator*() const {
          return current_;
        }

        friend bool operator!=(const iterator &l, const iterator &r) {
          return l.current_ != r.current_;
        }

        friend bool operator==(const iterator &l, const iterator &r) {
          return l.current_ == r.current_;
        }

        auto &operator++() {
          current_ += range_->step_;
          return *this;
        }

        auto operator++(int) {
          auto cpy = this;
          current_ += range_->step_;
          return cpy;
        }

      private:
        const range * range_;
        T current_;
    };

    auto begin() const {
      return iterator(this, start_);
    }

    auto end() const {
      return iterator(this, start_ + round_away_from_zero_to_multiple(stop_-start_, step_));
    }

  private:
    static bool wrong_direction(T start, T stop, T step) {
      if (start < stop && step < 0) return true;
      if (start > stop && step > 0) return true;
      return false;
    }

    const T start_, stop_, step_;
};

} // namespace impyster
