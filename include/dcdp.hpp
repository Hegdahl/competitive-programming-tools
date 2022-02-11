#pragma once

#include <vector>
#include <utility>

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
