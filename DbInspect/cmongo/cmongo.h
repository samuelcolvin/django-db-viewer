#include "mongo.h"
#include <string.h>
#include <stdio.h>

#ifndef PYTHON
int main();
int json2bson_test();
#endif
int json_to_bson(const char *js, bson *b);

#define DEBUG 0
#if DEBUG
	#define debug(...) printf(__VA_ARGS__);
#else
	#define debug(...)
#endif
