#ifdef PYTHON
#include <Python.h>
#endif
#include "cmongo.h"

typedef int (*debug_func)(const char *, ...);

#define BLOCK 20000000
struct BigStr {
	size_t buffer_size;
	char* buffer;
	char* buftemp;
	int curr_size;
};

int mon_connect(mongo *conn, const char * host, const int port);
char* all_query(const char* host, const int port, const char* collection);
char* filter_query(const char* host, const int port, const char* collection,
		bson* query);
char* filter_query_json(const char* host, const int port,
		const char* collection, const char* json);
void str_headings(const char *data, struct BigStr *bs);
void str_row(const char *data, struct BigStr *bs);
void debug_head(const char* str);
void adjust_size(struct BigStr *bs);

#ifdef PYTHON
static PyObject * py_all_query(PyObject *self, PyObject *args);
static PyObject * py_filter_query(PyObject *self, PyObject *args);

static PyMethodDef module_functions[] = {
	{	"all_query", py_all_query, METH_VARARGS, "CSV string of entire collection"},
	{	"filter_query", py_filter_query, METH_VARARGS, "CSV string of filtered collection"},
	{	NULL, NULL, 0, NULL}
};

static PyObject *JsonParseError;
PyMODINIT_FUNC initcmongo(void)
{
    PyObject *m;
	m = Py_InitModule("cmongo", module_functions);

    if (m == NULL)
        return;

    JsonParseError = PyErr_NewException("py_filter_query.error", NULL, NULL);
    Py_INCREF(JsonParseError);
    PyModule_AddObject(m, "error", JsonParseError);
}

static PyObject * py_all_query(PyObject *self, PyObject *args)
{
	const char *host;
	const int port;
	const char *collection;

	if (!PyArg_ParseTuple(args, "sis:all_query", &host, &port, &collection))
	return NULL;
	char* result = all_query(host, port, collection);
	return Py_BuildValue("s", result);
}

static PyObject * py_filter_query(PyObject *self, PyObject *args)
{
	const char *host;
	const int port;
	const char *collection;
	const char *json;

	if (!PyArg_ParseTuple(args, "siss:filter_query", &host, &port, &collection, &json))
		return NULL;

	bson query[1];
	if (!json_to_bson(json, query)){
		PyErr_SetString(JsonParseError, "Failed to Parse Json");
		return NULL;
	}

	char* result = filter_query(host, port, collection, query);
	bson_destroy(query);
	return Py_BuildValue("s", result);
}
#endif

#ifndef PYTHON
int main(void) {
	debug("JSON TEST:\n------------\n------------\n");
	json2bson_test();
	debug("\n------------\n------------\n");
	char collection[] = "markets.markets_trace"; //
	debug("Testing with '%s':\n", collection);
	char host[] = "127.0.0.1";
	int port = 27017;
	debug("All Results:\n");
	char* result1 = all_query(host, port, collection);
	debug_head(result1);
	if (result1 == '\0') {
		free(result1);
	}
	bson query[1];
	bson_init(query);
	bson_append_int(query, "exchange_id", 1);
	bson_finish(query);
	debug("BSON Filtered Results:\n");
	char* result2 = filter_query(host, port, collection, query);
	debug_head(result2);
	if (result2 == '\0') {
		free(result2);
	}
	debug("JSON Filtered Results:\n");
	char* result3 = filter_query_json(host, port, collection,
			"{ \"exchange_id\": 1 }");
	debug_head(result3);
	if (result3 == '\0') {
		free(result3);
	}
	return 1;
}
#endif

void debug_head(const char* str) {
	if (str == NULL) {
		debug("HEAD DEBUG: string null\n");
		return;
	}
	if (str[0] == '\0') {
		debug("HEAD DEBUG: blank string\n");
		return;
	}
	int l = 10000;
	if (l > strlen(str))
		l = strlen(str) + 1;
	char substr[l];
	memcpy(substr, str, l);
	debug("HEAD DEBUG: (total length: %d)\n", (int) strlen(str));
	debug("'%s'\n", substr);
}

char* all_query(const char* host, const int port, const char* collection) {
	bson *query = NULL;
	char* result = filter_query(host, port, collection, query);
	return result;
}

char* filter_query_json(const char* host, const int port,
		const char* collection, const char* json) {
	bson query[1];
	json_to_bson(json, query);
	char* result = filter_query(host, port, collection, query);
	bson_destroy(query);
	return result;
}

char* filter_query(const char* host, const int port, const char* collection,
		bson* query) {
	mongo conn;
	struct BigStr bs;
	bs.buffer_size = BLOCK;
	bs.buffer = (char*) malloc(bs.buffer_size);
	bs.buftemp = bs.buffer;
	bs.curr_size = 0;
	int e = mon_connect(&conn, host, port);
	if (e != 1) {
		return "ERROR";
	}
	mongo_cursor cursor[1];
	mongo_cursor_init(cursor, &conn, collection);
	if (query != NULL) {
		mongo_cursor_set_query(cursor, query);
	}
	int i = 0;
	while (mongo_cursor_next(cursor) == MONGO_OK) {
		const bson *b = &cursor->current;
		if (i == 0) {
			str_headings(b->data, &bs);
			bs.buftemp = bs.buffer + bs.curr_size;
			bs.curr_size += sprintf(bs.buftemp, "\n");
		}
		str_row(b->data, &bs);
		bs.buftemp = bs.buffer + bs.curr_size;
		bs.curr_size += sprintf(bs.buftemp, "\n");
		adjust_size(&bs);
		i++;
	}
	debug("buffer_size: %d\n", (int)bs.buffer_size);
	bs.buffer = realloc(bs.buffer, strlen(bs.buffer + 1));
	mongo_cursor_destroy(cursor);
	mongo_destroy(&conn);
	return bs.buffer;
}

