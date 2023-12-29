#include <iostream>
#include <chrono>
#include <thread>
#include "timerospf.h"
 
void ospftimer::independentThread() 
{
    std::cout << "Starting process ospf.\n";
    while(1)
	{
    		std::this_thread::sleep_for(std::chrono::seconds(interval));
		std::cout << "Sending hello packet.\n";
	}
		   
}
 
void ospftimer::threadCaller() 
{
    //std::cout << "Starting thread caller.\n";
    std::thread t(ospftimer::independentThread);
    t.detach();
    //std::this_thread::sleep_for(std::chrono::seconds(1));
    //std::cout << "Exiting thread caller.\n";
}
