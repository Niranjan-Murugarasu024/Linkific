import json
from src.processors.file_processor import read_file
def test_json_batch_reader(tmp_path):
    p=tmp_path/"x.json"; p.write_text(json.dumps([{"id":1},{"id":2},{"id":3}]))
    batches=list(read_file(p,chunksize=2))
    assert [len(x) for x in batches]==[2,1]
