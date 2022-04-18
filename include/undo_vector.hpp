#pragma once

#include <utils.hpp>
#include <vector>
#include <variant>

template<class T>
class undo_vector : public std::vector<T> {
  using change = std::variant<std::monostate, T, std::pair<T, size_t>>;
  std::vector<change> changes_;
  std::vector<size_t> checkpoints_;

  struct index_reference {
    undo_vector &u;
    size_t i;
    template<class V>
    index_reference &operator=(V &&v) {
      u.changes_.push_back(std::make_pair(u.std::vector<T>::operator[](i), i));
      u.std::vector<T>::operator[](i) = std::forward<V>(v);
      return *this;
    }

    operator T&() {
      return u.std::vector<T>::operator[](i);
    }
  };

 public:

  using std::vector<T>::vector;

  auto operator[](size_t i) {
    return index_reference{*this, i};
  }

  template<class U>
  void push_back(U &&v) {
    changes_.push_back({});
    std::vector<T>::push_back(std::forward<U>(v));
  } 

  void pop_back() {
    changes_.push_back(std::move(std::vector<T>::back()));
    std::vector<T>::pop_back();
  }

  void undo() {
    std::visit(overloaded{

      // undo push_back
      [&](std::monostate) {
        std::vector<T>::pop_back();
      },

      // undo pop_back
      [&](T &v) {
        std::vector<T>::push_back(std::move(v));
      },

      // undo assign
      [&](std::pair<T, size_t> &p) {
        std::vector<T>::operator[](p.second) = std::move(p.first);
      },

    }, changes_.back());
    changes_.pop_back();
  }

  void undo_to_checkpoint() {
    while (changes_.size() > checkpoints_.back())
      undo();
    checkpoints_.pop_back();
  }

  void checkpoint() {
    checkpoints_.push_back(changes_.size());
  }
};
