#include "registration.h"
#include <vector>
#include <functional>
using namespace std;

vector<std::function<int(int , void *)>> registerprotocol;

registration::registration( void *name )
{
	//registerprotocol.emplace_back(name);	


}
