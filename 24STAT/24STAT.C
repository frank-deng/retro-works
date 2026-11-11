#include <stdio.h>

#define NVAL     13
#define NCOUNT   1820
#define GOALMAX  99
#define NOP      64
#define NPERM    24
#define MAPROWS  114

static unsigned int map[MAPROWS][GOALMAX + 1];
static unsigned int hash[2401];
static unsigned char perm[NPERM][4];
static int vals[4];

typedef struct {
    int n;
    int d;
} FRAC;

static FRAC frac(int n, int d)
{
    FRAC r;

    r.n = n;
    r.d = d;
    return r;
}

static FRAC fop(FRAC x, FRAC y, int op)
{
    FRAC r;

    r.n = 0;
    r.d = 0;
    if (x.d == 0 || y.d == 0)
        return r;
    switch (op) {
    case 1:
        r.n = x.n * y.d - y.n * x.d;
        r.d = x.d * y.d;
        break;
    case 2:
        r.n = x.n * y.n;
        r.d = x.d * y.d;
        break;
    case 3:
        r.n = x.n * y.d;
        r.d = x.d * y.n;
        break;
    default:
        r.n = x.n * y.d + y.n * x.d;
        r.d = x.d * y.d;
        break;
    }
    return r;
}

static void fcheck(FRAC v, int row, unsigned int bit)
{
    int q;

    if (v.d == 0 || v.n % v.d != 0)
        return;
    q = v.n / v.d;
    if (q < 0 || q > GOALMAX)
        return;
    map[row][q] |= bit;
}

static void expr_all(int a, int b, int c, int d, int o0, int o1, int o2,
                     int row, unsigned int bit)
{
    FRAC A, B, C, D;

    A = frac(a, 1);
    B = frac(b, 1);
    C = frac(c, 1);
    D = frac(d, 1);

    fcheck(fop(A, fop(B, fop(C, D, o0), o1), o2), row, bit);
    fcheck(fop(A, fop(fop(B, C, o0), D, o1), o2), row, bit);
    fcheck(fop(fop(A, fop(B, C, o0), o1), D, o2), row, bit);
    fcheck(fop(fop(fop(A, B, o0), C, o1), D, o2), row, bit);
    fcheck(fop(fop(A, B, o0), fop(C, D, o1), o2), row, bit);
}

static int prochash(int a, int b, int c, int d)
{
    int d0, d1, d2, hs;
    unsigned int mh;

    d0 = b - a + 15;
    d1 = c - b + 15;
    d2 = d - c + 15;
    hs = (d2 + d1 * 32 + d0 * 1024) >> 4;
    mh = (unsigned int)1 << (d2 & 15);
    if (hash[hs] & mh)
        return 0;
    hash[hs] |= mh;
    return 1;
}

static void calc24(int p, int row, unsigned int bit)
{
    int a, b, c, d, k, o0, o1, o2;

    a = vals[perm[p][0]];
    b = vals[perm[p][1]];
    c = vals[perm[p][2]];
    d = vals[perm[p][3]];
    if (!prochash(a, b, c, d))
        return;
    for (k = 0; k < NOP; k++) {
        o0 = k >> 4;
        o1 = (k >> 2) & 3;
        o2 = k & 3;
        expr_all(a, b, c, d, o0, o1, o2, row, bit);
    }
}

static int countres(int g)
{
    int i, n;
    unsigned int v;

    n = 0;
    for (i = 0; i < MAPROWS; i++) {
        v = map[i][g];
        while (v) {
            v &= v - 1;
            n++;
        }
    }
    return n;
}

static void init(void)
{
    int i, j, k, p;

    p = 0;
    for (i = 0; i < 4; i++)
        for (j = 0; j < 4; j++) {
            if (i == j)
                continue;
            for (k = 0; k < 4; k++) {
                if (i == k || j == k)
                    continue;
                perm[p][0] = (unsigned char)i;
                perm[p][1] = (unsigned char)j;
                perm[p][2] = (unsigned char)k;
                perm[p][3] = (unsigned char)(6 - i - j - k);
                p++;
            }
        }
    for (i = 0; i < 2401; i++)
        hash[i] = 0;
}

int main(void)
{
    int a, b, c, d, idx, i, p;
    unsigned int bit;
    FILE *fp;

    init();
    idx = 0;
    for (a = 1; a <= NVAL; a++) {
        vals[0] = a;
        for (b = a; b <= NVAL; b++) {
            vals[1] = b;
            for (c = b; c <= NVAL; c++) {
                vals[2] = c;
                for (d = c; d <= NVAL; d++) {
                    vals[3] = d;
                    printf("\rProcessed: %4d/%4d %3d%%", idx + 1, NCOUNT,
                           (idx + 1) * 100 / NCOUNT);
                    bit = (unsigned int)1 << (idx & 15);
                    for (p = 0; p < NPERM; p++)
                        calc24(p, idx >> 4, bit);
                    idx++;
                    for (i = 0; i < 2401; i++)
                        hash[i] = 0;
                }
            }
        }
    }

    printf("\nWriting 24STAT.CSV\n");
    fp = fopen("24STAT.CSV", "w");
    if (fp == NULL) {
        printf("Cannot create 24STAT.CSV\n");
        return 1;
    }
    fprintf(fp, "Goal,Solvable In %d\n", NCOUNT);
    for (i = 0; i <= GOALMAX; i++)
        fprintf(fp, "%d,%d\n", i, countres(i));
    fclose(fp);
    printf(" Done.\n");
    return 0;
}
