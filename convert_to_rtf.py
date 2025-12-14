import json
import sys
import os
import tempfile
import shutil

def escape_unicode_to_rtf(text):
    """
    Converts non-ASCII characters in a string to RTF Unicode escape sequences.
    """
    escaped_text = []
    for char in text:
        if ord(char) > 127:  # Check if character is non-ASCII
            # Use an empty group '{}' as a delimiter after the Unicode escape sequence.
            # This is a standard RTF idiom to delimit control words without rendering a space.
            escaped_text.append(r"\u{}\'3f{{}}".format(ord(char)))
        else:
            escaped_text.append(char)
    return "".join(escaped_text)

def convert_txt_to_rtf(txt_file_path, rtf_file_path, video_info=None):
    """
    Converts a plain text file to a simple RTF file.
    If video_info is provided, it prepends the information with specific RTF formatting.
    """
    try:
        # If video_info is not directly passed, try to load it from video_info.json
        if video_info is None:
            temp_dir = os.environ.get('GEMINI_TEMP_DIR', '.')
            video_info_path = os.path.join(temp_dir, 'video_info.json')
            if os.path.exists(video_info_path):
                try:
                    with open(video_info_path, 'r', encoding='utf-8') as f:
                        video_info = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Error decoding video_info.json: {e}", file=sys.stderr)
                    video_info = None
            else:
                print(f"video_info.json not found at {video_info_path}. Proceeding without video information.", file=sys.stderr)

        with open(txt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Process content with OpenAI
        import llm_processor
        content = llm_processor.process_text_with_openai(content)

        rtf_lines = []
        # Re-added \ansicpg65001. Using \uc0 to disable Unicode processing for standard text
        # and \uc1\uN? for actual Unicode characters, making it explicit.
        rtf_lines.append(r"{\rtf1\ansi\ansicpg65001\deff0\nouicompat")
        rtf_lines.append(r"{\fonttbl{\f0\fnil\fcharset0 Calibri;}}")
        rtf_lines.append(r"{\generator Riched20 10.0.19041}\viewkind4 ") # Removed \uc1 from here
        
        # Define RTF styles
        # Added \uc1 prefix to each block that potentially contains unicode characters
        H1_STYLE_START = r"\pard\sa200\sl276\slmult1\b\fs48\uc1 "
        H1_STYLE_END = r"\par\par\uc0 " # Added \uc0 to revert to default after
        
        H2_STYLE_START = r"\pard\sa200\sl276\slmult1\b\fs36\uc1 "
        H2_STYLE_END = r"\par\par\uc0 " # Added \uc0 to revert to default after

        NORMAL_STYLE_START = r"\pard\sa200\sl276\slmult1\f0\fs22\lang9\uc1 "
        NORMAL_STYLE_END = r"\par\par\uc0 " # Added \uc0 to revert to default after


        if video_info:
            sermon_title = escape_unicode_to_rtf(video_info.get("sermon_title", "N/A"))
            preacher = escape_unicode_to_rtf(video_info.get("preacher", "N/A"))
            place_of_event = escape_unicode_to_rtf(video_info.get("place_of_event", "N/A"))
            date = escape_unicode_to_rtf(video_info.get("date", "N/A"))

            # Add sermon title as Header1
            rtf_lines.append(H1_STYLE_START + f"{sermon_title}" + r"\b0" + H1_STYLE_END)
            
            # Add preacher as Header2
            rtf_lines.append(H2_STYLE_START + f"{preacher}" + r"\b0" + H2_STYLE_END)

            # Add date and place as Normal
            rtf_lines.append(NORMAL_STYLE_START + f"{date}, {place_of_event}" + NORMAL_STYLE_END)
        
        # Add "Shrnutí" header
        rtf_lines.append(H2_STYLE_START + "Shrnutí" + r"\b0" + H2_STYLE_END)

        # Append the original transcription content, escaping Unicode characters
        rtf_lines.append(NORMAL_STYLE_START + escape_unicode_to_rtf(content).replace('\n', r'\par ')
 + r"\par }")
        
        rtf_content = "".join(rtf_lines)


        # Write with utf-8, no BOM
        # Use a temporary file in GEMINI_TEMP_DIR to write, then move it to the final destination
        temp_dir = os.environ.get('GEMINI_TEMP_DIR', '.')
        temp_rtf_file_path = os.path.join(temp_dir, os.path.basename(rtf_file_path) + ".tmp")

        with open(temp_rtf_file_path, 'w', encoding='utf-8') as f:
            f.write(rtf_content)

        # Remove the original RTF file if it exists, to prevent permission errors during move
        if os.path.exists(rtf_file_path):
            try:
                os.remove(rtf_file_path)
            except OSError as e:
                print(f"Warning: Could not remove existing RTF file {rtf_file_path}: {e}", file=sys.stderr)
                # If removal fails, we might still encounter issues, but try to proceed.

        shutil.move(temp_rtf_file_path, rtf_file_path)

        print(f"Successfully converted '{txt_file_path}' to '{rtf_file_path}'")

    except Exception as e:
        print(f"Error converting file: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        convert_txt_to_rtf(sys.argv[1], sys.argv[2])
    else:
        convert_txt_to_rtf("audio.txt", "audio.rtf")