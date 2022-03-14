#pragma once

#include <string_view>
#include <cstddef>
#ifndef FAST_CIN_BUFFER_SIZE
#warning "FAST_CIN_BUFFER_SIZE is set to default of 1e8"
#define FAST_CIN_BUFFER_SIZE (int)(1e8)
#endif

#ifndef FAST_COUT_BUFFER_SIZE
#warning "FAST_COUT_BUFFER_SIZE is set to default of 1e8"
#define FAST_COUT_BUFFER_SIZE (int)(1e8)
#endif

#include <iostream>
#define cin std_cin_replacer
#define cout std_cout_replacer

#include <cstdio>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>

namespace fastio_detail {

constexpr bool is_whitespace(char c) {
  return c == ' ' || c == '\n';
}

static struct in_t {
  char data[FAST_CIN_BUFFER_SIZE];
  size_t pos = 0;

  in_t() {
    std::fread(data, 1, sizeof(data), stdin);
  };

  void skip_whitespace() {
    while (is_whitespace(data[pos])) ++pos;
  }

  std::string_view readline() {
    size_t start = pos;
    while (data[pos] != '\n') ++pos;
    return {data+start, pos - start};
  }
} in;

static struct out_t {
  char data[FAST_COUT_BUFFER_SIZE];
  size_t pos = 0;

  ~out_t() {
    std::fputs(data, stdout);
  }
} out;

template<class T, class = void>
struct reader : std::false_type {};

template<class T, class = void>
struct writer : std::false_type {};

template<class T>
struct reader<T, std::enable_if_t<std::is_integral_v<T>>> {
  void read_unsigned(T &x) {
    x = 0;
    while ('0' <= in.data[in.pos]  && in.data[in.pos] <= '9')
      x = 10 * x + in.data[in.pos++] - '0';
  }

  void read(T &x) {
    in.skip_whitespace();
    if constexpr (std::is_signed_v<T>) {
      bool neg = false;
      if (in.data[in.pos] == '-')
        neg = true, ++in.pos;
      read_unsigned(x);
      if (neg)
        x = -x;
    } else {
      read_unsigned(x);
    }
  }
};

template<class T>
struct writer<T, std::enable_if_t<std::is_integral_v<T>>> {
  void write_unsigned(T x) {
    size_t start = out.pos;
    do {
      out.data[out.pos++] = char(x%10+'0');
    } while (x /= 10);
    size_t end = out.pos-1;
    while (start < end)
      std::swap(out.data[start++], out.data[end--]);
  }

  void write(const T &x) {
    if constexpr (std::is_signed_v<T>) {
      if (x < 0) {
        out.data[out.pos++] = '-';
        write_unsigned(-x);
      } else {
        write_unsigned(x);
      }
    } else {
      write_unsigned(x);
    }
  }
};

template<>
struct reader<char> {
  void read(char &c) {
    in.skip_whitespace();
    c = in.data[in.pos++];
  }
};

template<>
struct writer<char> {
  void write(char c) {
    out.data[out.pos++] = c;
  }
};

template<>
struct reader<char*> {
  void read(char *s) {
    in.skip_whitespace();
    do {
      *s++ = in.data[in.pos++];
    } while (!is_whitespace(in.data[in.pos]));
  }
};

template<class T>
struct writer<T, std::enable_if_t<std::is_convertible_v<T, const char*>>> {
  void write(const char *s) {
    while (*s)
      out.data[out.pos++] = *s++;
  }
};

template<>
struct reader<std::string> {
  void read(std::string &s) {
    in.skip_whitespace();
    size_t start = in.pos;
    while (!is_whitespace(in.data[in.pos])) ++in.pos;
    s.assign(in.data+start, in.data+in.pos);
  }
};

template<>
struct writer<std::string> {
  void write(const std::string &s) {
    for (size_t i = 0; i < s.size(); ++i, ++out.pos)
      out.data[out.pos] = s[i];
  }
};

} // namespace fastio_detail

namespace std {

struct {
  template<class T, class = std::enable_if_t<
    !std::is_base_of_v<std::false_type, fastio_detail::reader<T>>>>
  auto &operator>>(T &x) {
    fastio_detail::reader<T>{}.read(x);
    return *this;
  }
} cin;

struct {
  template<class T, class = std::enable_if_t<
    !std::is_base_of_v<std::false_type, fastio_detail::writer<T>>>>
  auto &operator<<(const T &x) {
    fastio_detail::writer<T>{}.write(x);
    return *this;
  }
} cout;

template<class T>
auto &getline(decltype(cin) &fin_ref, T &s) {
  s.assign(fastio_detail::in.readline());
  return fin_ref;
}

} // namespace std
