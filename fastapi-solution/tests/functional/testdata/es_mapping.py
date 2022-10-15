import os

ES_MOVIES_MAPPING = {
os.environ['ELASTIC_INDEX_TO_TEST'] : {
    "mappings" : {
    "dynamic" : "strict",
    "properties" : {
        "actors" : {
        "type" : "nested",
        "dynamic" : "strict",
        "properties" : {
            "id" : {
            "type" : "keyword"
            },
            "name" : {
            "type" : "text",
            "analyzer" : "ru_en"
            }
        }
        },
        "actors_names" : {
        "type" : "text",
        "analyzer" : "ru_en"
        },
        "description" : {
        "type" : "text",
        "analyzer" : "ru_en"
        },
        "director" : {
        "type" : "text",
        "analyzer" : "ru_en"
        },
        "genre" : {
        "type" : "keyword"
        },
        "id" : {
        "type" : "keyword"
        },
        "imdb_rating" : {
        "type" : "float"
        },
        "title" : {
        "type" : "text",
        "fields" : {
            "raw" : {
            "type" : "keyword"
            }
        },
        "analyzer" : "ru_en"
        },
        "writers" : {
        "type" : "nested",
        "dynamic" : "strict",
        "properties" : {
            "id" : {
            "type" : "keyword"
            },
            "name" : {
            "type" : "text",
            "analyzer" : "ru_en"
            }
        }
        },
        "writers_names" : {
        "type" : "text",
        "analyzer" : "ru_en"
        }
    }
    }
}
}

