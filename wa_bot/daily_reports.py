import zipfile
import os
import re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

from llms import llm, extract_json_from_text, PROMPT

def build_messages(chat_log):
    newline_index = chat_log.find('\n')
    if newline_index != -1:
        chat_log = chat_log[newline_index + 1:]
    chat_log = chat_log.replace('\u202f', ' ')
    pattern = r"(?i)(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}(?: (?:am|pm))? -)"
    split_log = re.split(pattern, chat_log)
    messages_list = []
    for i in range(0, len(split_log), 2):
        log = split_log[i]
        if log and ":" in log:
            message = log[log.find(':') + 1:].strip()
            messages_list.append(message)
    return messages_list


def read_whatsapp_zip(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            txt_files = [f for f in file_list if f.endswith('.txt')]
            if not txt_files:
                print("No text file found in the zip archive")
                return None, None
            chat_file = txt_files[0]
            with zip_ref.open(chat_file) as f:
                try:
                    chat_text = f.read().decode('utf-8')
                except UnicodeDecodeError:
                    chat_text = f.read().decode('utf-8', errors='ignore')
            messages = build_messages(chat_text)
            return chat_text, messages
    except FileNotFoundError:
        print(f"Error: File '{zip_path}' not found")
        return None, None
    except zipfile.BadZipFile:
        print(f"Error: '{zip_path}' is not a valid zip file")
        return None, None
    return raw_text, messages


def generate_report_image(data, date_str, output_path):
    sorted_data = sorted(data, key=lambda x: (x['present'] / x['total_mem'] * 100) if x['total_mem'] > 0 else 0, reverse=True)

    # Image dimensions - MUCH LARGER
    width = 1600
    row_height = 70
    header_height = 80
    title_height = 80
    total_height = title_height + header_height + (len(sorted_data) + 1) * row_height + 10
    
    # Create image
    img = Image.new('RGB', (width, total_height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Load fonts - MUCH BIGGER with Unicode support
    try:
        # Try fonts with good Unicode/Hindi support
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", 48)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", 36)
        data_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", 32)
        total_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", 38)
    except:
        try:
            # Fallback to DejaVu
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            data_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            total_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
        except:
            try:
                # Windows fallback
                title_font = ImageFont.truetype("arial.ttf", 48)
                header_font = ImageFont.truetype("arial.ttf", 36)
                data_font = ImageFont.truetype("arial.ttf", 32)
                total_font = ImageFont.truetype("arial.ttf", 38)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                data_font = ImageFont.load_default()
                total_font = ImageFont.load_default()
    
    # Column widths - Better proportions
    col_widths = [600, 220, 220, 220, 340]
    
    # Colors
    title_bg = (255, 182, 193)
    header_bg = (173, 216, 230)
    gold_bg = (255, 215, 0)
    silver_bg = (192, 192, 192)
    bronze_bg = (205, 127, 50)
    red_bg = (255, 0, 0)
    total_bg = (216, 191, 216)
    
    # Draw title with thick border
    draw.rectangle([0, 0, width, title_height], fill=title_bg, outline='black', width=4)
    title_text = f"Satsang Seva Report {date_str}"
    draw.text((width//2, title_height//2), title_text, fill='black', font=title_font, anchor="mm")
    
    # Draw header row
    y = title_height
    draw.rectangle([0, y, width, y + header_height], fill=header_bg, outline='black', width=3)
    headers = ["Team Name", "Total Mem", "Present", "Absent", "% Present"]
    x = 0
    for i, header in enumerate(headers):
        # Vertical lines between columns
        if i > 0:
            draw.line([(x, y), (x, y + header_height)], fill='black', width=3)
        draw.text((x + col_widths[i]//2, y + header_height//2), header, 
                  fill='black', font=header_font, anchor="mm")
        x += col_widths[i]
    
    # Right border of header
    draw.line([(width-2, y), (width-2, y + header_height)], fill='black', width=3)
    # Bottom border of header
    draw.line([(0, y + header_height), (width, y + header_height)], fill='black', width=3)
    
    # Calculate totals
    total_mem = sum(row['total_mem'] for row in sorted_data)
    total_present = sum(row['present'] for row in sorted_data)
    total_absent = sum(row['absent'] for row in sorted_data)
    
    # Draw data rows
    y = title_height + header_height
    for idx, row in enumerate(sorted_data):
        # Determine background color based on rank
        if row['total_mem'] == 0 or 'absent' in str(row.get('present', '')).lower():
            bg_color = red_bg
        elif idx == 0:
            bg_color = gold_bg
        elif idx == 1:
            bg_color = silver_bg
        elif idx == 2:
            bg_color = bronze_bg
        else:
            bg_color = 'white'
        
        # Draw row background
        draw.rectangle([0, y, width, y + row_height], fill=bg_color, outline='black', width=2)
        
        # Calculate percentage
        if row['total_mem'] > 0:
            percent = (row['present'] / row['total_mem']) * 100
        else:
            percent = 0
        
        # Draw cells
        values = [
            row['team_name'],
            str(row['total_mem']),
            str(row['present']) if row['total_mem'] > 0 else "Absent",
            str(row['absent']) if row['total_mem'] > 0 else "Absent",
            f"{percent:.8g}" if row['total_mem'] > 0 else "0"
        ]
        
        x = 0
        for i, value in enumerate(values):
            # Red background for "Absent" cells
            if value == "Absent":
                draw.rectangle([x+2, y+2, x + col_widths[i]-2, y + row_height-2], fill=red_bg)
            
            # Vertical lines between columns
            if i > 0:
                draw.line([(x, y), (x, y + row_height)], fill='black', width=2)
            
            draw.text((x + col_widths[i]//2, y + row_height//2), value, 
                      fill='black', font=data_font, anchor="mm")
            x += col_widths[i]
        
        # Right border
        draw.line([(width-2, y), (width-2, y + row_height)], fill='black', width=2)
        y += row_height
    
    # Draw total row with thick borders
    draw.rectangle([0, y, width, y + row_height], fill=total_bg, outline='black', width=4)
    total_values = ["", str(total_mem), str(total_present), str(total_absent), ""]
    x = 0
    for i, value in enumerate(total_values):
        # Vertical lines
        if i > 0:
            draw.line([(x, y), (x, y + row_height)], fill='black', width=3)
        if value:
            draw.text((x + col_widths[i]//2, y + row_height//2), value, 
                      fill='black', font=total_font, anchor="mm")
        x += col_widths[i]
    
    # Right border of total row
    draw.line([(width-2, y), (width-2, y + row_height)], fill='black', width=4)
    
    # Draw outer border - THICK
    draw.rectangle([0, 0, width-1, total_height-1], outline='black', width=5)
    
    # Save image
    img.save(output_path, quality=95)
    print(f"[+] Report saved to {output_path}")


def generate_daily_report(zip_file_path, output_folder):
    _, chats = read_whatsapp_zip(zip_path=zip_file_path)
    try:
        output_text = llm.get_llm_response(
            messages=[{
                "role": "user",
                "content": PROMPT.format(data=chats)
            }]
        )
        print(f"[Generated Output]: {output_text}")
        report_data = extract_json_from_text(output_text)
    except Exception as e:
        print(f"[ERROR in get_llm_response]: {e}")
        report_data = []

    day_today = datetime.now().strftime("%d-%m-%Y (%A)")
    jpg_output = f"DAILY REPORT {day_today}.jpg"
    jpg_output_path = os.path.join(output_folder, jpg_output)

    generate_report_image(
        data=report_data,
        date_str=day_today,
        output_path=jpg_output_path
    )

    return jpg_output


if __name__ == "__main__":
    zip_file_path = "wa report.zip"
    raw_text, messages = read_whatsapp_zip(zip_file_path)

    # if messages:
    #     for msg in messages:
    #         print(f"\n{msg}\n")
    # else:
    #     print("No messages to display")
    
    report = generate_daily_report(zip_file_path=zip_file_path, output_folder=".")

    # # Sample data matching the image
    # data = [
    #     {"team_name": "Ramnagar Tumkur", "total_mem": 30, "present": 28, "absent": 2},
    #     {"team_name": "Bidar,Kalaburgi", "total_mem": 35, "present": 31, "absent": 4},
    #     {"team_name": "Bijapur + 2 Distt", "total_mem": 13, "present": 11, "absent": 2},
    #     {"team_name": "Bgalkot", "total_mem": 16, "present": 13, "absent": 3},
    #     {"team_name": "02 SMedia(F)", "total_mem": 132, "present": 102, "absent": 30},
    #     {"team_name": "03 SMedia 7D(F)", "total_mem": 23, "present": 17, "absent": 6},
    #     {"team_name": "03 SMedia 7D(M)", "total_mem": 22, "present": 13, "absent": 9},
    #     {"team_name": "02 SMedia 8D", "total_mem": 6, "present": 3, "absent": 3},
    #     {"team_name": "Anekal", "total_mem": 60, "present": 23, "absent": 37},
    #     {"team_name": "Blore South", "total_mem": 0, "present": 0, "absent": 0},
    #     {"team_name": "Blore North", "total_mem": 0, "present": 0, "absent": 0},
    # ]
    
    # generate_report_image(data, "22-12-2025(Monday)", "satsang_report.jpg")
