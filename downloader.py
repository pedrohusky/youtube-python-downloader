import concurrent
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import eyed3
from PIL import Image
from io import BytesIO
import requests
from proglog import ProgressBarLogger
from pytube import YouTube, Playlist
import os
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip


class MyBarLogger(ProgressBarLogger):
    def __init__(self, downloader):
        super().__init__()
        self.downloader = downloader

    def bars_callback(self, bar, attr, value, old_value=None):
        # Every time the logger progress is updated, this function is called
        percentage = (value / self.bars[bar]['total']) * 100
        self.downloader.main_app.finish_label.configure(text=f"Processing video.. {percentage:.2f}%",
                                                        text_color="purple")


def set_mp3_metadata_eyed3(filename, album, artist, year, genre, image_data):
    """
    Sets the metadata of an MP3 file using the `eyed3` library.

    Args:
        filename (str): The path of the MP3 file.
        album (str): The album name.
        artist (str): The artist name.
        year (str): The year of release.
        genre (str): The genre of the song.
        image_data (bytes): The binary data of the album cover image.

    Returns:
        None

    Raises:
        None

    Prints:
        - "Error loading MP3 file" if the file cannot be loaded.
        - "Metadata updated successfully." after saving the changes to the MP3 file.
    """

    audio = eyed3.load(filename)
    if audio is None:
        print("Error loading MP3 file")
        return

    # Set the metadata tags
    audio.tag.album = album
    audio.tag.artist = artist
    audio.tag.year = year
    audio.tag.genre = genre

    # Set the album cover image
    if image_data:
        audio.tag.images.set(3, image_data, "image/jpeg")

    # Save the changes to the MP3 file
    audio.tag.save()
    print("Metadata updated successfully.")


