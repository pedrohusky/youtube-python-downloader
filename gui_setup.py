import concurrent
import os
import re
import sys
import tkinter as tk
import threading
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from tkinter import filedialog
from PIL import Image
import customtkinter
import requests
from pytube import YouTube

from downloader import YouTubeDownloader

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("720x480")
        self.root.title("Youber")

        # Running from source
        icon_path = getattr(sys, '_MEIPASS', '.')  # Fallback to current directory
        icon_path = os.path.join(icon_path, 'icon.ico')

        self.root.iconbitmap(icon_path)

        self.downloader = YouTubeDownloader(self)

        # Variables
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar()
        self.audio_var = tk.BooleanVar(value=True)
        self.video_var = tk.BooleanVar(value=True)
        self.max_min_quality = tk.BooleanVar(value=True)
        self.playlist_only_audio = tk.BooleanVar(value=True)
        self.convert_to_mp3 = tk.BooleanVar(value=False)
        self.format_label = None
        self.format_menu = None
        self.selected_format = None
        self.find_button = None
        self.download_button = None
        self.save_path_var = None
        self.audio_check = None
        self.video_check = None
        self.quality_menu = None
        self.url_entry = None
        self.video_info_frame = None
        self.checkbox_frame = None
        self.video_name_label = None
        self.finish_label = None
        self.yt = None
        self.quality_label = None
        self.save_path_button = None
        self.save_label = None
        self.playlist_title_label = None
        self.playlist_download_button = None
        self.video_names_text = None
        self.progressbar = None

        self.create_widgets_1()

    def create_widgets_1(self):
        """
        Create and initialize widgets for the user interface.

        Returns:
            None
        """

        # Label for the YouTube link
        link_label = customtkinter.CTkLabel(self.root, text="1. Insert a YouTube link below:")
        link_label.pack(padx=10, pady=10)

        # Entry field for the YouTube link
        self.url_entry = customtkinter.CTkEntry(self.root, height=40, width=500, textvariable=self.url_var)
        self.url_entry.pack(padx=10, pady=10)
        # Bind an event handler to the entry field for changes
        self.url_entry.bind("<Return>", self.on_entry_change)

        def on_button_click():
            self.on_entry_change(None)

        # Entry field for the YouTube link
        self.find_button = customtkinter.CTkButton(self.root, height=40,
                                                   text="Find", width=500, command=on_button_click)
        self.find_button.pack(padx=10, pady=10)

        self.progressbar = customtkinter.CTkProgressBar(master=self.root, mode="indeterminate", height=0)
        self.progressbar.pack(padx=10, pady=10)

        self.update_layout()

    def create_playlist_layout(self, videos, title):
        """
        Generate the layout for the playlist.

        Args:
            videos (list): A list of videos in the playlist.
            title (str): The title of the playlist.

        Returns:
            None
        """

        self.hide_widgets()

        # Create a frame for video names and download quality switch
        self.playlist_title_label = customtkinter.CTkLabel(self.root, text=title, text_color="orange")
        self.playlist_title_label.pack(padx=10, pady=10)

        # Create a frame for video names and download quality switch
        self.video_info_frame = customtkinter.CTkFrame(self.root)
        self.video_info_frame.pack(padx=10, pady=10)

        # Create a Text widget to display playlist video names
        self.video_names_text = customtkinter.CTkTextbox(self.video_info_frame)
        self.video_names_text.grid(row=0, column=0, padx=10, pady=10)

        # Create a switch (checkbutton) for download quality
        download_quality_switch = customtkinter.CTkCheckBox(self.video_info_frame,
                                                            text="Maximum Quality",
                                                            variable=self.max_min_quality)
        download_quality_switch.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Create a switch (checkbutton) for download quality
        download_audio_switch = customtkinter.CTkCheckBox(self.video_info_frame,
                                                          text="Only Audio",
                                                          variable=self.playlist_only_audio)
        download_audio_switch.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Create a switch (checkbutton) for download quality
        download_mp3_switch = customtkinter.CTkCheckBox(self.video_info_frame,
                                                        text="Convert to MP3",
                                                        variable=self.convert_to_mp3)
        download_mp3_switch.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        # Label for save path
        self.save_label = customtkinter.CTkLabel(self.root, text="2. Save to:")
        self.save_label.pack(padx=10, pady=10)

        # Button to select save path
        self.save_path_var = tk.StringVar(value="Select destination folder")
        self.save_path_button = customtkinter.CTkButton(self.root, textvariable=self.save_path_var,
                                                        command=self.open_folder_selector)
        self.save_path_button.pack(padx=10, pady=10)

        # Button to start download
        self.playlist_download_button = customtkinter.CTkButton(self.root, text="Download",
                                                                command=self.downloader.download_playlst)
        self.playlist_download_button.pack(padx=10, pady=10)
        self.playlist_download_button.configure(state=tk.DISABLED)  # Initially disabled

        # Finish label
        self.finish_label = customtkinter.CTkLabel(self.root, text='')
        self.finish_label.pack()

        self.update_layout()

        self.load_video_names(videos)

    def create_video_layout(self, qualities):
        """
        Creates a video layout with the given qualities.

        Parameters:
            - qualities (list): A list of qualities for the video.

        Returns:
            None
        """

        self.hide_widgets()
        # Create a frame for video title and image
        self.video_info_frame = customtkinter.CTkFrame(self.root)
        self.video_info_frame.pack(padx=10, pady=10)

        # Load and display the video thumbnail
        thumbnail_url = self.yt.thumbnail_url
        # Fetch the image data using requests
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            # Convert the image data to a Pillow Image object
            img_data = Image.open(BytesIO(response.content))

            # Convert the Pillow Image to a PhotoImage
            thumbnail = customtkinter.CTkImage(light_image=img_data, size=(100, 100))

            # Create a Label widget to display the thumbnail
            thumbnail_label = customtkinter.CTkLabel(self.video_info_frame, image=thumbnail, text='')
            thumbnail_label.grid(row=0, column=1, padx=10, pady=10)

        video_title = self.yt.title
        line_length = len(f"Published at: {self.yt.publish_date}") * 2  # Adjust the offset as needed
        video_info = (f"{video_title}\n\n"
                      f"{'-' * line_length}\n"
                      f"Author: {self.yt.author}\n"
                      f"Published at: {self.yt.publish_date}\n"
                      f"Views: {self.yt.views}\n"
                      f"{'-' * line_length}")

        # Label for video title
        self.video_name_label = customtkinter.CTkLabel(self.video_info_frame, text=video_info, text_color="orange")
        self.video_name_label.grid(row=0, column=2, padx=10, pady=10)

        # Label for quality selection
        self.quality_label = customtkinter.CTkLabel(self.root, text="2. Select a quality:")
        self.quality_label.pack(padx=10, pady=10)

        # Option menu for quality selection
        self.quality_menu = customtkinter.CTkOptionMenu(self.root, values=qualities, variable=self.quality_var)
        self.quality_menu.pack(padx=10, pady=10)

        # Create a list of format options
        format_options = ["No conversion", "MP3", "AVI", "MKV", "MP4"]  # You can add more formats as needed

        # Create a StringVar to store the selected format
        self.selected_format = tk.StringVar()

        # Set the default format
        self.selected_format.set(format_options[0])  # Set it to the first format in the list

        # Label for quality selection
        self.format_label = customtkinter.CTkLabel(self.root, text="3. Select a output format:")
        self.format_label.pack(padx=10, pady=10)

        # Create the OptionMenu widget
        self.format_menu = customtkinter.CTkOptionMenu(self.root, values=format_options, variable=self.selected_format)
        self.format_menu.pack(padx=10, pady=10)

        # Create a frame for checkboxes managed by grid
        self.checkbox_frame = customtkinter.CTkFrame(self.root)
        self.checkbox_frame.pack(padx=10, pady=10)

        # Checkbox for audio only (in checkbox_frame)
        audio_check = customtkinter.CTkCheckBox(self.checkbox_frame, text="Audio Output",
                                                variable=self.audio_var)
        audio_check.grid(row=0, column=0, padx=10, pady=10)

        # Checkbox for video only (in checkbox_frame)
        video_check = customtkinter.CTkCheckBox(self.checkbox_frame, text="Video Output",
                                                variable=self.video_var)
        video_check.grid(row=0, column=1, padx=10, pady=10)

        # Label for save path
        self.save_label = customtkinter.CTkLabel(self.root, text="4. Save to:")
        self.save_label.pack(padx=10, pady=10)

        # Button to select save path
        self.save_path_var = tk.StringVar(value="Select destination folder")
        self.save_path_button = customtkinter.CTkButton(self.root, textvariable=self.save_path_var,
                                                        command=self.open_folder_selector)
        self.save_path_button.pack(padx=10, pady=10)

        # Button to start download
        self.download_button = customtkinter.CTkButton(self.root, text="Download",
                                                       command=self.downloader.download)
        self.download_button.pack(padx=10, pady=10)
        self.download_button.configure(state=tk.DISABLED)  # Initially disabled

        # Finish label
        self.finish_label = customtkinter.CTkLabel(self.root, text='')
        self.finish_label.pack()

        self.update_layout()

    def update_layout(self):
        """
        Update the window size based on its content.

        This function updates the size of the window based on the size of its content.
        It ensures that all widgets are displayed before calculating the required width and height.
        The resulting width and height are then used to set the geometry of the window.

        Parameters:
            self (YouTubeDownloaderApp): The current instance of the class.

        Returns:
            None
        """

        # Update the window size based on its content
        self.root.update_idletasks()  # Ensure all widgets are displayed
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        self.root.geometry(f"{width}x{height}")

    def handle_error(self):
        """
        Hides the widgets, creates a button click event handler, creates an entry field for the YouTube link,
        creates a finish label, and updates the layout.

        Returns:
            None
        """
        self.hide_widgets()

        def on_button_click():
            self.on_entry_change(None)

        # Entry field for the YouTube link
        self.find_button = customtkinter.CTkButton(self.root, height=40,
                                                   text="Find", width=500, command=on_button_click)
        self.find_button.pack(padx=10, pady=10)

        # Finish label
        self.finish_label = customtkinter.CTkLabel(self.root,
                                                   text="Something went wrong. "
                                                        "Maybe video is only available when logged-in.",
                                                   text_color="red")
        self.finish_label.pack()

        self.update_layout()

    def start_spinner(self):
        """
        Start the spinner animation.

        This function starts the spinner animation by creating a progress bar widget and configuring it,
        with the specified height. The progress bar is then started to initiate the animation.

        Parameters:
            self (YouTubeDownloaderApp): The reference to the current instance of the class.

        Returns:
            None
        """
        # self.hide_widgets()
        self.progressbar.pack(padx=10, pady=10)
        self.progressbar.configure(height=10)
        self.progressbar.start()

    def create_widgets_2(self):
        """
        Creates and initializes the widgets for the application.
        It changes its layout based on the link entered by the user.
        Possible layouts are: Playlist and Video

        Returns:
            None
        """

        self.root.after(0, self.start_spinner)

        if "playlist" in self.url_var.get():
            playlist_videos, title = self.downloader.fetch_playlist()

            if playlist_videos is not None:
                # Update UI in the main thread
                self.root.after(0, lambda: self.create_playlist_layout(playlist_videos, title))

            else:
                self.root.after(0, self.handle_error)

        else:
            qualities = self.downloader.fetch_qualities()

            if qualities is not None:
                self.root.after(0, lambda: self.create_video_layout(qualities))

            else:
                self.root.after(0, self.handle_error)

    def progress_callback(self, stream, _, bytes_remaining):
        """
        A callback function that updates the progress of a download.

        Args:
            stream: The stream object representing the download.
            _: An optional argument that is not used in this function.
            bytes_remaining: The number of bytes remaining to be downloaded.

        Returns:
            None
        """
        percent_done = int((1 - bytes_remaining / stream.filesize) * 100)
        self.finish_label.configure(text=f"Downloaded: {percent_done}%", text_color="yellow")

    def hide_widgets(self):
        """
        Hides the widgets.

        This function hides a list of widgets by using the `pack_forget()` method.
        The list of widgets to hide is defined in the `widgets` list.
        Each widget is checked to see if it exists before it is hidden.


        Returns:
            None
        """
        # Hide the widgets
        widgets = [
            self.format_menu,
            self.format_label,
            self.quality_label,
            self.quality_menu,
            self.audio_check,
            self.save_label,
            self.save_path_button,
            self.download_button,
            self.finish_label,
            self.video_name_label,
            self.checkbox_frame,
            self.video_info_frame,
            self.playlist_download_button,
            self.playlist_title_label,
            self.find_button,
            self.progressbar
        ]

        for widget in widgets:
            if widget:
                widget.pack_forget()

        self.update_layout()

    def on_entry_change(self, _):
        """
        This function is called when the content of the entry field changes.
        It spawns a thread to change the layout based on the link entered by the user.

        Parameters:
            event: The event object representing the event that triggered the function.

        Returns:
            None
            :param _: Not used in this function
        """

        # This function is called when the content of the entry field changes
        new_url = self.url_var.get()
        # You can access the new URL value here and react accordingly
        print(f"URL changed to: {new_url}")

        threading.Thread(target=self.create_widgets_2).start()

    def update_download_button_state(self):
        """
        Updates the state of the download button based on the availability of required input.

        Returns:
            None
        """

        # Check if all required input is provided
        url = self.url_var.get()
        quality = self.quality_var.get()
        save_path = self.save_path_var.get()

        try:
            if url and save_path and quality:
                self.download_button.configure(state=tk.NORMAL)  # Enable the button
            else:
                self.download_button.configure(state=tk.DISABLED)  # Disable the button
        except AttributeError:
            pass

    def update_playlist_download_button_state(self):
        """
        Updates the state of the playlist download button based on the availability of required input.

        Parameters:
            self (YouTubeDownloaderApp): The current instance of the class.

        Returns:
            None
        """

        # Check if all required input is provided
        url = self.url_var.get()
        save_path = self.save_path_var.get()

        try:
            if url and save_path:
                self.playlist_download_button.configure(state=tk.NORMAL)  # Enable the button
            else:
                self.playlist_download_button.configure(state=tk.DISABLED)  # Disable the button
        except ValueError:
            pass

    def open_folder_selector(self):
        """
        Opens a dialog box to allow the user to select a folder. If a folder is selected,
        the path is stored in `self.save_path_var` along with the playlist title, if available.
        Additionally, it updates the state of the download button and the playlist download button.
        """

        folder_path = filedialog.askdirectory()
        if folder_path:
            try:
                playlist_title = self.playlist_title_label.cget("text")
                self.save_path_var.set(f"{folder_path}/{playlist_title}")
            except LookupError:
                self.save_path_var.set(f"{folder_path}")

        self.update_download_button_state()  # Update button state when folder selected
        self.update_playlist_download_button_state()

    def load_video_names(self, videos):
        """
        Loads the video names into the video_names_text widget.
        It uses concurrency to load the video names in parallel to speed up the process.
        Max_workers is set to 75% of CPU cores available.

        Parameters:
            videos (list): A list of video URLs.

        Returns:
            None
        """

        def load_title(video_url, index):
            """
            Loads the title of a video from a given URL and inserts it into the video_names_text widget.

            Parameters:
                video_url (str): The URL of the video.
                index (int): The index of the video.

            Returns:
                str: The title of the video with the index appended.
            """
            yt = YouTube(video_url)
            title = f"{index} - {yt.title}\n"
            self.video_names_text.insert(tk.END, title)
            return title

        def background_task():
            """
            Executes a background task using a thread pool executor to load video titles and sort them in a text box.

            This function uses a thread pool executor to load video titles asynchronously.
            It creates a number of threads based on the CPU count,
            and then submits tasks to load titles for each video in the 'videos' list.
            The 'load_title' function is called for each video, passing the video and an index as parameters.
            The titles are loaded concurrently in separate threads.

            After all threads have completed, the function retrieves the text from the 'video_names_text' textbox.
            It splits the text into lines and removes any blank lines.
            Then, it extracts numbers from each non-blank line using a regular expression.
            The lines are sorted based on the parsed numbers,
            and the sorted lines are joined back together to form the sorted text.

            Finally, the function updates the 'video_names_text' textbox with the sorted text,
            by deleting the existing content and inserting the sorted text at the end.
            """
            with ThreadPoolExecutor(max_workers=int(os.cpu_count() * 0.75)) as executor:
                futures = []
                i = 0
                for video in videos:
                    futures.append(executor.submit(load_title, video, i))
                    i += 1

                # Wait for all threads to complete
                concurrent.futures.wait(futures)

                # Extract the text from self.video_names_text
                text = self.video_names_text.get("1.0", tk.END)

                # Split the text into lines and remove blank lines
                lines = [line for line in text.splitlines() if line.strip()]

                # Parse and extract numbers from each non-blank line
                def extract_number(line):
                    match = re.search(r'(\d+)', line)
                    if match:
                        return int(match.group(1))
                    return 0

                # Sort the lines based on the parsed numbers
                sorted_lines = sorted(lines, key=extract_number)

                # Reconstruct the sorted text
                sorted_text = '\n'.join(sorted_lines)

                # Update the CTkTextbox with the sorted text
                self.video_names_text.delete("1.0", tk.END)
                self.video_names_text.insert(tk.END, sorted_text)

        # Create a thread to run the background task
        background_thread = threading.Thread(target=background_task)
        background_thread.start()


if __name__ == "__main__":
    root = customtkinter.CTk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
