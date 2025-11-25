import argparse
import json
import time
import urllib.request
import urllib.error

def normalize_url(u):
    return u.replace('/:', ':').strip().strip('"').strip("'")

def create_user(url, username, password, auth_token, timeout):  
    payload = json.dumps({"username": username, "password": password}).encode('utf-8')
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = auth_token
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore') if hasattr(e, 'read') else ''
        return e.code, body
    except Exception as e:
        return None, str(e)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', default='http://36.248.221.176:7200/uc/users/create')
    ap.add_argument('--username-prefix', default='third_account_')
    ap.add_argument('--start', type=int, default=1)
    ap.add_argument('--count', type=int, default=100)
    ap.add_argument('--pad', type=int, default=2)
    ap.add_argument('--password', default='dwsj.cn')
    ap.add_argument('--auth-token', default='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjQwMzc1MzQsInN1YiI6IjM1MGJiMjEzMzdiZjQ5Yjg5NWJjYmQxOGMwZTE1NmY1IiwianRpIjoiYWY1MGVhODQ4MTAwNDU0NmE0ZGUxNjI3ZmI5YzNhYTMifQ.YJdvyPPxi3kB_TPGRny7Qscrk4bLdK9AZcmgPjbTNx8')
    ap.add_argument('--sleep', type=float, default=0.2)
    ap.add_argument('--timeout', type=int, default=10)
    args = ap.parse_args()

    url = normalize_url(args.base_url)
    results = []
    for i in range(args.start, args.start + args.count):
        uname = f"{args.username_prefix}{str(i).zfill(args.pad)}"
        status, body = create_user(url, uname, args.password, args.auth_token, args.timeout)
        results.append({"username": uname, "status": status, "response": body[:1000] if isinstance(body, str) else body})
        if args.sleep > 0:
            time.sleep(args.sleep)
    print(json.dumps({"created": results}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()