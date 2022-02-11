#pragma once

#include <array>
#include <cassert>
#include <utility>

template<class T, int N>
class Tensor {
 public:

  Tensor(const T &value, const std::array<int, N> &dimensions)
    : dimensions_(dimensions), size_(calc_size()), data(new T[size()]{}) {
    fill(value);
  }

  ~Tensor() {
    delete[] data;
  }

  long long size() {
    return size_;
  }

  template<class ...Ints>
  T &operator()(Ints ...indices_pack) {
    static_assert(sizeof...(indices_pack) == N);

    long long indices[sizeof...(indices_pack)]{indices_pack...};

    long long I = 0;
    for (int i = 0; i < N; ++i) {
      assert(0 <= indices[i] && indices[i] < dimensions_[i]);
      I = I * dimensions_[i] + indices[i];
    }

    return data[I];
  }

  void fill(const T &value) {
    for (int i = 0; i < size(); ++i)
      data[i] = value;
  }

 private:
  long long calc_size() const {
    long long res = 1;
    for (int i = 0; i < N; ++i)
      res *= dimensions_[i];
    return res;
  }

  const std::array<int, N> dimensions_;
  const long long size_;
  T *data;
};

template<class T, class ... Ints>
auto make_tensor(T &&val, Ints...dimensions) {
  return Tensor<std::remove_reference_t<T>, sizeof...(Ints)>(std::forward<T>(val), {dimensions...});
}
