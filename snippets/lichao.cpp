#pragma GCC optimize("Ofast")
#include <bits/stdc++.h>

using ll = long long;

/*BEGIN_SNIPPET*/
class LiChao {
 
 public:
  LiChao(ll x0, ll xf)
    : sz(0), x0_(x0), xf_(xf), root(nullptr) {}
 
  ~LiChao() {
    if (root) delete root;
  }
 
  ll query(ll x) {
    return query_impl(root, x, x0_, xf_);
  }
 
  void update(ll a, ll b) {
    return update_impl(root, Line{a, b}, x0_, xf_);
  }
 
  friend LiChao* merge(LiChao *lc0, LiChao *lc1) {
    if (!lc0) return lc1;
    if (!lc1) return lc0;
    if (lc0->size() < lc1->size())
      std::swap(lc0, lc1);

    std::set<std::pair<ll, ll>> lines;
    dfs(lc1->root, [&](ll a, ll b){
      lines.insert({a, b});
    });
    for (auto [a, b] : lines)
      lc0->update(a, b);
    delete lc1;
    return lc0;
  }

  size_t size() const {
    return sz;
  }

 private:
  struct Line {
    ll a, b;
    ll operator()(ll x) const {
      return a*x + b;
    }
  };

  struct Node {
    Line line;
    Node *lkid, *rkid;
    Node(Line line_)
      : line(line_), lkid(nullptr), rkid(nullptr) {}
    ~Node() {
      if (lkid) delete lkid;
      if (rkid) delete rkid;
    }
  };

  template<class CallBack>
  static void dfs(Node *node, const CallBack &cb) {
    if (!node) return;
    dfs(node->lkid, cb);
    cb(node->line.a, node->line.b);
    dfs(node->rkid, cb);
  }
 
  size_t sz;
  ll x0_, xf_;
  Node *root;
 
  ll query_impl(Node *node, ll x, ll x0, ll xf) {
    if (!node) return 1LL<<60;
 
    ll xm = x0 + (xf-x0)/2;
 
    if (x < xm)
      return std::min(node->line(x), query_impl(node->lkid, x, x0, xm));
    else
      return std::min(node->line(x), query_impl(node->rkid, x, xm, xf));
  }
 
  void update_impl(Node *&node, Line new_line, ll x0, ll xf) {
    if (!node) {
      ++sz;
      node = new Node(new_line);
      return;
    }
 
    ll xm = x0 + (xf-x0)/2;
    bool imp0 = new_line(x0) < node->line(x0);
    bool impm = new_line(xm) < node->line(xm);
 
    if (impm)
      std::swap(node->line, new_line);
 
    if (xf-x0 == 1)
      return;
 
    if (imp0 != impm)
      update_impl(node->lkid, new_line, x0, xm);
    else
      update_impl(node->rkid, new_line, xm, xf);
  }
};
/*END_SNIPPET*/

using namespace std;

int main() {
  cin.tie(0)->sync_with_stdio(0);

  //TODO: make test
}
