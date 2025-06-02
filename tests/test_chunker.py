from utils.chunker import chunk_diff

def test_chunk_diff_basic_add_remove():
    diff = """@@ -1,2 +1,2 @@
-print("Hello")
+print("Hi")"""
    added, removed = chunk_diff(diff)

    assert added == [{
        'lines': [1],
        'code': 'print("Hi")'
    }]

    assert removed == [{
        'lines': [1],
        'code': 'print("Hello")'
    }]
