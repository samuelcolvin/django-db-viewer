#include "cmongo.h"
#include "json/json.h"

void json_to_bson_append_element( bson *b , const char *k , struct json_object *v );

void json_to_bson_append_array( bson *b , struct json_object *a ) {
    int i;
    char buf[10];
    for ( i=0; i<json_object_array_length( a ); i++ ) {
        debug( buf , "%d" , i );
        json_to_bson_append_element( b , buf , json_object_array_get_idx( a , i ) );
    }
}

void json_to_bson_append( bson *b , struct json_object *o ) {
    json_object_object_foreach( o, k, v ) {
        json_to_bson_append_element( b , k , v );
    }
}

void json_to_bson_append_element( bson *b , const char *k , struct json_object *v ) {
    if ( ! v ) {
        bson_append_null( b , k );
        return;
    }

    switch ( json_object_get_type( v ) ) {
    case json_type_int:
        bson_append_int( b , k , json_object_get_int( v ) );
        break;
    case json_type_boolean:
        bson_append_bool( b , k , json_object_get_boolean( v ) );
        break;
    case json_type_double:
        bson_append_double( b , k , json_object_get_double( v ) );
        break;
    case json_type_string:
        bson_append_string( b , k , json_object_get_string( v ) );
        break;
    case json_type_object:
        bson_append_start_object( b , k );
        json_to_bson_append( b , v );
        bson_append_finish_object( b );
        break;
    case json_type_array:
        bson_append_start_array( b , k );
        json_to_bson_append_array( b , v );
        bson_append_finish_object( b );
        break;
    default:
        debug("can't handle type for : %s\n" , json_object_to_json_string( v ) );
    }
}


int json_to_bson_insert(const char *js, bson *b ) {
    struct json_object *o = json_tokener_parse( js );

    if ( is_error( o ) ) {
        debug( "\t ERROR PARSING\n" );
        return 0;
    }
    if ( ! json_object_is_type( o , json_type_object ) ) {
        debug("json_to_bson needs a JSON object, not type\n" );
        return 0;
    }
    json_to_bson_append( b , o );
    return 1;
}

int json_to_bson(const char *js, bson *b ) {
    debug("----\nJSON: %s\n" , js );

    bson_init( b );
    int success = json_to_bson_insert( js, b);
    if(!success){
    	debug("json_to_bson_insert error\n");
    }
    bson_finish( b );
    if (DEBUG && success){
    	debug("BSON: \n");
    	bson_print( b);
    }
    return success;
}

void json_to_bson_test(char *js){
	bson b[1];
	json_to_bson(js, b);
    bson_destroy( b );
}

int json2bson_test(void) {
    json_to_bson_test("1");
    json_to_bson_test("{'array' : [1, 2, 3] }");
    json_to_bson_test("{ 'x' : true }");
    json_to_bson_test("{ 'x' : null }");
    json_to_bson_test("{ 'x' : 5.2 }");
    json_to_bson_test("{ 'x' : 'eliot' }");
    json_to_bson_test("{ 'x' : 5.2 , 'y' : 'truth' , 'z' : 1.1 }");
    json_to_bson_test("{ 'x' : 4 }");
    json_to_bson_test("{ 'x' : 5.2 , 'y' : 'truth' , 'z' : 1 }");
    json_to_bson_test("{ 'x' : 'eliot' , 'y' : true , 'z' : 1 }");
    json_to_bson_test("{ 'a' : { 'b' : 1.1 } }");
    json_to_bson_test("{ 'x' : 5.2 , 'y' : { 'a' : 'eliot' , 'b' : true } , 'z' : null }");
    json_to_bson_test("{ 'x' : 5.2 , 'y' : [ 'a' , 'eliot' , 'b' , true ] , 'z' : null }");
    return 1;
}

//int main() {
//	json2bson_test();
//}
