#include <iostream>
#include <vector>
#include <functional>
using std::cout;
using std::vector;
using std::endl;
using std::function;
int add(int i, int k) {
return i+k;
}
int subtract(int i, int k) {
return i-k;
}
int main() {
vector<std::function<int(int, int)>> ops;
ops.emplace_back(add);
ops.emplace_back(subtract);const int input2 = 13;
const int input1 = 123;
for (const auto& op : ops) {
cout<<op(input1, input2) << endl;
}
return 0;
}
