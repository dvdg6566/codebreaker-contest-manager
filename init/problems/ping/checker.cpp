#include <bits/stdc++.h>

using namespace std;

int P, S, ans;

int main(int argc, char *argv[]){
    FILE *in = fopen(argv[1], "r");
    FILE *uout = fopen(argv[2], "r");
    fscanf(in, "%d%d", &S, &P);
    char str[50];
    fscanf(uout, "%s\n", &str);
    if (strcmp("wabbit", str)) {
        char x = str[6];
        printf("0\n");
        if (x == '1') printf("Too many pings\n");
        else if (x == '2') printf("Invalid ping\n");
        else if (x == '3') printf("Wrong Answer\n");
        return 0;
    }
    fscanf(uout, "%d", &ans);
    if (P == 100000){
        printf("1\n");
    }
    else{
        printf("%.4lf\n", min(((double)31.0-(double)ans)/((double)30),(double)1));
        printf("Queries Used = %d\n",ans);
    }
}