class YouTubeDownloader:
    def __init__(self, main_app):
        self.playlist_urls = None
        self.audio_path = None
        self.main_app = main_app
        self.logger = MyBarLogger(self)

    def download(self):
        """
        Start the download in a separate thread.
        """

        # This method starts the download in a separate thread
        threading.Thread(target=self.download_in_background).start()

    def download_playlist(self):
        """
        Starts the download of the playlist in a separate thread.
        """

        # This method starts the download in a separate thread
        threading.Thread(target=self.download_playlist_in_background).start()

    def download_image(self, thumbnail_url, title):
        """
        Downloads an image from the given thumbnail URL.

        Parameters:
            thumbnail_url (str): The URL of the thumbnail image to download.
            title (str): The title of the image.

        Returns:
            bytes: The downloaded image data as bytes, or None if the download failed.
        """
        response = requests.get(thumbnail_url)

        if response.status_code == 200:
            img_data = Image.open(BytesIO(response.content))
            # Convert the image data to bytes
            with BytesIO() as img_bytes_io:
                img_data.save(img_bytes_io,
                              format='JPEG')  # You can specify the desired format ('JPEG', 'PNG', etc.)
                img_data = img_bytes_io.getvalue()

            self.main_app.finish_label.configure(text=f"Finished album download for: {title}",
                                                 text_color="purple")
            return img_data
        return None

    def download_audio_and_convert_to_mp3(self, video_url, save_path):
        """
        Downloads a video from the given YouTube `video_url` and converts it to mp3 format.
        Then, updates the metadata of the mp3 with some info from the video.

        Args:
            video_url (str): The URL of the YouTube video to download.
            save_path (str): The directory in which to save the downloaded file.

        Returns:
            None
        """
        yt = YouTube(video_url)
        self.main_app.finish_label.configure(text=f"Initializing download for: {yt.title}",
                                             text_color="purple")
        yt.register_on_progress_callback(self.main_app.progress_callback)

        img_data = self.download_image(yt.thumbnail_url, yt.title)

        if self.main_app.playlist_only_audio.get():
            # Download the highest quality audio
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            audio_stream.download(output_path=save_path)
        else:
            # Download the highest quality audio and video streams
            audio_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by(
                'resolution').desc().first()
            audio_stream.download(output_path=save_path)

        self.main_app.finish_label.configure(text=f"Downloaded video/mp3 for: {yt.title}",
                                             text_color="purple")

        mp3_path = self.convert_mp3(self.main_app.convert_to_mp3.get(), save_path, audio_stream.default_filename, yt)

        if mp3_path is not None:
            self.try_update_metadata(yt, mp3_path, img_data)

    def convert_mp3(self, convert, save_path, filename, yt, logger=None):
        """
        Convert a downloaded audio file to MP3 format.

        Args:
            convert (bool): Whether to perform the conversion or not.
            save_path (str): The path to the directory where the downloaded audio file is saved.
            filename (str): The name of the downloaded audio file.
            yt (YouTube): The YouTube object representing the downloaded video.
            logger (Logger, optional): An optional logger object for logging conversion progress.

        Returns:
            str: The path to the converted MP3 file.

        Raises:
            None
        """

        if convert:
            # Get the downloaded audio file path
            audio_path = os.path.join(save_path, filename)

            # Define the output MP3 file path
            mp3_path = os.path.splitext(audio_path)[0] + ".mp3"

            self.main_app.finish_label.configure(text=f"Starting conversion for: {yt.title}",
                                                 text_color="purple")

            # Convert the audio to MP3 using moviepy
            audio_clip = AudioFileClip(audio_path)
            audio_clip.write_audiofile(mp3_path, codec='mp3', logger=logger)

            # Close the audio clip to release resources
            audio_clip.close()

            # Remove the original WebM audio file if it exists
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except FileExistsError:
                    print("Got a problem while excluding a file. It is being used by another process, but this is "
                          "just a warning, as the file was removed.")
            else:
                print(f"Original audio file does not exist at {audio_path}")
            return mp3_path

    def try_update_metadata(self, yt, mp3_path, image_data):
        """
        Updates the metadata of an MP3 file with information from a YouTube video.

        Parameters:
            yt (YouTube object): The YouTube video object.
            mp3_path (str): The path to the MP3 file.
            image_data (bytes): The binary data of the album cover image.

        Returns:
            None
        """

        # Embed album cover into the MP3 file
        if os.path.exists(mp3_path) and image_data:
            self.main_app.finish_label.configure(text=f"Processing metadata for: {yt.title}",
                                                 text_color="purple")

            set_mp3_metadata_eyed3(mp3_path, yt.title, yt.author, yt.publish_date, "", image_data)

            self.main_app.finish_label.configure(text=f"All done: {yt.title}",
                                                 text_color="purple")

    def download_playlist_in_background(self):
        """
        Downloads all the videos in the playlist concurrently in the background.
        Max_workers is set to 75% of CPU cores available.

        Args:
            self (YouTubeDownloader): The instance of the class.

        Returns:
            None
        """

        # Loop through the videos in the playlist and download each one concurrently
        save_path = self.main_app.save_path_var.get()
        with ThreadPoolExecutor(max_workers=int(os.cpu_count() * 0.75)) as executor:  # Adjust max_workers as needed
            futures = []
            start_time = time.time()
            for video in self.playlist_urls:
                futures.append(executor.submit(self.download_audio_and_convert_to_mp3, video, save_path))

            i = 0
            for future in concurrent.futures.as_completed(futures):
                future.result()
                i += 1
                end_time = time.time()
                elapsed_time = end_time - start_time
                self.main_app.finish_label.configure(
                    text=f"Downloaded video {i}/{len(self.playlist_urls)} - Elapsed time: {elapsed_time:.2f}s",
                    text_color="purple")
            # Wait for all threads to complete
            concurrent.futures.wait(futures)

        self.main_app.finish_label.configure(
            text=f"All videos downloaded {i}/{len(self.playlist_urls)} - Elapsed time: {elapsed_time:.2f}s",
            text_color="green")

    def download_audio(self, title, save_path):
        """
        Downloads the audio track for a given title and saves it to the specified path.

        Args:
            title (str): The title of the audio track.
            save_path (str): The path where the audio track will be saved.

        Returns:
            str: The path to the downloaded audio file.
        """
        audio_stream = self.main_app.streams.filter(only_audio=True).order_by('abr').desc().first()
        audio_extension = audio_stream.mime_type.split("/")[-1]
        audio_filename = f"{title}-audio.{audio_extension}"
        self.main_app.finish_label.configure(text="Downloading audio track..", text_color="blue")
        audio_stream.download(output_path=save_path, filename=audio_filename)
        self.main_app.finish_label.configure(text="Downloaded audio track.", text_color="green")
        return os.path.join(save_path, audio_filename)

    def download_video(self, title, save_path, video_stream):
        """
        Downloads a video track.

        Args:
            title (str): The title of the video.
            save_path (str): The path where the video will be saved.
            video_stream: The video stream to download.

        Returns:
            str: The path of the downloaded video.
        """

        self.main_app.finish_label.configure(text="Downloading video track.", text_color="yellow")

        video_extension = video_stream.mime_type.split("/")[-1]
        video_filename = f"{title}.{video_extension}"
        video_stream.download(output_path=save_path, filename=video_filename)
        video_path = os.path.join(save_path, video_filename)

        self.main_app.finish_label.configure(text="Downloaded successfully", text_color="green")
        return video_path

    def merge_audio_and_video(self, title, save_path, video_path, audio_path, thumbnail, yt):
        """
        Merges audio and video files to create a final video with audio track.

        Args:
            title (str): The title of the final video.
            save_path (str): The directory where the final video will be saved.
            video_path (str): The path to the video file.
            audio_path (str): The path to the audio file.
            thumbnail (str): The path to the thumbnail image.
            yt (YouTube): A instance of the downloaded video.

        Returns:
            None
        """

        if self.main_app.selected_format.get().lower() == "mp3":
            image_data = self.download_image(thumbnail, audio_path.split('\\')[-1])
            mp3_path = self.convert_mp3(True, save_path, audio_path.split('\\')[-1], yt, self.logger)
            self.try_update_metadata(yt, mp3_path, image_data)
            if audio_path != video_path and video_path != "":
                os.remove(video_path)
        elif (self.main_app.selected_format.get().lower() in ["mp4", "avi", "mkv"]
              and audio_path != video_path and video_path != ""):
            self.main_app.finish_label.configure(text="Creating objects..", text_color="purple")
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)

            self.main_app.finish_label.configure(text="Merging audio track..", text_color="purple")
            final_clip = video_clip.set_audio(audio_clip)

            self.main_app.finish_label.configure(text="Processing video..", text_color="purple")
            output_video_path = os.path.join(save_path,
                                             f"{title}-converted.{self.main_app.selected_format.get().lower()}")

            try:
                final_clip.write_videofile(output_video_path, codec='libx264', logger=self.logger)
                os.remove(video_path)
                os.remove(audio_path)

                self.main_app.finish_label.configure(text="Download complete. Converted audio and video tracks.",
                                                     text_color="green")
            except IOError as e:
                error_message = f"Error during video and audio merging: {str(e)}"
                self.main_app.finish_label.configure(text=error_message, text_color="red")
        elif self.main_app.selected_format.get().lower() != "no conversion":
            self.main_app.finish_label.configure(text="To convert to any format besides MP3 you need to enable both "
                                                      "outputs.", text_color="red")
            if audio_path != video_path and video_path != "":
                os.remove(video_path)
            if audio_path != "":
                os.remove(audio_path)

    def download_in_background(self):
        """
        Downloads a video or audio file in the background.

        Parameters:
            self (YouTubeDownloader): The instance of the class.

        Returns:
            None
        """

        is_audio_only = self.main_app.audio_var.get()
        is_video_only = self.main_app.video_var.get()
        save_path = self.main_app.save_path_var.get()
        selected_quality = self.main_app.quality_var.get()
        video_path = ''
        self.audio_path = ''

        title = (f"{self.main_app.yt.title.replace(' ', '_').replace(':', '-').replace('|', '-')}"
                 f"-{selected_quality.split(' - ')[0]}")
        thumbnail = self.main_app.yt.thumbnail_url

        if is_audio_only:
            video_stream = self.main_app.streams.filter(res=selected_quality.split(" - ")[0]).first()

            if not video_stream.is_progressive:
                self.audio_path = self.download_audio(title, save_path)
            elif not is_video_only:
                self.audio_path = self.download_audio(title, save_path)
            elif is_video_only and not video_stream.is_progressive:
                self.audio_path = self.download_audio(title, save_path)
        else:
            video_stream = self.main_app.streams.filter(res=selected_quality.split(" - ")[0],
                                                        file_extension="webm").first()

        if is_video_only:
            video_path = self.download_video(title, save_path, video_stream)

        if self.audio_path == "":
            self.audio_path = video_path
        self.merge_audio_and_video(title, save_path, video_path, self.audio_path, thumbnail, self.main_app.yt)

    def fetch_qualities(self):
        """
        Fetches the qualities of a video based on the provided URL.

        Returns:
            - A list of qualities of the video.
              Each quality is represented as a string in the format:
              "{resolution} - {download_speed} - {fps}".
              - {resolution}: The resolution of the video stream.
              - {download_speed}: The download speed of the video stream, either "Fast download" or "Slow download".
              - {fps}: The frames per second of the video stream (optional).

              If the URL is invalid or the video is unavailable, returns None.

        Raises:
            Exception
        """

        # Get the URL from the entry field
        url = self.main_app.url_var.get()

        qualities = {}

        # Fetch the video details
        try:
            self.main_app.yt = YouTube(url)
            self.main_app.yt.register_on_progress_callback(self.main_app.progress_callback)
            self.main_app.streams = self.main_app.yt.streams
            for stream in self.main_app.streams:
                if stream.resolution is not None:
                    resolution = stream.resolution
                    fast = "Fast download" if stream.is_progressive else "Slow download"
                    fps = f" - {stream.fps} fps" if stream.fps is not None else ""
                    stream_value = resolution + f" - {fast}" + fps
                    if resolution not in qualities or "Fast download" not in qualities[resolution]:
                        qualities[resolution] = stream_value

            # Convert the dictionary values to a list
            qualities_list = list(qualities.values())

            return qualities_list
        except Exception as e:
            # Handle exceptions, e.g., invalid URL or unavailable video
            print(f"Error fetching qualities: {e}")
            return None

    def fetch_playlist(self):
        """
        Fetches a playlist from a given URL.

        :return: A tuple containing the video URLs and the title of the playlist.
                 Returns None if there is an error fetching the playlist.
        """

        # Get the URL from the entry field
        url = self.main_app.url_var.get()

        # Fetch the video details
        try:
            # Create a Playlist object
            playlist = Playlist(url)
            self.playlist_urls = playlist.video_urls
            return playlist.video_urls, playlist.title
        except Exception as e:
            # Handle exceptions, e.g., invalid URL or unavailable video
            print(f"Error fetching playlists: {e}")
            return None
