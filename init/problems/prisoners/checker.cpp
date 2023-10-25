#include <cstdio>
#include <set>
#include <algorithm>
#include <iostream>
#include <cstring>
using namespace std;
char str[1000];
int main (int argc, char* argv[]) {
    FILE* uout = fopen(argv[2], "r");
    FILE* inf = fopen(argv[1], "r");
    FILE* out = fopen(argv[3], "r");
    int saved = 0;
    int swaps = 0;
    int N;

    fscanf(inf,"%d", &N);

    fscanf(uout, "%s %d %d\n", str,&saved, &swaps);
    //printf("%s", str);
    if (strcmp(str,"EVILPENGUIN")) {
        printf("0\nInvalid output detected.\n");
        return 0;
    }
    if (saved==0) {
        printf("0\n%s",str);
        return 0;
    }
    fgets(str,999,uout);
    double frac = ((double)saved) / (double)(2*N);
    double score = (frac*frac)/(double)max(swaps,1);
    printf("%.4lf\n%s", score, str);
    fclose(uout);
    fclose(inf);
    fclose(out);
    return 0;
}
