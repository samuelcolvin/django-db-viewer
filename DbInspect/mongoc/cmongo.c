#include "mongo.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#define BLOCK 20000000

struct BigStr{
    size_t buffer_size ;
    char *buffer ;
    char* buffer_pntr ;
};

int monary_connect(mongo *conn, char * host, int port);
void empty_query(char * host, int port, struct BigStr *bs);
void print(char * str);
void print_headings(const char *data, struct BigStr *bs);
void print_row( const char *data, struct BigStr *bs);

int main(void) {
  struct BigStr bs;
  bs.buffer_size = BLOCK;
  bs.buffer = (char*) malloc(BLOCK);
  bs.buffer_pntr = bs.buffer;
  
  char host[]="127.0.0.1";
  empty_query(host, 27017, &bs);
  
  bs.buffer = realloc(bs.buffer, strlen(bs.buffer+1));
  char substr[5000];
  memcpy(substr, bs.buffer, 5000);
  printf("%s", substr);
}

int monary_connect(mongo *conn, char * host, int port)
{
  char s[200];
  if( mongo_client( conn, host, port ) != MONGO_OK ) {
    switch( (*conn).err ) {
      case MONGO_CONN_SUCCESS:
	return 1;
	break;
      case MONGO_CONN_NO_SOCKET:
	sprintf(s,"FAIL: Could not create a socket!");
	break;
      case MONGO_CONN_FAIL:
	sprintf(s,"FAIL: Could not connect to mongod. Make sure it's listening to the correct port.");
	break;
      default:
	sprintf(s, "MongoDB connection error number %d.", (*conn).err);
    }
    print(s);
    return 0;
  }
  print("Connected.\n");
  return 1;
}

void empty_query(char * host, int port, struct BigStr *bs) {
  mongo conn;
  int e = monary_connect(&conn, host, port);
  if( e != 1 ) {
    return;
  }
  mongo_cursor cursor[1];
  mongo_cursor_init( cursor, &conn, "markets.markets_article" );
  int i = 0;
  while( mongo_cursor_next( cursor ) == MONGO_OK ){
    const bson *b = &cursor->current;
    if (i == 0){
      print_headings( b->data, bs);
      bs->buffer_pntr += sprintf(bs->buffer_pntr, "\n" );
    }
    print_row( b->data, bs);
    bs->buffer_pntr += sprintf(bs->buffer_pntr, "\n" );
    if ((bs->buffer + bs->buffer_size - bs->buffer_pntr) < BLOCK) {
      bs->buffer_size += BLOCK;
      bs->buffer = realloc(bs->buffer, bs->buffer_size);
    }
    i++;
  }
  
  mongo_cursor_destroy( cursor );
  mongo_destroy( &conn );
}

void print(char s[])
{
  printf("%s\n",s);
  return;
}

void print_headings(const char *data, struct BigStr *bs) {
    const char *key;
    bson_iterator i;
    bson_iterator_from_buffer( &i, data);

    while ( bson_iterator_next( &i ) ) {
        bson_type t = bson_iterator_type( &i );
        if ( t == 0 )
            break;
        key = bson_iterator_key( &i );
	if (key[0] == '\0')
	  continue;
        bs->buffer_pntr += sprintf(bs->buffer_pntr, "%s, ", key);
    }
}

void print_row(const char *data, struct BigStr *bs) {
    const char *key;
    bson_timestamp_t ts;
    char oidhex[25];
//     bson scope;
    bson_iterator i;
    bson_iterator_from_buffer( &i, data );

    while ( bson_iterator_next( &i ) ) {
        bson_type t = bson_iterator_type( &i );
        if ( t == 0 )
            break;
        key = bson_iterator_key( &i );
	if (key[0] == '\0')
	  continue;
        switch ( t ) {
        case BSON_DOUBLE:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "%f" , bson_iterator_double( &i ) );
            break;
        case BSON_STRING:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "%s" , bson_iterator_string( &i ) );
            break;
        case BSON_SYMBOL:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "%s" , bson_iterator_string( &i ) );
            break;
        case BSON_OID:
            bson_oid_to_string( bson_iterator_oid( &i ), oidhex );
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "%s" , oidhex );
            break;
        case BSON_BOOL:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "%s" , bson_iterator_bool( &i ) ? "true" : "false" );
            break;
        case BSON_DATE:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "%ld" , ( long int )bson_iterator_date( &i ) );
            break;
        case BSON_REGEX:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "%s", bson_iterator_regex( &i ) );
            break;
        case BSON_CODE:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "%s", bson_iterator_code( &i ) );
            break;
        case BSON_BINDATA:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "BSON_BINDATA" );
            break;
        case BSON_UNDEFINED:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "BSON_UNDEFINED" );
            break;
        case BSON_NULL:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "BSON_NULL" );
            break;
        case BSON_INT:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "%d" , bson_iterator_int( &i ) );
            break;
        case BSON_LONG:
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "%ld" , ( long )bson_iterator_long( &i ) );
            break;
        case BSON_TIMESTAMP:
            ts = bson_iterator_timestamp( &i );
            bs->buffer_pntr += sprintf(bs->buffer_pntr, "i: %d, t: %d", ts.i, ts.t );
            break;
//         case BSON_CODEWSCOPE:
//             bs->buffer_pntr += sprintf(bs->buffer_pntr, "BSON_CODE_W_SCOPE: %s", bson_iterator_code( &i ) );
//             bson_iterator_code_scope_init( &i, &scope, 0 );
//             bs->buffer_pntr += sprintf(bs->buffer_pntr, "\n\t SCOPE: " );
//             bson_print( &scope );
//             bson_destroy( &scope );
//             break;
//         case BSON_OBJECT:
//         case BSON_ARRAY:
//             bs->buffer_pntr += sprintf(bs->buffer_pntr, "\n" );
//             bson_print_raw( bson_iterator_value( &i ) , depth + 1 );
//             break;
        default:
            bson_errprintf( "missing type: %d" , t );
        }
    bs->buffer_pntr += sprintf(bs->buffer_pntr, ", " );
    }
}