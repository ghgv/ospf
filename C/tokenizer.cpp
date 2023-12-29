//https://java2blog.com/split-string-space-cpp/

#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include "tokenizer.h"
using namespace std;

tokenizer::tokenizer()
{
//    for (auto &s: out) {
//        std::cout << s << '\n';
//    }
//return 0;
}
 
void tokenizer::tokenize(string &str, vector<string> &out)
{
    stringstream ss(str);
 	
    string s;
    while (getline(ss, s, this->delim)) {
        out.push_back(s);
    }
    
}
 

