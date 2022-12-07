#define  _POSIX_C_SOURCE  200809L

#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <limits.h>
#include <pulse/simple.h>
#include <pulse/error.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>

static volatile int     done = 0;

static pa_simple       *audio = NULL;
static size_t           audio_channels = 0;
static size_t           audio_samples = 0;
static int32_t         *audio_buffer = NULL;    /* audio_buffer[audio_samples][audio_channels] */
static int32_t         *audio_min = NULL;       /* audio_min[audio_channels] */
static int32_t         *audio_max = NULL;       /* audio_max[audio_channels] */
static pthread_t        audio_thread;

static pthread_mutex_t  peak_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t   peak_update = PTHREAD_COND_INITIALIZER;
static float           *peak_amplitude = NULL;
static volatile int     peak_available = 0;

int one(){
  return 1;
}

int vu_peak_available(void)
{
    return peak_available;
}

static void *worker(void *unused)
{
    (void)unused;  /* Silence warning about unused parameter. */

    while (!done) {
        int  err = 0;

        if (pa_simple_read(audio, audio_buffer, audio_channels * audio_samples * sizeof audio_buffer[0], &err) < 0) {
            done = -EIO;
            break;
        }

        for (size_t c = 0; c < audio_channels; c++) {
            audio_min[c] = (int32_t)( 2147483647);
            audio_max[c] = (int32_t)(-2147483648);
        }

        int32_t *const  end = audio_buffer + audio_channels * audio_samples;
        int32_t        *ptr = audio_buffer;

        /* Min-max peak detect. */
        while (ptr < end) {
            for (size_t c = 0; c < audio_channels; c++) {
                const int32_t  s = *(ptr++);
                audio_min[c] = (audio_min[c] < s) ? audio_min[c] : s;
                audio_max[c] = (audio_max[c] > s) ? audio_max[c] : s;
            }
        }

        /* absolute values. */
        for (size_t c = 0; c < audio_channels; c++) {
            if (audio_min[c] == (int32_t)(-2147483648))
                audio_min[c] =  (int32_t)( 2147483647);
            else
            if (audio_min[c] < 0)
                audio_min[c] = -audio_min[c];
            else
                audio_min[c] = 0;

            if (audio_max[c] < 0)
                audio_max[c] = 0;
        }

        /* Update peak amplitudes. */
        pthread_mutex_lock(&peak_lock);
        if (peak_available++) {
            for (size_t c = 0; c < audio_channels; c++) {
                const float  amplitude = (audio_max[c] > audio_min[c]) ? audio_max[c] / 2147483647.0f : audio_min[c] / 2147483647.0f;
                peak_amplitude[c] = (peak_amplitude[c] > amplitude) ? peak_amplitude[c] : amplitude;
            }
        } else {
            for (size_t c = 0; c < audio_channels; c++) {
                const float  amplitude = (audio_max[c] > audio_min[c]) ? audio_max[c] / 2147483647.0f : audio_min[c] / 2147483647.0f;
                peak_amplitude[c] = amplitude;
            }
        }
        pthread_cond_broadcast(&peak_update);
        pthread_mutex_unlock(&peak_lock);
    }

    /* Wake up all waiters on the peak update, too. */
    pthread_cond_broadcast(&peak_update);
    return NULL;
}
