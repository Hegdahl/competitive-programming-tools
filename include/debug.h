#include <cxxabi.h>

namespace debugging {

  using namespace std;

  template<typename T> struct to_void { using type = void; };
 
  template<typename T, typename = void>
  struct is_iterable { static const bool value = false; };
  template<typename T>
  struct is_iterable<T, typename to_void<decltype(begin(T()))>::type> { static const bool value = true; };


  string find_and_replace(const string &source, const string &from, const string &to) {
    string retval;
    size_t p1 = 0;
    size_t p2 = min(source.find(from, p1), source.size());
    while (p2 < source.size()) {
      retval += source.substr(p1, p2-p1);
      retval += to;
      p1 = p2 + from.size();
      p2 = min(source.find(from, p1), source.size());
    }
    retval += source.substr(p1, p2-p1);
    return retval;
  }
 
  template<typename T>
  constexpr string type_name() {
    if (is_same<T, string>::value) return "string";
 
    int status;
    char *c_str = abi::__cxa_demangle(typeid(T).name(), 0, 0, &status);
    string retval = c_str;
    free(c_str);
 
    return find_and_replace(retval, "std::", "");
  }

  struct Debugger {
    ostream &_os;
    Debugger(ostream &os, size_t line_number) : _os(os) {
      _os << "\e[1;35m[DEBUG:" << line_number << "]\e[m ";
    }
    ~Debugger() { _os << '\n'; }
 
    template<typename T, typename = void>
    struct show_val { show_val(ostream &os, const T &value) { os << value; } };
 
    template<typename C>
    struct show_val<C, typename enable_if<is_iterable<C>::value &&
					!is_same<C, string>::value &&
					!is_same<C, const char *>::value &&
					!is_same<C, char *>::value &&
					!is_same<C, char[]>::value
					>::type> {
      show_val(ostream &os, const C &container) {
        os << "{ ";
        for (auto v : container) {
	  show_val<decltype(v)> sv(os, v);
	  os << ' ';
        }
        os << '}';
      }
    };
 
    template<typename T1, typename T2>
    struct show_val<pair<T1, T2>> {
      show_val(ostream &os, const pair<T1, T2> &p) {
        os << '(';
        show_val<T1>(os, p.first);
        os << ", ";
        show_val<T2>(os, p.second);
        os << ')';
      }
    };

    template<typename T>
    void show_type_and_val(const T &value) {
      string c = "\e[34m", r = "\e[m";
      _os << c
          << find_and_replace(
	       find_and_replace(
	         find_and_replace(
	           type_name<T>(), "<", r+"<"+c
	         ),
	         ">", r+">"+c),
               ",", r+","+c
	     )
          << r << ' ';
      show_val<T>(_os, value);
    }
 
    template<typename T>
    void show_tabbed(const T &value) {
      _os << "  "; show_type_and_val(value);
    }
    template<typename T, typename... Ts>
    void show_tabbed(const T &first, const Ts&... rest) {
      show_tabbed(first);
      _os << '\n';
      show_tabbed(rest...);
    }
    template<typename... Ts>
    void show_named(const char *names, const Ts&... values) {
      _os << names << " =\n";
      show_tabbed(values...);
    }
    template<typename T>
    void show_named(const char *name, const T &value) {
      _os << name << " = ";
      show_type_and_val(value);
    }
    template<size_t N, typename... Ts>
    void show_named(const char *name, const char (&first)[N], const Ts&... rest) {
      ++name;
      while (*name != '"') {
        if (*name == '\\') name += 2;
	else ++name;
      }
      name += 2;
      while (*name == ' ') ++name;
      _os << "\e[1;33m" << first << "\e[m " << name << " =\n";
      show_tabbed(rest...);
    }
    template<size_t N>
    void show_named(const char *name, const char (&value)[N]) {
      _os << "\e[1;33m" << value << "\e[m" << '\n';
    }
  };
}
#define DEBUG(...) do {				        \
  debugging::Debugger _debugger(cerr, __LINE__);	\
  _debugger.show_named(#__VA_ARGS__, __VA_ARGS__);	\
} while(0)
