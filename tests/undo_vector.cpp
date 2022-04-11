#include <impyster.hpp>
#include <undo_vector.hpp>

using namespace impyster;

int main() {

  undo_vector<int> a {1, 2, 3};
  a.checkpoint();

  print(a);
  a[0] = 5;
  print(a);
  a[2] = 5;
  print(a);
  a.undo();
  print(a);
  a.push_back(4);
  print(a);
  a.undo();
  print(a);

  a.push_back(0);
  a[0] = a[1] = a[2] = a[3];
  print(a);
  a.undo_to_checkpoint();
  print(a);

  a.pop_back();
  print(a);
  a.undo();
  print(a);
}
