# TREC
Tools for the TREC Web tracks.

## Classes
- An instance of `Query`, `q`, is a dictionary of strings where `q[query_id] = query` .
- An instance of `Relevance`, `r`, is a nested dictionary where `r[query_id][intent_id][document_id] = relevance` .
- An instance of `Result`, `r`, is a nested dictionary where `r[query_id][measure] = score` .
- An instance of `Run`, `r`, is a dictionary of lists where `r[query_id][index] = document_id` .

## Methods
- The `read(path)` methods read the file at `path` in the format for TREC Web tracks.
- The `write(path)` methods write the instance to the file at `path` in the format for TREC Web tracks.
