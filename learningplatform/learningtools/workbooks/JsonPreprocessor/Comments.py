WORKBOOK = {
    "name": "JsonPreprocessor.Comments",
    "questions": {
        "p1": {
            "validator": "json_object_equals",
            "expected_value": {
                "name": "JPP comments",
                "version": "1.0.0",
            },
            "source_variable": "json_object",
            "content_variable": "content",
            "parser_kwargs": {
                "syntax": "python",
            },
        },
        "p2": {
            "validator": "json_object_equals",
            "expected_value": {
                "testlist": ["A1", "D4"],
            },
            "source_variable": "json_object",
            "content_variable": "content",
            "parser_kwargs": {
                "syntax": "python",
            },
        },
    },
}
