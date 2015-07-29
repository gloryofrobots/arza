*
   Double to ASCII Conversion without sprintf.
   Roughly equivalent to: sprintf(s, "%.14g", n);
*/

#include <math.h>
#include <string.h>
// For printf
#include <stdio.h>

static double PRECISION = 0.00000000000001;
static int MAX_NUMBER_STRING_SIZE = 32;

/**
 * Double to ASCII
 */
char * dtoa(char *s, double n) {
    // handle special cases
    if (isnan(n)) {
        strcpy(s, "nan");
    } else if (isinf(n)) {
        strcpy(s, "inf");
    } else if (n == 0.0) {
        strcpy(s, "0");
    } else {
        int digit, m, m1;
        char *c = s;
        int neg = (n < 0);
        if (neg)
            n = -n;
        // calculate magnitude
        m = log10(n);
        int useExp = (m >= 14 || (neg && m >= 9) || m <= -9);
        if (neg)
            *(c++) = '-';
        // set up for scientific notation
        if (useExp) {
            if (m < 0)
               m -= 1.0;
            n = n / pow(10.0, m);
            m1 = m;
            m = 0;
        }
        if (m < 1.0) {
            m = 0;
        }
        // convert the number
        while (n > PRECISION || m >= 0) {
            double weight = pow(10.0, m);
            if (weight > 0 && !isinf(weight)) {
                digit = floor(n / weight);
                n -= (digit * weight);
                *(c++) = '0' + digit;
            }
            if (m == 0 && n > 0)
                *(c++) = '.';
            m--;
        }
        if (useExp) {
            // convert the exponent
            int i, j;
            *(c++) = 'e';
            if (m1 > 0) {
                *(c++) = '+';
            } else {
                *(c++) = '-';
                m1 = -m1;
            }
            m = 0;
            while (m1 > 0) {
                *(c++) = '0' + m1 % 10;
                m1 /= 10;
                m++;
            }
            c -= m;
            for (i = 0, j = m-1; i<j; i++, j--) {
                // swap without temporary
                c[i] ^= c[j];
                c[j] ^= c[i];
                c[i] ^= c[j];
            }
            c += m;
        }
        *(c) = '\0';
    }
    return s;
}

int main(int argc, char** argv) {

    int i;
    char s[MAX_NUMBER_STRING_SIZE];
    double d[] = {
        0.0,
        42.0,
        1234567.89012345,
        0.000000000000018,
        555555.55555555555555555,
        -888888888888888.8888888,
        111111111111111111111111.2222222222
    };
    for (i = 0; i < 7; i++) {
        printf("%d: printf: %.14g, dtoa: %s\n", i+1, d[i], dtoa(s, d[i]));
    }
}
