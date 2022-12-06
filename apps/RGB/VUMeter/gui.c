#define  _POSIX_C_SOURCE  200809L
#include <stdlib.h>
#include "vu.h"
#include <stdio.h>
#include <pthread.h>

static const char      devNum[] = "0";
static const char     *server   = NULL;
static const char     *device   = devNum;
static const int       channels = 2;     //    0 <  channels < 32
static const int       rate     = 48000; //  128 <   rate    < 250000
static const int       updates  = 60;    //    1 <  updates  < 200
static float          *peak     = NULL;
static const float     decay    = 0.95f;
static const size_t    samples  = rate/updates;

void *VUThread(){

  long val;
  val = vu_start(server, "vu-bar", device, "VU monitor", channels, rate, samples);
  if (val) {
    fprintf(stderr, "Cannot monitor audio source: %s.\n", vu_error(val));
    pthread_exit(NULL);
  }
  
  peak = calloc((size_t)channels * sizeof (float), samples);
  if (!peak) {
    fprintf(stderr, "Out of memory.\n");
    vu_stop();
    pthread_exit(NULL);
  }
  
  while(1){
    float  new_peak[channels];
    
    if (vu_peak(new_peak, channels) == channels) {
      for (int c = 0; c < channels; c++) {
	peak[c] *= decay;
	peak[c]  = (new_peak[c] > peak[c]) ? new_peak[c] : peak[c];
	printf("%f", peak[c]); //channels L,R
	if (c!=channels-1) printf(","); //channels L,R
      }
      printf("\n");
    }
    nanosleep((const struct timespec[]){{0, 17000000L}}, NULL);
  }
}


int main()
{
  pthread_t thread_id;
  pthread_create(&thread_id, NULL, VUThread, NULL);
  pthread_join(thread_id, NULL);

  getchar(); 
  int pthread_cancel(pthread_t thread);
  
  vu_stop();
  return 0;
}
