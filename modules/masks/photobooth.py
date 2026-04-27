import cv2
import tkinter as tk
from PIL import Image, ImageTk
import mediapipe as mp
import numpy as np
import time
import os


class PhotoBoothApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Фотобудка")

        self.window.configure(bg='#ffe6f0')
        self._apply_shared_geometry()

        self.window.update_idletasks()


        self.cap = cv2.VideoCapture(0)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)

        self.glasses_img = cv2.imread('glasses.png', cv2.IMREAD_UNCHANGED)
        self.crown_img = cv2.imread('crown.png', cv2.IMREAD_UNCHANGED)
        self.mustache_img = cv2.imread('mustache.png', cv2.IMREAD_UNCHANGED)
        self.heart_img = cv2.imread('heart.png', cv2.IMREAD_UNCHANGED)

        self.current_filter = "none"
        self.last_frame = None

        self.video_frame = tk.Frame(window, bg='white', bd=10, relief=tk.RAISED)
        self.video_frame.pack(pady=15, padx=20)

        self.canvas = tk.Canvas(self.video_frame, width=640, height=480, bg='#f0f0f0', highlightthickness=0)
        self.canvas.pack()

        btn_container = tk.Frame(window, bg='#ffe6f0')
        btn_container.pack(fill=tk.X, padx=20, pady=10)

        canvas_btns = tk.Canvas(btn_container, height=80, bg='#ffe6f0', highlightthickness=0)
        scrollbar = tk.Scrollbar(btn_container, orient="horizontal", command=canvas_btns.xview)
        scrollable_frame = tk.Frame(canvas_btns, bg='#ffe6f0')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_btns.configure(scrollregion=canvas_btns.bbox("all"))
        )

        canvas_btns.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_btns.configure(xscrollcommand=scrollbar.set)

        filters = [
            ("Обычный", "none"), ("Ч/Б", "gray"), ("Сепия", "sepia"),
            ("Очки", "glasses"), ("Корона", "crown"), ("Усы", "mustache"),
            ("Глаза ++", "big_eyes"), ("Большой рот", "big_mouth"), ("Сердечки", "heart_eyes")
        ]

        colors = ['#ffb7c5', '#ffc4d4', '#ffd0e0', '#ffdce8', '#ffe8f0', '#fff0f5', '#fff5f8', '#fffafc', '#ffffff']

        for i, (text, mode) in enumerate(filters):
            btn = tk.Button(scrollable_frame, text=text, command=lambda m=mode: self.set_filter(m),
                            font=('Comic Sans MS', 10, 'bold'), bg=colors[i % len(colors)],
                            fg='#cc6699', relief=tk.RAISED, bd=3, cursor='hand2',
                            padx=15, pady=5)
            btn.pack(side=tk.LEFT, padx=5, pady=5)

            def on_enter(e, button=btn):
                button.config(bg='#ff99bb', fg='white')

            def on_leave(e, button=btn):
                button.config(bg=colors[i % len(colors)], fg='#cc6699')

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        canvas_btns.pack(side=tk.TOP, fill=tk.X, expand=True)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.photo_btn = tk.Button(window, text="СДЕЛАТЬ ФОТО", bg='#ff6699', fg='white',
                                   font=('Comic Sans MS', 14, 'bold'), command=self.take_snapshot,
                                   relief=tk.RAISED, bd=5, cursor='hand2', height=2, width=20)
        self.photo_btn.pack(pady=15)

        def on_enter_photo(e):
            self.photo_btn.config(bg='#ff3366', font=('Comic Sans MS', 15, 'bold'))

        def on_leave_photo(e):
            self.photo_btn.config(bg='#ff6699', font=('Comic Sans MS', 14, 'bold'))

        self.photo_btn.bind("<Enter>", on_enter_photo)
        self.photo_btn.bind("<Leave>", on_leave_photo)

        self.label = tk.Label(window, text="Улыбнись!",
                              font=('Comic Sans MS', 12, 'italic'), bg='#ffe6f0', fg='#cc6699')
        self.label.pack(pady=5)

        self.update()

    def _apply_shared_geometry(self):
        x = os.getenv("APP_WINDOW_X")
        y = os.getenv("APP_WINDOW_Y")
        w = os.getenv("APP_WINDOW_W")
        h = os.getenv("APP_WINDOW_H")

        if x and y and w and h:
            self.window.geometry(f"{w}x{h}+{x}+{y}")
        else:
            self.window.geometry("720x720")

    def set_filter(self, mode):
        self.current_filter = mode
        self.label.config(text=f"Фильтр: {mode}")
        self.window.after(1500, lambda: self.label.config(text="Улыбнись! Ты прекрасна!"))

    def apply_sepia(self, frame):
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        return cv2.transform(frame, kernel)

    def overlay_transparent(self, background, overlay, x, y, size=None):
        if size: overlay = cv2.resize(overlay, size)
        h, w, _ = overlay.shape
        y1, y2 = max(0, y), min(background.shape[0], y + h)
        x1, x2 = max(0, x), min(background.shape[1], x + w)
        overlay_x1, overlay_y1 = max(0, -x), max(0, -y)
        overlay_x2, overlay_y2 = overlay_x1 + (x2 - x1), overlay_y1 + (y2 - y1)
        if x1 >= x2 or y1 >= y2: return background
        overlay_image = overlay[overlay_y1:overlay_y2, overlay_x1:overlay_x2, :3]
        mask = overlay[overlay_y1:overlay_y2, overlay_x1:overlay_x2, 3] / 255.0
        for c in range(3):
            background[y1:y2, x1:x2, c] = (mask * overlay_image[:, :, c] + (1.0 - mask) * background[y1:y2, x1:x2, c])
        return background

    def zoom_eye(self, frame, center_x, center_y, radius=40, scale=1.5):
        x1, x2 = center_x - radius, center_x + radius
        y1, y2 = center_y - radius, center_y + radius
        if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]: return frame
        roi = frame[y1:y2, x1:x2].copy()
        h, w = roi.shape[:2]
        flex_x, flex_y = np.zeros((h, w), np.float32), np.zeros((h, w), np.float32)
        for i in range(h):
            for j in range(w):
                dx, dy = j - w / 2, i - h / 2
                distance = np.sqrt(dx ** 2 + dy ** 2)
                if distance < radius:
                    factor = np.power(distance / radius, 1 / scale)
                    flex_x[i, j] = max(0, min(w - 1, w / 2 + dx * factor))
                    flex_y[i, j] = max(0, min(h - 1, h / 2 + dy * factor))
                else:
                    flex_x[i, j], flex_y[i, j] = j, i
        dst = cv2.remap(roi, flex_x, flex_y, cv2.INTER_LINEAR)
        frame[y1:y2, x1:x2] = dst
        return frame

    def zoom_mouth(self, frame, center_x, center_y, width=100, height=60, scale=1.5):
        x1, x2 = center_x - width, center_x + width
        y1, y2 = center_y - height, center_y + height

        if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
            return frame

        roi = frame[y1:y2, x1:x2].copy()
        h, w = roi.shape[:2]
        flex_x, flex_y = np.zeros((h, w), np.float32), np.zeros((h, w), np.float32)

        for i in range(h):
            for j in range(w):
                dx, dy = j - w / 2, i - h / 2
                distance = np.sqrt((dx) ** 2 + (dy * (width / height)) ** 2)

                if distance < width:
                    factor = np.power(distance / width, 1 / scale)
                    flex_x[i, j] = max(0, min(w - 1, w / 2 + dx * factor))
                    flex_y[i, j] = max(0, min(h - 1, h / 2 + dy * factor))
                else:
                    flex_x[i, j], flex_y[i, j] = j, i

        dst = cv2.remap(roi, flex_x, flex_y, cv2.INTER_LINEAR)
        frame[y1:y2, x1:x2] = dst
        return frame

    def process_frame(self, frame):

        if self.current_filter == "gray":
            return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        if self.current_filter == "sepia":
            return self.apply_sepia(frame)

        results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.multi_face_landmarks:
            for face in results.multi_face_landmarks:
                ih, iw, _ = frame.shape

                if self.current_filter == "big_eyes":
                    face_w = int((face.landmark[454].x - face.landmark[234].x) * iw)
                    r = int(face_w * 0.15)
                    for idx in [468, 473]:
                        ex, ey = int(face.landmark[idx].x * iw), int(face.landmark[idx].y * ih)
                        frame = self.zoom_eye(frame, ex, ey, radius=r, scale=1.7)

                elif self.current_filter == "glasses" and self.glasses_img is not None:
                    lx, ly = int(face.landmark[33].x * iw), int(face.landmark[33].y * ih)
                    rx, ry = int(face.landmark[263].x * iw), int(face.landmark[263].y * ih)
                    angle = np.degrees(np.arctan2(ry - ly, rx - lx))
                    dist = np.sqrt((rx - lx) ** 2 + (ry - ly) ** 2)
                    w_g = int(dist * 2.7)
                    h_g = int(w_g * self.glasses_img.shape[0] / self.glasses_img.shape[1])
                    M = cv2.getRotationMatrix2D((w_g // 2, h_g // 2), -angle, 1)
                    rot_g = cv2.warpAffine(cv2.resize(self.glasses_img, (w_g, h_g)), M, (w_g, h_g))
                    frame = self.overlay_transparent(frame, rot_g, int(face.landmark[6].x * iw - w_g // 2),
                                                     int(face.landmark[6].y * ih - h_g // 2 + h_g * (-0.01)))
                if self.current_filter == "heart_eyes" and self.heart_img is not None:
                    for eye_idx in [468, 473]:
                        eye_pt = face.landmark[eye_idx]
                        ex, ey = int(eye_pt.x * iw), int(eye_pt.y * ih)

                        face_w = int((face.landmark[454].x - face.landmark[234].x) * iw)
                        h_size = int(face_w * 0.5)

                        offset_x = int(face_w * 0.00001)

                        if eye_idx == 468:
                            start_x = ex - h_size // 2 + offset_x
                        else:
                            start_x = ex - h_size // 2 - offset_x

                        start_y = ey - h_size // 2

                        frame = self.overlay_transparent(frame, self.heart_img, start_x, start_y, (h_size, h_size))
                elif self.current_filter == "big_mouth":
                    up_lip = face.landmark[13]
                    down_lip = face.landmark[14]

                    mouth_open = np.sqrt((up_lip.x - down_lip.x) ** 2 + (up_lip.y - down_lip.y) ** 2)

                    if mouth_open > 0.02:
                        cx = int((up_lip.x + down_lip.x) / 2 * iw)
                        cy = int((up_lip.y + down_lip.y) / 2 * ih)

                        face_w = int((face.landmark[454].x - face.landmark[234].x) * iw)

                        dynamic_scale = 1.0 + (mouth_open * 10)

                        frame = self.zoom_mouth(frame, cx, cy,
                                                width=int(face_w * 0.25),
                                                height=int(face_w * 0.2),
                                                scale=min(dynamic_scale, 2.5))

                elif self.current_filter == "crown" and self.crown_img is not None:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.face_mesh.process(rgb_frame)
                    if results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            ih, iw, _ = frame.shape

                            l_temple = face_landmarks.landmark[234]
                            r_temple = face_landmarks.landmark[454]

                            top_forehead = face_landmarks.landmark[10]

                            head_width = int(
                                np.sqrt((r_temple.x - l_temple.x) ** 2 + (r_temple.y - l_temple.y) ** 2) * iw)
                            crown_width = int(head_width * 1.2)
                            aspect_ratio = self.crown_img.shape[0] / self.crown_img.shape[1]
                            crown_height = int(crown_width * aspect_ratio)

                            cx, cy = int(top_forehead.x * iw), int(top_forehead.y * ih)

                            start_x = cx - crown_width // 2
                            start_y = cy - int(crown_height * 0.8)

                            angle = np.degrees(np.arctan2(r_temple.y - l_temple.y, r_temple.x - l_temple.x))

                            scaled_crown = cv2.resize(self.crown_img, (crown_width, crown_height))
                            M = cv2.getRotationMatrix2D((crown_width // 2, crown_height // 2), -angle, 1)
                            rotated_crown = cv2.warpAffine(scaled_crown, M, (crown_width, crown_height),
                                                           flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                                                           borderValue=(0, 0, 0, 0))

                            frame = self.overlay_transparent(frame, rotated_crown, start_x, start_y)

                elif self.current_filter == "mustache" and self.mustache_img is not None:
                    w_m = int((face.landmark[291].x - face.landmark[61].x) * iw * 1.6)
                    h_m = int(w_m * self.mustache_img.shape[0] / self.mustache_img.shape[1])
                    frame = self.overlay_transparent(frame, self.mustache_img,
                                                     int(face.landmark[164].x * iw - w_m // 2),
                                                     int(face.landmark[164].y * ih - h_m // 2 + 10), (w_m, h_m))
        return frame

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            processed = self.process_frame(frame)
            self.last_frame = processed.copy()
            img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=img, anchor=tk.NW)
            self.canvas.img = img
        self.window.after(10, self.update)

    def take_snapshot(self):
        if self.last_frame is not None:
            filename = f"photo_{int(time.time())}.jpg"
            cv2.imwrite(filename, self.last_frame)
            self.label.config(text=f"Фото сохранено как {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoBoothApp(root)
    root.mainloop()