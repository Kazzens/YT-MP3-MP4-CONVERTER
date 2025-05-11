import yt_dlp
import os
import imageio_ffmpeg
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import sys
import time
from re import sub
import threading
import glob
import traceback

# Output folder
OUTPUT_PATH_MP3 = 'Converted-mp3'
OUTPUT_PATH_MP4 = 'Converted-mp4'
os.makedirs(OUTPUT_PATH_MP3, exist_ok=True)
os.makedirs(OUTPUT_PATH_MP4, exist_ok=True)


# Global ffmpeg path
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

# --- MP3/MP4 Download Logic ---
def download_video(url, convert_to_mp3=True):
    try:
        output_path = OUTPUT_PATH_MP3 if convert_to_mp3 else OUTPUT_PATH_MP4
        output_template = os.path.join(output_path, '%(title)s - Converted by KAZZENS.%(ext)s')

        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio' if convert_to_mp3 else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'ffmpeg_location': FFMPEG_PATH,
            'quiet': False
        }

        if convert_to_mp3:
            ydl_opts['postprocessors'] = [
                {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'
                }
            ]
            ext = 'mp3'
        else:
            ydl_opts['postprocessors'] = [
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }
            ]
            ydl_opts['merge_output_format'] = 'mp4'
            ydl_opts['postprocessor_args'] = ['-c:v', 'copy', '-c:a', 'copy']
            ext = 'mp4'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info.get('is_live'):
                return "❌ Error: Live streams are not supported."
            info = ydl.extract_info(url, download=True)
        ext = 'mp3' if convert_to_mp3 else 'mp4'  # Force mp4 if not mp3
        safe_title = sub(r'[\\/*?:"<>|]', "", info['title'])
        filename = f"{safe_title} - Converted by KAZZENS.{ext}"
        filepath = os.path.join(output_path, filename)

        # Clean up leftover .webm if it exists
        if not convert_to_mp3:
            pattern = os.path.join(output_path, f"{safe_title} - Converted by KAZZENS*.webm")
            for leftover_webm in glob.glob(pattern):
                try:
                    os.remove(leftover_webm)
                except FileNotFoundError:
                    pass

                # Strip metadata
        if os.path.exists(filepath):
            cleaned = filepath.replace(f'.{ext}', f'_clean.{ext}')
            subprocess.run([
                FFMPEG_PATH, '-i', filepath,
                '-map_metadata', '-1',
                '-c', 'copy',
                '-y', cleaned
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            try:
                os.remove(filepath)
                os.rename(cleaned, filepath)
            except Exception as e:
                print(f"⚠️ Post-clean rename failed: {e}")

        return f"✅ File downloaded: {filename}", output_path

    except Exception as e:
        return f"❌ Error: {e}\n{traceback.format_exc()}", None

# --- YouTube Search Logic ---
def search_youtube(keyword, page=1, results_per_page=10):
    try:
        offset = (page - 1) * results_per_page
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch{offset + results_per_page}:{keyword}", download=False)
            entries = search_results.get('entries', [])
            return entries[offset:offset + results_per_page]
    except Exception as e:
        return []

# --- GUI Logic ---
def show_search_gui():
    root = tk.Tk()
    root.iconbitmap('icon.ico')
    root.title("YouTube Converter by KAZZENS")
    window_width = 500
    window_height = 610

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.resizable(False, False)

    def center_popup(popup, parent):
        parent.update_idletasks()
        popup.update_idletasks()

        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        popup_width = popup.winfo_reqwidth()
        popup_height = popup.winfo_reqheight()

        x = parent_x + (parent_width // 2) - (popup_width // 2)
        y = parent_y + (parent_height // 2) - (popup_height // 2)

        popup.geometry(f"+{x}+{y}")

    search_frame = tk.Frame(root)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Enter YouTube link or keyword:", font=("Arial", 12)).pack()
    entry = tk.Entry(search_frame, width=50, font=("Arial", 10))
    entry.pack(pady=5)
    entry.bind("<Return>", lambda event: handle_submit())
    entry.focus()

    format_choice = tk.StringVar(value='mp3')
    tk.Radiobutton(search_frame, text="MP3", variable=format_choice, value='mp3', ).pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(search_frame, text="MP4", variable=format_choice, value='mp4', cursor="hand2").pack(side=tk.LEFT)

    result_frame = tk.Frame(root)
    result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollable_frame = tk.Frame(result_frame)
    scrollable_frame.pack(fill="both", expand=True)

    nav_frame = tk.Frame(root)

    prev_button = tk.Button(nav_frame, text="← Prev", state=tk.DISABLED, cursor="hand2")
    next_button = tk.Button(nav_frame, text="Next →", state=tk.DISABLED, cursor="hand2")
    current_page_label = tk.Label(nav_frame, text="Page 1", font=("Arial", 10))

    results_per_page = 10
    current_results = {"keyword": "", "page": 1}
    last_click_time = [0]

    def clear_results():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()



    def update_navigation():
        prev_button.config(state=tk.NORMAL if current_results["page"] > 1 else tk.DISABLED)
        next_button.config(state=tk.NORMAL)
        current_page_label.config(text=f"Page {current_results['page']}")

    def render_results(videos):
        clear_results()
        nav_frame.pack(pady=5)
        prev_button.grid(row=0, column=0, padx=10)
        current_page_label.grid(row=0, column=1, padx=10)
        next_button.grid(row=0, column=2, padx=10)
        clear_results()
        for video in videos:
            title = video.get('title', 'Untitled')
            url = f"https://www.youtube.com/watch?v={video.get('id')}"
            button = tk.Button(scrollable_frame, text=title, wraplength=450, anchor='w', justify='left', command=lambda u=url: on_video_click(u), cursor="hand2")
            button.pack(fill="x", padx=5, pady=3)
        update_navigation()
        search_button.config(state=tk.NORMAL)
        prev_button.config(state=tk.NORMAL if current_results["page"] > 1 else tk.DISABLED)
        next_button.config(state=tk.NORMAL)

    def load_page(page):
        videos = search_youtube(current_results["keyword"], page=page, results_per_page=results_per_page)
        if videos:
            render_results(videos)
        else:
            clear_results()
            tk.Label(scrollable_frame, text="No more results.", font=("Arial", 10)).pack(pady=10)

    def handle_submit():
        if search_button['state'] == tk.DISABLED:
            return
        text = entry.get().strip()
        now = time.time()
        if now - last_click_time[0] < 5:
            return
        last_click_time[0] = now
        search_button.config(state=tk.DISABLED)
        clear_results()

        if text.startswith("http"):
            nav_frame.pack_forget()
            filetype = format_choice.get().title()
            download_confirm = tk.Toplevel(root)
            download_confirm.title("Download")
            download_confirm.geometry("350x100")
            download_confirm.resizable(False, False)
            download_confirm.iconbitmap('icon.ico')
            center_popup(download_confirm, root)
            download_confirm.grab_set()


            msg = tk.Message(
                download_confirm,
                text=f"Would you like to convert, download, and clean the metadata of the {filetype} file?",
                font=("Arial", 10),
                width=320,
                justify="center"
            )
            msg.pack(pady=(10, 10))

            def on_accept():
                download_confirm.destroy()
                loading_popup = tk.Toplevel(root)
                loading_popup.title("Downloading")
                loading_popup.geometry("350x100")
                loading_popup.resizable(False, False)
                loading_popup.iconbitmap('icon.ico')
                center_popup(loading_popup, root)
                loading_popup.grab_set()

                tk.Label(
                    loading_popup,
                    text="Downloading, Converthing, and Cleaning...",
                    font=("Arial", 10),
                    wraplength=300,
                    justify="center"
                ).pack(expand=True, pady=25)

                root.update()
                
                def threaded_download():
                    result, output_path = download_video(text, convert_to_mp3=(format_choice.get() == 'mp3'))
                    if "Live streams are not supported" in result:
                        loading_popup.destroy()
                        messagebox.showwarning("Live Stream Blocked", result)
                        search_button.config(state=tk.NORMAL)
                        entry.delete(0, tk.END)
                        clear_results()
                        current_results["keyword"] = ""
                        current_results["page"] = 1
                        return

                    if '❌' in result:
                        messagebox.showerror("Download Failed", result)
                        return

                    filename = result.split(': ', 1)[-1]
                    filetype = filename.split('.')[-1].title()

                    if messagebox.askyesno("Download Complete", f"{filetype} file downloaded. Open now?"):
                        os.startfile(os.path.join(output_path, filename))

                    search_button.config(state=tk.NORMAL)
                    entry.delete(0, tk.END)
                    clear_results()
                    current_results["keyword"] = ""
                    current_results["page"] = 1

                threading.Thread(target=threaded_download).start()

            def on_decline():
                download_confirm.destroy()
                search_button.config(state=tk.NORMAL)

            btn_frame = tk.Frame(download_confirm)
            btn_frame.pack(pady=(0, 10))  # Space from message to buttons

            tk.Button(btn_frame, text="Yes", width=10, command=on_accept, cursor="hand2").pack(side="left", padx=20)
            tk.Button(btn_frame, text="No", width=10, command=on_decline, cursor="hand2").pack(side="right", padx=20)
            
        else:
                current_results["keyword"] = text
                current_results["page"] = 1

                def threaded_search():
                    videos = search_youtube(current_results["keyword"], page=1, results_per_page=results_per_page)
                    if videos:
                        render_results(videos)
                    else:
                        clear_results()
                        tk.Label(scrollable_frame, text="No results found.", font=("Arial", 10)).pack(pady=10)

                threading.Thread(target=threaded_search).start()


    def on_video_click(video_url):
        filetype = format_choice.get().title()
        download_confirm = tk.Toplevel(root)
        download_confirm.title("Download")
        download_confirm.geometry("350x100")
        download_confirm.resizable(False, False)
        download_confirm.iconbitmap('icon.ico')
        center_popup(download_confirm, root)
        download_confirm.grab_set()

        msg = tk.Label(download_confirm, text=f"Download, Convert and clean the metadata of the {filetype} file?", font=("Arial", 10))
        msg.pack(pady=10)

        def on_accept():
            download_confirm.destroy()
            loading_popup = tk.Toplevel(root)
            loading_popup.title("Downloading")
            loading_popup.geometry("350x100")
            loading_popup.resizable(False, False)
            loading_popup.iconbitmap('icon.ico')
            center_popup(loading_popup, root)
            loading_popup.grab_set()

            tk.Label(
                loading_popup,
                text="Downloading, Cleaning, and Converting...",
                font=("Arial", 10),
                wraplength=300,
                justify="center"
            ).pack(expand=True, pady=25)

            root.update()
            def threaded_download():
                result, path = download_video(video_url, convert_to_mp3=(format_choice.get() == 'mp3'))
                loading_popup.destroy()

                if '❌' in result:
                    messagebox.showerror("Download Failed", result)
                    return

                filename = result.split(': ', 1)[-1]
                filetype = filename.split('.')[-1].title()

                if messagebox.askyesno("Download Complete", f"{filetype} file downloaded. Open now?"):
                    os.startfile(os.path.join(path, filename))

                search_button.config(state=tk.NORMAL)
                entry.delete(0, tk.END)
                clear_results()
                current_results["keyword"] = ""
                current_results["page"] = 1


            threading.Thread(target=threaded_download).start()

        def on_decline():
            download_confirm.destroy()

        btn_frame = tk.Frame(download_confirm)
        btn_frame.pack()
        tk.Button(btn_frame, text="Yes", width=10, command=on_accept, cursor="hand2").pack(side="left", padx=20)
        tk.Button(btn_frame, text="No", width=10, command=on_decline, cursor="hand2").pack(side="right", padx=20)

    def go_prev():
        if prev_button['state'] == tk.DISABLED:
            return
        if current_results["page"] > 1:
            prev_button.config(state=tk.DISABLED)
            current_results["page"] -= 1
            threading.Thread(target=lambda: load_page(current_results["page"])).start()


    def go_next():
        if next_button['state'] == tk.DISABLED:
            return
        next_button.config(state=tk.DISABLED)
        current_results["page"] += 1
        threading.Thread(target=lambda: load_page(current_results["page"])).start()

    prev_button.config(command=go_prev)
    next_button.config(command=go_next)

    search_button = tk.Button(search_frame, text="Search / Download", command=handle_submit, cursor="hand2")
    search_button.pack(pady=10)
    root.mainloop()

# Run GUI
show_search_gui()
