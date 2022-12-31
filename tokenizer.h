#ifndef TOKENIZER_H
#define TOKENIZER_H

#include <iostream>
#include <string>
#include <vector>
#include <sstream>

using namespace std;

class tokenizer
{
	public:
	vector<string> out;
	tokenizer();
	void tokenize(string  &str, vector<string> &out);
	
	private:
	const char delim = ' ';
};



#endif
