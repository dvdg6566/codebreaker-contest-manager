#include <cstdlib>
#include <cstdio>
#include "swapper.h"
#include "prisoner.h"

using namespace std;

int * boxes;
int counter = 0;

void swapKeys(int a, int b) {
    int t = boxes[a];
    boxes[a] = boxes[b];
    boxes[b] = t;
    counter++;
    return;
}
int N;
int counterob = 0;
int priboxes[3000];
int cur_id;
int saved = 0;

int openBox(int x) {
    counterob++;
    if (x<0||x>=2*N) return counterob=-1000000000;
    if (priboxes[x]==cur_id) {
        saved++;
        cur_id = -1;
    }
    return priboxes[x];
}

int main () {
    scanf("%d", &N);
    boxes = new int[2*N];
    int * tboxes = new int[2*N];
    for (int i = 0; i < 2*N; i++) {
        scanf("%d", &boxes[i]);
        tboxes[i] = boxes[i];
    }

    swapper(N,tboxes);
    int swaps = counter;
    if (swaps>100) {
        printf("EVILPENGUIN 0 0\nToo many swaps!\n");
        return 0;
    }
    for (int i = 0; i < 2*N; i++) priboxes[i]=boxes[i];
    for (int i = 0; i < 2*N; i++) {
        counterob = 0;
        cur_id = i;
        prisoner(N,i);
        if (counterob > N) {
            printf("EVILPENGUIN 0 0\nToo many boxes opened!\n");
            return 0;
        }
        if (counterob < 0) {
            printf("EVILPENGUIN 0 0\nID of box not within valid range!\n");
            return 0;
        }
    }
    printf("EVILPENGUIN %d %d\nSaved %d prisoners in %d swaps.\n", saved,swaps,saved,swaps);
    return 0;
}
