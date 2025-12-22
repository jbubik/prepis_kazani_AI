
import re
import json
import sys
import os

def extract_yt_initial_data(html_content):
    match = re.search(r'var ytInitialData = (\{.*?\});', html_content, re.DOTALL)
    if match:
        json_string = match.group(1)
        json_string = json_string.strip().rstrip(';')
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}", file=sys.stderr)
            print(f"Problematic JSON string (start): {json_string[:500]}", file=sys.stderr)
            print(f"Problematic JSON string (end): {json_string[-500:]}", file=sys.stderr)
            return None
    return None

def get_latest_video_info(data):
    try:
        for tab in data['contents']['twoColumnBrowseResultsRenderer']['tabs']:
            if 'tabRenderer' in tab and tab['tabRenderer'].get('selected') == True and tab['tabRenderer'].get('title') == 'Živě':
                if 'content' in tab['tabRenderer'] and 'richGridRenderer' in tab['tabRenderer']['content']:
                    first_item = tab['tabRenderer']['content']['richGridRenderer']['contents'][0]['richItemRenderer']
                    if 'content' in first_item and 'videoRenderer' in first_item['content']:
                        video_renderer = first_item['content']['videoRenderer']
                        
                        full_title = video_renderer['title']['runs'][0]['text']
                        
                        parts = [p.strip() for p in full_title.split('|')]
                        
                        place_of_event = parts[0] if len(parts) > 0 else "N/A"
                        preacher = parts[1] if len(parts) > 1 else "N/A"
                        sermon_title = parts[2] if len(parts) > 2 else full_title
                        
                        description_snippet = video_renderer['descriptionSnippet']['runs'][0]['text']
                        date_match = re.search(r'\d{1,2}\.\d{1,2}\.\d{4}', description_snippet)
                        date = date_match.group(0) if date_match else "N/A"

                        return {
                            "place_of_event": place_of_event,
                            "preacher": preacher,
                            "sermon_title": sermon_title,
                            "date": date
                        }
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing YouTube data structure: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    try:
        temp_dir = os.environ.get('TEMP_BASE', '.')
        youtube_html_path = os.path.join(temp_dir, 'youtube.html')

        with open(youtube_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        yt_initial_data = extract_yt_initial_data(html_content)

        if yt_initial_data:
            video_info = get_latest_video_info(yt_initial_data)
            if video_info:
                output_file = os.path.join(temp_dir, 'video_info.json')
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(video_info, f, ensure_ascii=False, indent=4)
                print(f"Video information saved to {output_file}")
            else:
                print("Could not find the latest video information.", file=sys.stderr)
        else:
            print("Could not extract ytInitialData.", file=sys.stderr)
    except FileNotFoundError:
        print(f"youtube.html not found at {youtube_html_path}. Please ensure the file exists.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
