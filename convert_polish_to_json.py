# 语音润色稿
import argparse
import json

def parse_line(line):
    s = line.strip()
    if not s:
        return None
    i1 = s.find(',')
    if i1 == -1:
        return None
    i2 = s.find(',', i1 + 1)
    if i2 == -1:
        return None
    speaker = s[:i1].strip()
    timestamp = s[i1 + 1:i2].strip()
    transcript = s[i2 + 1:].strip()
    if speaker.lower().startswith('speaker') and timestamp.lower().startswith('timestamp'):
        return None
    return {
        "speaker": speaker,
        "timestamp": timestamp,
        "transcript": transcript,
    }

def parse_file(path):
    items = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if idx == 0 and line.strip().lower().startswith('speaker,timestamp,transcript'):
                continue
            item = parse_line(line)
            if item:
                items.append(item)
    return items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-txt', '--input_txt', dest='input_txt', required=True)
    ap.add_argument('--output-json', '--output_json', dest='output_json', required=True)
    args = ap.parse_args()
    items = parse_file(args.input_txt)
    out = {"llm_summary": items}
    with open(args.output_json, 'w', encoding='utf-8') as w:
        json.dump(out, w, ensure_ascii=False, indent=2)
# python convert_polish_to_json.py --input-txt "d:\multi_modal\demo_init_data\AI润色稿.txt" --output-json "d:\multi_modal\demo_init_data\subtitle_improve_converted.json"
if __name__ == '__main__':
    main()