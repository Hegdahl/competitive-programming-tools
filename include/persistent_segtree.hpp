#pragma once

#include <memory>
#include <vector>

template<class S, class F>
struct PersistentSegtree {
  struct Node;
  using ptr = std::shared_ptr<Node>;

  struct Node {
    ptr lk, rk;
    long long l, r;
    S value;
    F queued;
    Node(ptr lk_, ptr rk_, long long l_, long long r_, S value_, F queued_)
      : lk(lk_), rk(rk_), l(l_), r(r_), value(value_), queued(queued_) {}
  };

  template<class ...Args>
  static ptr make_node(Args...args) {
    return std::make_shared<Node>(std::forward<Args>(args)...);
  }

  static ptr init(long long l, long long r, const F &update = F{}) {
    S value(l, r);
    update.apply(value);
    return make_node(nullptr, nullptr, l, r, value, update);
  }

  static ptr enqueue(const ptr &node, const F &update) {
    S value = node->value;
    F queued = node->queued;
    update.apply(value);
    update.apply(queued);
    return make_node(node->lk, node->rk, node->l, node->r, value, queued);
  }

  static ptr pushed(const ptr &node) {
    if (node->l == node->r)
      return node;
    long long mid = node->l + (node->r - node->r + 1) / 2;
    ptr lk = node->lk;
    ptr rk = node->rk;
    if (!lk) lk = init(node->l, mid-1, node->queued);
    else lk = enqueue(lk, node->queued);
    if (!rk) rk = init(mid, node->r, node->queued);
    else rk = enqueue(rk, node->queued);
    return make_node(lk, rk, node->l, node->r, node->value, F{});
  }

  friend S query(const ptr &node, long long i, long long j) {
    if (i > node->r || j < node->l)
      return S{};
    if (i <= node->l && j >= node->r)
      return node->value;
    ptr pnode = pushed(node);
    return query(pnode->lk, i, j) + query(pnode->rk, i, j);
  }

  friend ptr update(const ptr &node, long long i, long long j, F f) {
    if (i > node->r || j < node->l)
      return node;
    if (i <= node->l && j >= node->r)
      return enqueue(node, f);
    ptr pnode = pushed(node);
    ptr lk = update(pnode->lk, i, j, f);
    ptr rk = update(pnode->rk, i, j, f);
    S value = lk->value + rk->value;
    return make_node(lk, rk, pnode->l, pnode->r, value, F{});
  }

};
