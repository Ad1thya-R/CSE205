#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
   name: TODO
   userid: TODO

   Why is hexadecimal a useful display format for systems programmers?
   TODO
 */

/*
   Simple programmer's calculator for a given wordsize (given on the command
   line, defaulting to 8). Use the command-line option "-e" to echo input to
   stdout (useful for testing). The command-line option "-d" can be used
   to active a "debug mode" where extra information is displayed.

   Accepts integers in binary (0b0001), hexadecimal (0x0001), and
   (signed) decimal (42, -7). Ignores underscores.

   Five commands:

   1. Single integer: prints it in binary, hexadecimal, unsigned decimal,
      and signed decimal. For binary and hexadecimal, inserts an underscore
      every 4 digits.

   2. Unary prefix operator (!, ~, -) and an integer.

   3. Two integers separated by spaces and a binary infix operator from C.
      Prints the condition flags after +, -, &, ^.

   4. The command "wordsize" followed by an integer: changes the wordsize.

   5. The command "quit": ends the program.

   Guidelines
   - Prefer simplicity and clarity to efficiency.

   - Use ONLY the three functions in the submitted solution:
       putchar  outputs a character to stdout
       puts     outputs a string followed by a newline to stdout
       fputs    outputs a string to the given channel (e.g., "stdout").

     Feel free to use other functions (e.g., printf) for debugging.

   - For information on character encodings, see: man ascii
 */

int debug = 0;

void illegal_value_warning(void)
{
    puts("Malformed value: treating as zero.");
}

enum operation {
    AND = 1,
    XOR = 2,
    ADD = 3,
};

// Only keep the least-significant wordsize bits, set the others to zero.
// E.g., if wordsize = 8, truncate(1100_1001_0101)
//				 =      1001_0101.
unsigned int truncate(unsigned int x, int wordsize)
{
    if (wordsize == (8 * sizeof(int))) return x;
    return x & ((1U << wordsize) - 1);
}

// Return 1 if the least-significant wordsize bits represent a negative
// number (in 2s complement representation).
int is_negative(unsigned int x, int wordsize)
{
    int r = 0;
    // TODO
    return r;
}

// Print wordsize binary digits
// with an underscore every 4 digits (from the least-significant digit)
// e.g., 11_0000, NOT 1100_00
void print_binary(unsigned int n, int wordsize)
{
    // TODO
}

// Convert a string of '0's and '1's into an unsigned integer value.
// Ignore '_'s. If any other character is encountered, call
// illegal_value_warning() and return 0.
unsigned int from_binary_string(const char* str)
{
    int r = 0;
    // TODO
    return r;
}

// Print the wordsize least-significant bits in (lower-case) hexadecimal,
// with leading zeros and an underscore every 4 digits (from the
// least-significant digit), e.g., f0_2ea7, NOT f02e_a7.
void print_hexadecimal(unsigned int n, int wordsize)
{
    // TODO
}

// Convert a string of (upper-case or lower-case) hexadecimal digits into
// an unsigned integer value.
// Ignore '_'s. If any other character is encountered, call
// illegal_value_warning() and return 0.
unsigned int from_hexadecimal_string(const char* str)
{
    int r = 0;
    // TODO
    return r;
}

// Calculate pow(10, floor(log10(n)))
unsigned int upperbound10(unsigned int n)
{
    int r = 1;

    while (n >= 10) {
	r = r * 10;
	n = n / 10;
    }

    return r;
}

// Prints the wordsize least-significant bits of an unsigned integer in
// decimal without leading zeros or underscores.
void print_unsigned_decimal(unsigned int n)
{
    int d = upperbound10(n);

    while (d > 0)
    {
	putchar('0' + ((n / d) % 10));
	d = d / 10;
    }
}

// Prints the wordsize least-significant bits of a signed integer in
// decimal without leading zeros or underscores.
void print_signed_decimal(unsigned int n, int wordsize)
{
    if (is_negative(n, wordsize)) {
	putchar('-');
	n = truncate(~n + 1, wordsize);
    }
    print_unsigned_decimal(n);
}

// Convert a string of decimal digits, possibly prefixed by a '-', into
// 2s complement representation.
unsigned int from_decimal_string(const char* str)
{
    int i = 0, r = 0;
    int add = 1;

    if (str[i] == '-') {
	add = 0;
	i = 1;
    }

    for (; str[i]; ++i) {
	r *= 10;

	if ('0' <= str[i] && str[i] <= '9') {
	    if (add) {
		r += (str[i] - '0');
	    } else {
		r -= (str[i] - '0');
	    }
	} else {
	    illegal_value_warning();
	    return 0;
	}
    }

    return (unsigned int)r;
}

// Assume that the processor just calculated r = x + y in wordsize bits,
// print the value (0 or 1) of the four condition codes. See 3.6.1 of
// Bryant and O'Halloran:
//
// CF: Carry flag. The most recent operation generated a carry out of the
// most significant bit. Used to detect overflow for unsigned operations.
//
// ZF: Zero flag. The most recent operation yielded zero.
//
// SF: Sign flag. The most recent operation yielded a negative value.
//
// OF: Overflow flag. The most recent operation caused a two's-complement
// overflow--either negative or positive.
void print_condition_codes(enum operation last_op,
			   unsigned int x, unsigned int y, unsigned int r,
			   int wordsize)
{
    // TODO
}

// parse an integer
unsigned int from_number(const char* str, int wordsize)
{
    unsigned int r;

    if (str == NULL || str[0] == '\0') return 0;

    if (strncmp(str, "0b", 2) == 0) {
	r = from_binary_string(str + 2);
    } else if (strncmp(str, "0x", 2) == 0) {
	r = from_hexadecimal_string(str + 2);
    } else {
	r = from_decimal_string(str);
    }

    return truncate(r, wordsize);
}

