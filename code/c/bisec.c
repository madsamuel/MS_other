/*
 * Finds roots of the equations
 *      g(x) = 0   and   h(x) = 0
 * on a specified interval [x_left, x_right] using the bisection method.
 */

#include <stdio.h>
#include <math.h>

#define FALSE 0
#define TRUE  1
#define NO_ROOT -99999.0

double bisect(double x_left, double x_right, double epsilon,
              double f(double farg));

double g(double x);
double h(double x);

int
main(void)
{
    double x_left, x_right,   /* left, right endpoints of interval */
           epsilon,           /* error tolerance */
           root;

    /* Get endpoints and error tolerance from user */
    printf("\nEnter interval endpoints> ");
    scanf("%lf%lf", &x_left, &x_right);
    printf("\nEnter tolerance> ");
    scanf("%lf", &epsilon);

    /* Use bisect function to look for roots of g and h */
    printf("\n\nFunction g");
    root = bisect(x_left, x_right, epsilon, g);
    if (root != NO_ROOT)
        printf("\n   g(%8.7f) = %e\n", root, g(root));
    
    printf("\n\nFunction h");
    root = bisect(x_left, x_right, epsilon, h);
    if (root != NO_ROOT)
    printf("\n   h(%8.7f) = %e\n", root, h(root));

    return (0);
}

/*
 * Implements the bisection method for finding a root of a function f.
 * Returns a root if signs of fp(x_left) and fp(x_right) are different.
 * Otherwise returns NO_ROOT.
 */

double
bisect(double x_left,        /* input  - endpoints of interval in */
       double x_right,       /*          which to look for a root */
       double epsilon,       /* input  - error tolerance */
       double f(double farg))/* input  - the function */
{
    double x_mid,    /* midpoint of interval */
           f_left,   /* f(x_left) */
           f_mid,    /* f(x_mid) */
           f_right;  /* f(x_right) */

    int root_found;  /* flag to indicate whether root is found */

    /* Computes function values at initial endpoints of interval */
    f_left  = f(x_left);
    f_right = f(x_right);

    /* If no change of sign occurs on the interval there is not a
     * unique root. Exit function and return NO_ROOT */
    if (f_left * f_right > 0) {   /* same sign */
        printf("\nMay be no root in [%.7f, %.7f]", x_left, x_right);
        return NO_ROOT;
    }

    /* Searches as long as interval size is large enough
     * and no root has been found */

root_found = FALSE;   /* no root found yet */
while (fabs(x_right - x_left) > epsilon && !root_found)
{
    /* Computes midpoint and function value at midpoint */
    x_mid = (x_left + x_right) / 2.0;
    f_mid = f(x_mid);

    if (f_mid == 0.0) {          /* Here's the root */
        root_found = TRUE;
    } else if (f_left * f_mid < 0.0) {  /* Root in [x_left, x_mid] */
        x_right = x_mid;
    } else {                     /* Root in [x_mid, x_right] */
        x_left = x_mid;
    }

    /* Trace loop execution - print root location or new interval */
    if (root_found)
        printf("\nRoot found at x = %.7f, midpoint of [%.7f, %.7f]",
               x_mid, x_left, x_right);
    else
        printf("\nNew interval is [%.7f, %.7f]",
               x_left, x_right);
}

/* If there is a root, it is the midpoint of [x_left, x_right] */
return ((x_left + x_right) / 2.0);
}

/* Functions for which roots are sought */

/*
 *   3      2
 *  5x  - 2x  + 3
 */
double g(double x)
{
    return (5 * pow(x, 3.0) - 2 * pow(x, 2.0) + 3);
}

/*
 *   4      2
 *  x  - 3x  - 8
 */
double h(double x)
{
    return (pow(x, 4.0) - 3 * pow(x, 2.0) - 8);
}
