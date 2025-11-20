import re
import json
import argparse
import os

def parse_transcript(path):
    subtitles = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tm = re.search(r'(\d{2}:\d{2}:\d{2})-(\d{2}:\d{2}:\d{2})', line)
            if not tm:
                continue
            start, end = tm.group(1), tm.group(2)
            sm = re.search(r'\bSPEAKER_\d+\b', line)
            if not sm:
                continue
            speaker = sm.group(0)
            si = line.find(speaker)
            text = line[si + len(speaker):].strip()
            if not text:
                continue
            item = {
                "start_time": start,
                "relative_start_time": start,
                "speaker": speaker,
                "original_text": text,
                "end_time": end,
                "relative_end_time": end,
            }
            subtitles.append(item)
    return subtitles

def parse_translation(path):
    texts = []
    if not path or not os.path.exists(path):
        return texts
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                texts.append("")
                continue
            sm = re.search(r'\bSPEAKER_\d+\b', line)
            if not sm:
                texts.append("")
                continue
            speaker = sm.group(0)
            si = line.find(speaker)
            text = line[si + len(speaker):].strip()
            texts.append(text)
    return texts

def write_json(subtitles, out_path):
    data = {"subtitles": subtitles}
    with open(out_path, 'w', encoding='utf-8') as w:
        json.dump(data, w, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-txt', '--input_txt', dest='input_txt', required=True)
    parser.add_argument('--translation-txt', '--translation_txt', dest='translation_txt', required=False)
    parser.add_argument('--output-json', '--output_json', dest='output_json', required=True)
    parser.add_argument('--language', '--lang', dest='language', default="")
    parser.add_argument('--source-language', '--source_language', dest='source_language', default="")
    parser.add_argument('--target-language', '--target_language', dest='target_language', default="")
    args = parser.parse_args()

    subs = parse_transcript(args.input_txt)
    translations = parse_translation(args.translation_txt) if args.translation_txt else []

    out = []
    for i, s in enumerate(subs):
        translated_text = ""
        if translations and i < len(translations):
            translated_text = translations[i] or ""
        item = {
            "language": args.language,
            "translated_text": translated_text,
            "start_time": s["start_time"],
            "relative_start_time": s["relative_start_time"],
            "speaker": s["speaker"],
            "original_text": s["original_text"],
            "source_language": args.source_language,
            "end_time": s["end_time"],
            "relative_end_time": s["relative_end_time"],
            "target_language": args.target_language
        }
        out.append(item)

    write_json(out, args.output_json)


#  python convert_transcript_to_json.py --input-txt "d:\multi_modal\demo_init_data\语音逐字稿.txt" --translation-txt "d:\multi_modal\demo_init_data\语音翻译稿.txt" --output-json "d:\multi_modal\demo_init_data\语音双语_converted.json"
if __name__ == '__main__':
    main()