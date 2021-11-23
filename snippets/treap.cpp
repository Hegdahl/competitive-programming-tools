#include <bits/stdc++.h>
#define ar array

using namespace std;
using ll = long long;

/*BEGIN_TEMPLATE*/
template<S, F>
struct Treap {

  struct Node {
    int sz;
    bool flipped;
    Node *up, *lkid, *rkid;
    S s;
    F f;
    Node(Node *up_) : sz(1), flipped = false, lkid(0), rkid(0) {}
  };

  int size(Node *node) {
    if (!node) return 0;
    return node->sz;
  }

  void push(Node *node) {
    if (!node) return;
    if (node->lkid) node->f.apply(node->lkid.s);
    if (node->rkid) node->f.apply(node->rkid.s);
  }

  void pull(Node *node) {
    
  }

};
/*END_TEMPLATE*/

int main() {
  cin.tie(0)->sync_with_stdio(0);

  
}
