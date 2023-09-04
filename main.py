import customtkinter
import gui_setup

if __name__ == "__main__":
    root = customtkinter.CTk()
    app = gui_setup.YouTubeDownloaderApp(root)
    root.mainloop()
