#ifndef TIMEROSPF_H
#define TIMEROSPF_H

class ospftimer {
	int interval = 30;

public:
	void independentThread();
	void threadCaller();
};


#endif
