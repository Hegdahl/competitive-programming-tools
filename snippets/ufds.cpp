#include <vector>

/*BEGIN_SNIPPET*/
struct UFDS {

  vector<int> a;
  UFDS(int n) : a(n, -1) {}

  int find(int i) {
    return a[i] < 0 ? i : a[i] = find(a[i]);
  }

  bool unite(int i, int j) {
    i = find(i), j = find(j);
    if (i == j) return false;
    if (-a[i] < -a[j])
      swap(i, j);
    a[i] += a[j];
    a[j] = i;
    return true;
  }
};
/*END_SNIPPET*/

int main() {

}
