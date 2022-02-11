#pragma once

#include <algorithm>
#include <vector>

template<class F, class X>
struct LiChao {
  struct Node {
    F f;
    int lk = -1, rk = -1;
  };

  int root = -1;
  std::vector<Node> nodes;

  auto query(const X &x) {
    return query_impl(root, x, X::lo(), X::hi());
  }

  void update(const F &f, const X &ux0, const X &uxf) {
    root = update_impl(root, f, X::lo(), X::hi(), ux0, uxf);
  }

  auto query_impl(int I, const X &x, const X &nx0, const X &nxf) {
    if (I == -1) return F{}(x);

    X mid {nx0, nxf};
    if (x < mid)
      return std::min(nodes[I].f(x), query_impl(nodes[I].lk, x, nx0, mid));
    else
      return std::min(nodes[I].f(x), query_impl(nodes[I].rk, x, mid, nxf));
  }

  int update_impl(int I, F f, const X &nx0, const X &nxf, const X &ux0, const X &uxf) {
    if (!(ux0 < nxf))
      return I;
    if (!(nx0 < uxf))
      return I;

    if (I == -1) {
      I = (int)nodes.size();
      nodes.emplace_back();
    }

    X mid {nx0, nxf};

    bool cover = !(nx0<ux0 || uxf<nxf);
    bool imp_lef = f(nx0) < nodes[I].f(nx0);
    bool imp_mid = f(mid) < nodes[I].f(mid);

    if (cover) {

      if (imp_mid)
        std::swap(f, nodes[I].f);

      if (!(nx0 < mid && mid < nxf))
        return I;

      if (imp_lef ^ imp_mid)
        nodes[I].lk = update_impl(nodes[I].lk, f, nx0, mid, ux0, uxf);
      else
        nodes[I].rk = update_impl(nodes[I].rk, f, mid, nxf, ux0, uxf);

    } else {

      if (!(nx0 < mid && mid < nxf))
        return I;

      nodes[I].lk = update_impl(nodes[I].lk, f, nx0, mid, ux0, uxf);
      nodes[I].rk = update_impl(nodes[I].rk, f, mid, nxf, ux0, uxf);
    }

    return I;
  }
};
