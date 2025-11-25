import argparse
import json

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-txt', '--input_txt', dest='input_txt')
    p.add_argument('--output-json', '--output_json', dest='output_json')
    a = p.parse_args()
    ip = a.input_txt or r'd:\multi_modal\demo_init_data\思维导图.txt'
    op = a.output_json or r'd:\multi_modal\demo_init_data\mind_map.json'
    with open(ip, 'r', encoding='utf-8', errors='ignore') as f:
        t = f.read()
    d = {"llm_summary": t}
    with open(op, 'w', encoding='utf-8') as w:
        json.dump(d, w, ensure_ascii=False, indent=2)

# python d:\multi_modal\demo_init_data\demo.py --input-txt "d:\multi_modal\demo_init_data\思维导图.txt" --output-json "d:\multi_modal\demo_init_data\mind_map.json"
if __name__ == '__main__':
    main()