// Exercise the pinned upstream schema converter offline, without loading model weights.
#include "json-schema-to-grammar.h"
#include <iostream>
#include <iterator>

int main() {
    const std::string input((std::istreambuf_iterator<char>(std::cin)), std::istreambuf_iterator<char>());
    const auto schema = common_json::parse(input);
    std::cout << json_schema_to_grammar(schema, true);
}
