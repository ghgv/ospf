#include <stdio.h>
#include <pthread.h>

float a=3.13;

void *thread_function(void *arg) {
  a=a+1;
  printf("Hello from the new thread! %f\n",a);
  return NULL;
}

int main(int argc, char *argv[]) {
  pthread_t thread;

  // Create the new thread
  if (pthread_create(&thread, NULL, thread_function, NULL) != 0) {
    perror("pthread_create");
    return 1;
  }
 a=a+1;
 printf("A= %f",a);
 
  // Wait for the new thread to finish
  if (pthread_join(thread, NULL) != 0) {
    perror("pthread_join");
    return 1;
  }

  return 0;
}

