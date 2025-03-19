import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageCropper:
    def __init__(self, root, image_folder, max_width=500, max_height=500):
        self.root = root
        self.image_folder = image_folder
        self.max_width = max_width
        self.max_height = max_height
        self.image_files = sorted([f for f in os.listdir(image_folder) 
                                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))])
        self.index = 0
        self.start_x = self.start_y = self.end_x = self.end_y = None
        self.rect_id = None

        # UI Elements
        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.btn_next = tk.Button(root, text="Next", command=self.next_image)
        self.btn_next.pack(side=tk.RIGHT, padx=10, pady=10)

        self.btn_crop = tk.Button(root, text="Crop & Save", command=self.crop_image)
        self.btn_crop.pack(side=tk.RIGHT, padx=10, pady=10)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.load_image()

        # Bind mouse events for cropping
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    def rename_files(self):
        """Renames files by replacing spaces with underscores."""
        for filename in os.listdir(self.image_folder):
            if " " in filename:
                new_filename = filename.replace(" ", "_")
                os.rename(os.path.join(self.image_folder, filename), os.path.join(self.image_folder, new_filename))

    def load_image(self):
        """Loads and displays the current image."""
        if self.index >= len(self.image_files):
            messagebox.showinfo("Done", "All images have been processed.")
            self.root.quit()
            return

        # Load image
        self.image_name = self.image_files[self.index]
        image_path = os.path.join(self.image_folder, self.image_name)

        try:
            self.original_image = Image.open(image_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image: {image_path}\n{e}")
            self.index += 1
            self.load_image()
            return

        # Resize for display
        w, h = self.original_image.size
        scale = min(self.max_width / w, self.max_height / h)
        new_width = int(w * scale)
        new_height = int(h * scale)
        self.display_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.status_label.config(text=f"Image {self.index+1}/{len(self.image_files)}: {self.image_name}")

    def on_mouse_press(self, event):
        """Captures the initial click position for cropping."""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def on_mouse_drag(self, event):
        """Draws a selection rectangle while dragging."""
        if self.rect_id:
            self.canvas.delete(self.rect_id)

        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)

        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red")

    def on_mouse_release(self, event):
        """Finalizes the cropping selection."""
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)

    def crop_image(self):
        """Crops the selected area and saves the image with the same filename."""
        if None in (self.start_x, self.start_y, self.end_x, self.end_y):
            messagebox.showwarning("Warning", "No crop area selected!")
            return

        # Convert coordinates to original image scale
        w_orig, h_orig = self.original_image.size
        w_disp, h_disp = self.display_image.size
        scale_x = w_orig / w_disp
        scale_y = h_orig / h_disp

        x1 = int(self.start_x * scale_x)
        y1 = int(self.start_y * scale_y)
        x2 = int(self.end_x * scale_x)
        y2 = int(self.end_y * scale_y)

        # Ensure proper cropping bounds
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        if x2 - x1 < 5 or y2 - y1 < 5:
            messagebox.showwarning("Warning", "Selection too small!")
            return

        # Crop and save (replace the original image)
        cropped_image = self.original_image.crop((x1, y1, x2, y2))
        new_filename = self.image_name.replace(" ", "_")  # Remove spaces from filename
        cropped_image.save(os.path.join(self.image_folder, new_filename))

        messagebox.showinfo("Success", f"Image {self.image_name} cropped and saved!")

        self.start_x = self.start_y = self.end_x = self.end_y = None
        self.index += 1
        self.load_image()

    def next_image(self):
        """Skips the image without cropping."""
        self.index += 1
        self.load_image()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Image Cropper Tool")
    image_folder = "image_folder"  # Folder containing images
    app = ImageCropper(root, image_folder, max_width=600, max_height=600)
    root.mainloop()
