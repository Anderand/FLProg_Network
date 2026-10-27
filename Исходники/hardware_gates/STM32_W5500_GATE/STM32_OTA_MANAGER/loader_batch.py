"""Build reports contain only results from the current invocation."""
import concurrent.futures
import json
import threading
import time


def run(builder, targets, source, notify, libraries=None):
    started = time.time()
    report = dict(started=started, finished=None, rows={
        name: dict(status='queued', started=None, seconds=0, size=0, error='')
        for name in targets})
    lock = threading.Lock()
    output = builder.ROOT / 'last_build_report.json'
    def publish():
        snapshot = json.loads(json.dumps(report))
        temporary = output.with_suffix('.tmp')
        temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(output)
        notify(snapshot)
    publish()
    def one(name):
        with lock:
            report['rows'][name].update(status='building', started=time.time())
            publish()
        try:
            path = builder.build(name, source, libraries=libraries) if libraries else builder.build(name, source)
            result = dict(status='success', size=path.stat().st_size)
        except Exception as exc:
            result = dict(status='failed', error=str(exc))
        with lock:
            item = report['rows'][name]
            item.update(result, seconds=round(time.time()-item['started'], 1))
            publish()
    # Board builds have separate directories and log files.
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(3, len(targets))) as pool:
        list(pool.map(one, targets))
    report['finished'] = time.time()
    publish()
    return report
