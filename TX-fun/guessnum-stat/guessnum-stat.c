#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include <malloc.h>
#include <sys/types.h>
#include <signal.h>
#include <unistd.h>

#include <pthread.h>
#include <sys/sysinfo.h>
#include "guessnum-stat.h"
#define GUESS_CHANCES 12

typedef union{uint64_t n; uint16_t c[4];} cv_t;
inline uint64_t check(uint64_t ans, uint64_t guess){
	cv_t cv_a, cv_g;
	uint64_t i, j, result = 0;
	cv_a.n = ans; cv_g.n = guess;
	for (i = 0; i < 4; i++) {
		if (cv_a.c[i] == cv_g.c[i]) {
			result += 0x10;
		} else {
			for (j = 0; j < 4; j++) {
				if ((i != j) && (cv_a.c[i] == cv_g.c[j])) {
					result += 1;
				}
			}
		}
	}
	return result;
}
inline uint64_t guess(){
	uint64_t ans = candidates[rand() % CANDIDATES_COUNT], cbuf[CANDIDATES_COUNT], *c = candidates, cl = CANDIDATES_COUNT, times = 0, ci, g, i, res;
	while (times < GUESS_CHANCES) {
		g = c[rand() % cl];
		res = check(ans, g);
		if (res == 0x40) {
			return times + 1;
		}
		times++;
		ci = 0;
		for (i = 0; i < cl; i++) {
			if (res == check(c[i], g)) {
				cbuf[ci] = c[i];
				ci++;
			}
		}
		c = cbuf; cl = ci;
		if (cl == 0) {
			return 0;
		}
	}
	return times;
}

typedef struct {
	pthread_t tid;
	uint64_t stat[GUESS_CHANCES + 1];
} thread_data_t;
typedef enum{
	ACTION_NORMAL,
	ACTION_RECORD,
	ACTION_QUIT,
}action_t;
action_t action = ACTION_NORMAL;
static pthread_mutex_t report_mutex = PTHREAD_MUTEX_INITIALIZER;
uint64_t mstat[GUESS_CHANCES + 1];
char *filename;

void action_quit(int sig){
	pthread_mutex_lock(&report_mutex);
	action = ACTION_QUIT;
	pthread_mutex_unlock(&report_mutex);
}
void action_record(int sig){
	pthread_mutex_lock(&report_mutex);
	action = ACTION_RECORD;
	pthread_mutex_unlock(&report_mutex);
}
int read_file(char *filename, uint64_t *stat){
	FILE *fp; int i;
	char num[100] = "\0";

	fp = fopen(filename, "r");
	if (NULL == fp) {
		return 0;
	}
	for (i = 0; i < GUESS_CHANCES + 1; i++) {
		stat[i] = strtoull(fgets(num, 100, fp), NULL, 0);
	}
	fclose(fp);
	return 1;
}
int write_file(char *filename, uint64_t *stat){
	FILE *fp; int i;

	fp = fopen(filename, "w");
	if (NULL == fp) {
		return 0;
	}
	for (i = 0; i < GUESS_CHANCES + 1; i++) {
		fprintf(fp, "%lu\n", stat[i]);
	}
	fclose(fp);
	return 1;
}

void report_stat(uint64_t *stat) {
	int i;
	pthread_mutex_lock(&report_mutex);
	for (i = 0; i < GUESS_CHANCES + 1; i++) {
		mstat[i] += stat[i];
		stat[i] = 0;
	}
	write_file(filename, mstat);
	if (action != ACTION_QUIT) {
		action = ACTION_NORMAL;
	}
	pthread_mutex_unlock(&report_mutex);
}
void* thread_main(void *data){
	while (action != ACTION_QUIT) {
		while (action == ACTION_NORMAL) {
			(((thread_data_t*)data)->stat)[guess()]++;
		}
		report_stat(((thread_data_t*)data)->stat);
	}
	return ((void*)0);
}
int main(int argc, char *argv[]) {
	thread_data_t *thread_data;
	int proc_cnt = get_nprocs(), i, j;

	if (argc < 2) {
		fprintf(stderr, "Usage: %s FILENAME\n", argv[0]);
		return 1;
	}
	filename = argv[1];
	read_file(filename, mstat);

	srand(time(NULL));
	signal(SIGINT, action_quit);
	signal(SIGQUIT, action_quit);
	signal(SIGUSR1, action_record);

	thread_data = malloc(sizeof(thread_data_t) * proc_cnt);
	for (i = 0; i < proc_cnt; i++) {
		for (j = 0; j < GUESS_CHANCES + 1; j++) {
			thread_data[i].stat[j] = 0;
		}
		pthread_create(&(thread_data[i].tid), NULL, thread_main, &(thread_data[i]));
	}

	for (i = 0; i < proc_cnt; i++) {
		pthread_join(thread_data[i].tid, NULL);
	}
	free(thread_data);

	signal(SIGUSR1, SIG_DFL);
	signal(SIGINT, SIG_DFL);
	signal(SIGQUIT, SIG_DFL);

	return 0;
}

