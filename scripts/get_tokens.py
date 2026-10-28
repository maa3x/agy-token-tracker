#!/usr/bin/env python3
import os
import sys
import json
import glob
import re
from datetime import datetime

def clean_title(raw_text):
    if not raw_text:
        return "Untitled Conversation"
    # Remove USER_REQUEST tags
    if "<USER_REQUEST>" in raw_text:
        raw_text = raw_text.split("<USER_REQUEST>")[1].split("</USER_REQUEST>")[0]
    
    # Clean whitespace and newlines
    text = " ".join(raw_text.strip().split())
    
    # Remove leading file mentions @[...]
    text = re.sub(r"^@\[.*?\]\s*", "", text)
    
    # Clean extra quotes or slash commands
    if len(text) > 80:
        text = text[:80] + "..."
    return text if text else "Untitled Conversation"

def parse_transcript(file_path):
    input_tokens = 0
    output_tokens = 0
    cache_read_tokens = 0
    turn_count = 0
    raw_prompt = ""
    start_time = None
    end_time = None

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except Exception:
                    continue

                ts = data.get("created_at")
                if ts:
                    if not start_time:
                        start_time = ts
                    end_time = ts

                if data.get("type") == "USER_INPUT" and not raw_prompt:
                    content = data.get("content", "")
                    if content and len(content.strip()) > 0:
                        raw_prompt = content.strip()

                if data.get("type") == "PLANNER_RESPONSE":
                    turn_count += 1
                    input_tokens += data.get("input_tokens", 0)
                    output_tokens += data.get("output_tokens", 0)
                    cache_read_tokens += data.get("cache_read_tokens", 0)

        total_tokens = input_tokens + output_tokens
        title = clean_title(raw_prompt)
        
        return {
            "turn_count": turn_count,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_tokens": cache_read_tokens,
            "total_tokens": total_tokens,
            "title": title,
            "first_prompt": title,
            "start_time": start_time,
            "end_time": end_time
        }
    except Exception as e:
        return None

def get_all_conversations():
    brain_dir = os.path.expanduser("~/.gemini/antigravity/brain")
    pattern = os.path.join(brain_dir, "*", ".system_generated", "logs", "transcript.jsonl")
    results = []
    
    for path in glob.glob(pattern):
        parts = path.split(os.sep)
        try:
            cid_idx = parts.index(".system_generated") - 1
            cid = parts[cid_idx]
        except Exception:
            continue

        stats = parse_transcript(path)
        if stats and (stats["total_tokens"] > 0 or stats["turn_count"] > 0):
            stats["conversation_id"] = cid
            results.append(stats)

    results.sort(key=lambda x: x["total_tokens"], reverse=True)
    return results

def get_conversation(cid):
    path = os.path.expanduser(f"~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl")
    if not os.path.exists(path):
        return None
    stats = parse_transcript(path)
    if stats:
        stats["conversation_id"] = cid
    return stats

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract token usage from Antigravity conversations")
    parser.add_argument("--conversation", "-c", help="Conversation ID")
    parser.add_argument("--json", "-j", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if args.conversation:
        data = get_conversation(args.conversation)
        if not data:
            print(json.dumps({"error": f"Conversation {args.conversation} not found"}))
            sys.exit(1)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(f"Conversation: {data['conversation_id']}")
            print(f"Title:        {data['title']}")
            print(f"Turns:        {data['turn_count']}")
            print(f"Input:        {data['input_tokens']:,}")
            print(f"Output:       {data['output_tokens']:,}")
            print(f"Cache Read:   {data['cache_read_tokens']:,}")
            print(f"Total:        {data['total_tokens']:,}")
    else:
        all_data = get_all_conversations()
        if args.json:
            print(json.dumps(all_data, indent=2))
        else:
            total_inp = sum(x["input_tokens"] for x in all_data)
            total_out = sum(x["output_tokens"] for x in all_data)
            total_cache = sum(x["cache_read_tokens"] for x in all_data)
            print(f"Total Conversations: {len(all_data)}")
            print(f"Total Input Tokens:  {total_inp:,}")
            print(f"Total Output Tokens: {total_out:,}")
            print(f"Total Cache Read:    {total_cache:,}")
            print(f"Grand Total:         {total_inp + total_out:,}\n")
            print(f"{'Title':<35} | {'Conversation ID':<36} | {'Turns':<5} | {'Input':<10} | {'Output':<8} | {'Total':<10}")
            print("-" * 115)
            for item in all_data[:15]:
                print(f"{item['title'][:34]:<35} | {item['conversation_id']:<36} | {item['turn_count']:<5} | {item['input_tokens']:<10,}"
                      f" | {item['output_tokens']:<8,} | {item['total_tokens']:<10,}")

if __name__ == "__main__":
    main()
