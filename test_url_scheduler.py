import argparse
import json
import time
import urllib.request
import urllib.error
from datetime import datetime

PROVIDERS = ["bilibili", "douyin", "kuaishou", "xiaohongshu", "weibo", "xiaoyuzhou"]

def normalize_url(u):
    if not isinstance(u, str):
        return None
    s = u.strip().strip('"').strip("'").strip()
    s = s.strip('`').strip()
    return s if s else None

def load_urls(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)
    queue = {p: [] for p in PROVIDERS}
    for p in PROVIDERS:
        arr = data.get(p, []) or []
        for u in arr:
            nu = normalize_url(u)
            if nu:
                queue[p].append(nu)
    return queue

def post_url(endpoint, url, auth_token, refresh_token, timeout):
    payload = json.dumps({"url": url}).encode('utf-8')
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = auth_token
    if refresh_token:
        headers["Cookie"] = f"refresh_token={refresh_token}"
    req = urllib.request.Request(endpoint, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            code = resp.getcode()
            try:
                j = json.loads(body)
            except Exception:
                j = None
            return code, j or body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore') if hasattr(e, 'read') else ''
        return e.code, body
    except Exception as e:
        return None, str(e)

def round_robin(queue):
    order = []
    exhausted = False
    idx = 0
    while not exhausted:
        exhausted = True
        for p in PROVIDERS:
            if queue[p]:
                exhausted = False
        if exhausted:
            break
        for p in PROVIDERS:
            if queue[p]:
                order.append((p, queue[p].pop(0)))
    return order

def by_provider(queue):
    order = []
    for p in PROVIDERS:
        while queue[p]:
            order.append((p, queue[p].pop(0)))
    return order

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-json', default=r'd:\multi_modal\demo_init_data\test_url.json')
    ap.add_argument('--endpoint', default='http://36.248.221.176:8889/api/upload-task/url-file-upload')
    ap.add_argument('--count-per-10min', type=int, default=5)
    ap.add_argument('--interval-minutes', type=float, default=10.0)
    ap.add_argument('--auth-token', default='')
    ap.add_argument('--refresh-token', default='')
    ap.add_argument('--timeout', type=int, default=15)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--mode', choices=['by-provider', 'round-robin'], default='by-provider')
    ap.add_argument('--max-batches', type=int, default=0)
    ap.add_argument('--output-json', default='')
    args = ap.parse_args()

    queue = load_urls(args.input_json)
    order = by_provider(queue) if args.mode == 'by-provider' else round_robin(queue)
    per_call_sleep = max(0.0, (args.interval_minutes * 60.0) / float(max(1, args.count_per_10min)))

    results = []
    batch = 0
    i = 0
    while i < len(order):
        batch += 1
        taken = 0
        while taken < args.count_per_10min and i < len(order):
            p, u = order[i]
            ts = datetime.now().isoformat()
            if args.dry_run:
                results.append({"provider": p, "url": u, "status": "dry_run", "time": ts})
            else:
                code, resp = post_url(args.endpoint, u, args.auth_token, args.refresh_token, args.timeout)
                ok = False
                if isinstance(resp, dict):
                    ok = resp.get('code') == 0
                results.append({"provider": p, "url": u, "http": code, "ok": ok, "resp": resp, "time": ts})
            taken += 1
            i += 1
            if i < len(order) and taken < args.count_per_10min:
                time.sleep(per_call_sleep)
        if args.max_batches and batch >= args.max_batches:
            break
        if i < len(order):
            time.sleep(max(0.0, args.interval_minutes * 60.0 - per_call_sleep * args.count_per_10min))

    out = {"results": results}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if args.output_json:
        with open(args.output_json, 'w', encoding='utf-8') as w:
            json.dump(out, w, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()