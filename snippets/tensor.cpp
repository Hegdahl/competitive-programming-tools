#include <cassert>
#include <iostream>
#include <string>

/*BEGIN_SNIPPET*/
template<class T>
class Tensor {
 public:

  template<class ...Ints>
  Tensor(const T &value, Ints ...dimensions)
  : dimension_count(sizeof...(dimensions)),
    dimensions_(new long[]{dimensions...}),
    data(new T[(unsigned long)size()]{}) {
    fill(value);
  }

  ~Tensor() {
    delete[] dimensions_;
    delete[] data;
  }

  long size() const {
    long res = 1;
    for (int i = 0; i < dimension_count; ++i)
      res *= dimensions_[i];
    return res;
  }

  template<class ...Ints>
  T &operator()(Ints ...indices_pack) {
    assert(sizeof...(indices_pack) == dimension_count);

    long indices[sizeof...(indices_pack)]{indices_pack...};

    long I = 0;
    for (int i = 0; i < dimension_count; ++i) {
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

  int dimension_count;
  const long *dimensions_;
  T *data;
};
/*END_SNIPPET*/

int main() {
  Tensor x(std::string("abc"), 2, 3);

  for (int i = 0; i < 2; ++i)
    for (int j = 0; j < 3; ++j)
      x(i, j) = std::to_string(i) + '_' + std::to_string(j);

  for (int i = 0; i < 2; ++i)
    for (int j = 0; j < 3; ++j)
      std::cerr << x(i, j) << '\n';
}
