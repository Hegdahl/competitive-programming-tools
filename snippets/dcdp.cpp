#include <algorithm>
#include <iostream>
#include <vector>

/*BEGIN_SNIPPET*/
template<class Cost>
struct DivideAndConquerDP {
  const Cost &cost_;
  using T = decltype(cost_(0,0));
  std::vector<T> dp, new_dp;
  T max;
 
  DivideAndConquerDP(const Cost &cost) : cost_(cost) {}
 
  void step(int l, int r, int optl, int optr) {
    if (l > r) return;
 
    int mid = l + (r-l+1)/2;
    std::pair<T, int> opt_pair {max, 1e9};
 
    for (int i = optl; i <= std::min(optr, mid-1); ++i)
      opt_pair = std::min(opt_pair, {dp[i]+cost_(i+1, mid), i});
 
    auto [val, opt] = opt_pair;
    new_dp[mid] = val;
 
    step(l, mid-1, optl, opt);
    step(mid+1, r, opt, optr);
  }
 
  T solve(int n, int k) {
    dp.resize(n);
    new_dp.resize(n);
 
    max = cost_(0, n-1);
 
    for (int i = 0; i < n; ++i)
      dp[i] = cost_(0, i);
 
    for (int kk = 1; kk < std::min(n, k); ++kk) {
      step(0, n-1, 0, n-1);
      swap(dp, new_dp);
    }
 
    return dp[n-1];
  }
};
/*END_SNIPPET*/

//* solution to https://open.kattis.com/problems/gondolas
int main() {
  std::cin.tie(0)->sync_with_stdio(0);

  int n, t, g;
  std::cin >> n >> t >> g;

  std::vector<int> a(n);
  for (int &x : a) {
    std::cin >> x;
    x %= 2*t;
  }
  std::sort(a.begin(), a.end());

  {
    std::vector<int> cpy = a;
    for (int &x : cpy)
      x += 2*t;
    a.insert(a.end(), cpy.begin(), cpy.end());
  }

  std::vector<int> pre(a.size()+1);
  for (int i = 0; i < (int)a.size(); ++i)
    pre[i+1] = pre[i] + a[i];

  int ans = 1e9;
  for (int offset = 0; offset < n; ++offset) {

    auto cost = [&](int i, int j){
      int sum = pre[j+1+offset] - pre[i+offset];
      return (j-i+1)*a[j+offset] - sum;
    };

    DivideAndConquerDP dcdp(cost);
    int here = dcdp.solve(n, g);
    ans = std::min(ans, here);
  }

  std::cout << ans << '\n';
}
// */
