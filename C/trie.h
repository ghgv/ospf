#ifndef TRIE_H
#define TRIE_H

#include <stdio.h>
#include <string>
using namespace std;

class Trie{
	
	// Initializae your data 
	
	public:
	void trie()
	{
	
	}
	
	
	void insert (string word){
	
	}
	
	bool search(string word){
		return false;
	}
	
	bool startWith(string prefix)
		{
		 return false;
		}
	
	class Node; 
};



class Trie::Node {
	public:
	char c;
	bool isWord;
	//Node children;
	Node(char c);
};


#endif