// Print an integer in binary, hexadecimal, usigned decimal, and signed
// decimal
void print_integer(unsigned int x, int wordsize)
{
    x = truncate(x, wordsize);

    fputs("0b", stdout);
    print_binary(x, wordsize);
    fputs("    0x", stdout);
    print_hexadecimal(x, wordsize);
    fputs(" (unsigned: ", stdout);
    print_unsigned_decimal(x);
    fputs(", signed: ", stdout);
    print_signed_decimal(x, wordsize);
    puts(")");
}

// Update the global wordsize variable with range checking.
int update_wordsize(int n, int wordsize)
{
    if (n <= 0 || n > (sizeof(int) * 8)) {
	puts("ignoring invalid word size.");
	return wordsize;
    } else {
	return n;
    }
}

// Print minimum and maximum values for the current wordsize
void print_limits(int wordsize)
{
    fputs("INT_MIN=", stdout);
    print_signed_decimal(truncate(1U << (wordsize - 1), wordsize), wordsize);
    fputs(" INT_MAX=", stdout);
    print_signed_decimal(truncate(~(1U << (wordsize - 1)), wordsize), wordsize);
    fputs(" UINT_MAX=", stdout);
    print_unsigned_decimal(truncate(~0U, wordsize));
}

// Word separators
static const char *delim = " \t\r\n";

int main(int argc, char** argv)
{
    static char inputline[200];
    char *arg1, *arg2, *arg3;
    unsigned int x, y, r;
    int subtract, show_condition_codes;
    enum operation last_op;
    int echo = 0;
    int wordsize = 8;

    // Check command-line arguments
    while (*(++argv)) {
	if (strcmp(*argv, "-e") == 0) {
	    echo = 1;
	} else if (strcmp(*argv, "-d") == 0) {
	    debug = 1;
	} else if ((*argv)[0] != '-') {
	    wordsize = update_wordsize(from_number(*argv, 8), wordsize);
	}
    }

    // Welcome message
    fputs("Welcome to calc (", stdout);
    print_limits(wordsize);
    puts(")");

    // Main read-eval loop
    while (1) {
	// prompt and read input
	putchar('\n');
	print_unsigned_decimal(wordsize);
	fputs(" > ", stdout);
	if (fgets(inputline, sizeof(inputline), stdin) == NULL) break;
	if (echo) fputs(inputline, stdout);

	arg1 = strtok(inputline, delim);
	arg2 = strtok(NULL, delim);
	arg3 = strtok(NULL, delim);

	if (arg1 == NULL) continue;
	
	if (strcmp(arg1, "quit") == 0) break;

	subtract = 0;
	show_condition_codes = 0;

	if (arg2 == NULL) {
	    // parse and print number
	    r = from_number(arg1, wordsize);

	} else if (strcmp(arg1, "wordsize") == 0) {
	    // update the wordsize
	    wordsize = update_wordsize(from_number(arg2, 8), wordsize);
	    print_limits(wordsize);
	    putchar('\n');
	    continue;

	} else if (strcmp(arg1, "~") == 0
		   || strcmp(arg1, "!") == 0
		   || strcmp(arg1, "-") == 0) {
	    // unary operator
	    x = from_number(arg2, wordsize);

	    if (arg1[0] == '~') {
		r = ~x; /* bitwise complement */
	    } else if (arg1[0] == '!') {
		r = !x; /* logical negation */
	    } else {
		r = -x;	/* negation */
	    }

	    puts(arg1);
	    print_integer(x, wordsize);

	} else {
	    // binary operator

	    x = from_number(arg1, wordsize);
	    y = from_number(arg3, wordsize);

	    if (strcmp(arg2, "^") == 0) {
		r = x ^ y;
		last_op = XOR;
		show_condition_codes = 1;
	    } else if (strcmp(arg2, "&") == 0) {
		r = x & y;
		last_op = AND;
		show_condition_codes = 1;
	    } else if (strcmp(arg2, "|") == 0) {
		r = x | y;
	    } else if (strcmp(arg2, "&&") == 0) {
		r = x && y;
	    } else if (strcmp(arg2, "||") == 0) {
		r = x || y;
	    } else if (strcmp(arg2, "+") == 0) {
		r = x + y;
		last_op = ADD;
		show_condition_codes = 1;
	    } else if (strcmp(arg2, "-") == 0) {
		r = x - y;
		subtract = 1;
		last_op = ADD;
		show_condition_codes = 1;
	    } else if (strcmp(arg2, "*") == 0) {
		r = x * y;
	    } else if (strcmp(arg2, "<<") == 0) {
		r = x << y;
	    } else if (strcmp(arg2, ">>") == 0) {
		r = x >> y;
	    } else if (strcmp(arg2, "==") == 0) {
		r = x == y;
	    } else if (strcmp(arg2, "<=") == 0) {
		r = x <= y;
	    } else if (strcmp(arg2, "<") == 0) {
		r = x < y;
	    } else if (strcmp(arg2, ">=") == 0) {
		r = x >= y;
	    } else if (strcmp(arg2, ">") == 0) {
		r = x > y;
	    } else {
		puts("unknown operator");
		continue;
	    }

	    print_integer(x, wordsize);
	    puts(arg2);
	    print_integer(y, wordsize);
	}

	// print the results
	fputs("--------------------------------------", stdout);
	puts("--------------------------------------");

	r = truncate(r, wordsize);
	print_integer(r, wordsize);
	if (show_condition_codes)
	    print_condition_codes(last_op, x,
		    truncate(subtract ? -y : y, wordsize),
		    r, wordsize);
    }

    puts("ciao");
    return 0;
}