void adjust_size(struct BigStr *bs) {
	if ((bs->buffer_size - bs->curr_size) < BLOCK) {
		bs->buffer_size += BLOCK;
		bs->buffer = realloc(bs->buffer, bs->buffer_size);
	}
}

int mon_connect(mongo *conn, const char * host, const int port) {
	if (mongo_client(conn, host, port) != MONGO_OK) {
		switch (conn->err) {
		case MONGO_CONN_SUCCESS:
			break;
		case MONGO_CONN_NO_SOCKET:
			debug("FAIL: Could not create a socket.\n");
			return 0;
		case MONGO_CONN_FAIL:
			debug(
					"FAIL: Could not connect to mongo. Make sure mongo is listening at: '%s' port %i\n",
					host, port);
			return 0;
		default:
			debug("MongoDB connection error number %d.\n", conn->err);
			return 0;
		}
	}
	debug("CONNECTED TO %s:%d\n", host, port);
	return 1;
}

void str_headings(const char *data, struct BigStr *bs) {
	const char *key;
	bson_iterator i;
	bson_iterator_from_buffer(&i, data);

	while (bson_iterator_next(&i)) {
		bson_type t = bson_iterator_type(&i);
		if (t == 0)
			break;
		key = bson_iterator_key(&i);
		if (key[0] == '\0')
			continue;
		bs->buftemp = bs->buffer + bs->curr_size;
		bs->curr_size += sprintf(bs->buftemp, "%s, ", key);
	}
}

void str_row(const char *data, struct BigStr *bs) {
	const char *key;
	bson_timestamp_t ts;
	char oidhex[25];
	bson_iterator i;
	bson_iterator_from_buffer(&i, data);
	while (bson_iterator_next(&i)) {
		bson_type t = bson_iterator_type(&i);
		if (t == 0)
			break;
		key = bson_iterator_key(&i);
		if (key[0] == '\0')
			continue;
		bs->buftemp = bs->buffer + bs->curr_size;
		switch (t) {
		case BSON_DOUBLE:
			bs->curr_size += sprintf(bs->buftemp, "%f",
					bson_iterator_double(&i));
			break;
		case BSON_STRING:
			bs->curr_size += sprintf(bs->buftemp, "%s",
					bson_iterator_string(&i));
			break;
		case BSON_SYMBOL:
			bs->curr_size += sprintf(bs->buftemp, "%s",
					bson_iterator_string(&i));
			break;
		case BSON_OID:
			bson_oid_to_string(bson_iterator_oid(&i), oidhex);
			bs->curr_size += sprintf(bs->buftemp, "%s", oidhex);
			break;
		case BSON_BOOL:
			bs->curr_size += sprintf(bs->buftemp, "%s",
					bson_iterator_bool(&i) ? "true" : "false");
			break;
		case BSON_DATE:
			bs->curr_size += sprintf(bs->buftemp, "%ld",
					(long int) bson_iterator_date(&i));
			break;
		case BSON_REGEX:
			bs->curr_size += sprintf(bs->buftemp, "%s",
					bson_iterator_regex(&i));
			break;
		case BSON_CODE:
			bs->curr_size += sprintf(bs->buftemp, "%s", bson_iterator_code(&i));
			break;
		case BSON_BINDATA:
			bs->curr_size += sprintf(bs->buftemp, "BSON_BINDATA");
			break;
		case BSON_UNDEFINED:
			bs->curr_size += sprintf(bs->buftemp, "BSON_UNDEFINED");
			break;
		case BSON_NULL:
			bs->curr_size += sprintf(bs->buftemp, "BSON_NULL");
			break;
		case BSON_INT:
			bs->curr_size += sprintf(bs->buftemp, "%d", bson_iterator_int(&i));
			break;
		case BSON_LONG:
			bs->curr_size += sprintf(bs->buftemp, "%ld",
					(long) bson_iterator_long(&i));
			break;
		case BSON_TIMESTAMP:
			ts = bson_iterator_timestamp(&i);
			bs->curr_size += sprintf(bs->buftemp, "i: %d, t: %d", ts.i, ts.t);
			break;
//         case BSON_CODEWSCOPE:
//             bs->curr_size += sprintf(bs->buftemp, "BSON_CODE_W_SCOPE: %s", bson_iterator_code( &i ) );
//             bson_iterator_code_scope_init( &i, &scope, 0 );
//             bs->curr_size += sprintf(bs->buftemp, "\n\t SCOPE: " );
//             bson_print( &scope );
//             bson_destroy( &scope );
//             break;
//         case BSON_OBJECT:
//         case BSON_ARRAY:
//             bs->curr_size += sprintf(bs->buftemp, "\n" );
//             bson_print_raw( bson_iterator_value( &i ) , depth + 1 );
//             break;
		default:
			bs->curr_size += sprintf(bs->buftemp, "?");
			debug("missing type: %d\n", t);
		}
		bs->buftemp = bs->buffer + bs->curr_size;
		bs->curr_size += sprintf(bs->buftemp, ", ");
		adjust_size(bs);
	}
}
