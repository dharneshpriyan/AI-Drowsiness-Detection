import sys
import os
import math
import re
import cv2
import time
import numpy as np
import mediapipe as mp
import threading
import json
import webbrowser
from urllib.parse import quote

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QProgressBar, QGraphicsDropShadowEffect, QStackedWidget,
    QMessageBox, QDialog, QTextEdit, QGraphicsBlurEffect,
    QLineEdit, QFormLayout, QRadioButton
)
from PySide6.QtCore import QTimer
from PySide6.QtCore import QPropertyAnimation
from PySide6.QtWidgets import QGraphicsBlurEffect
from collections import deque
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPointF
from PySide6.QtWidgets import QDialog, QTextEdit
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QLinearGradient, QIcon, QPixmap, QImage, QPen, QConicalGradient, QRadialGradient
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QProgressBar, QGraphicsDropShadowEffect, QStackedWidget,
    QMessageBox
)

# =========================================================
# ---------------- OPTIONAL SOUND BACKENDS ----------------
# =========================================================

IS_WINDOWS = sys.platform.startswith("win")

try:
    import winsound
except Exception:
    winsound = None

try:
    from playsound import playsound
except Exception:
    playsound = None

# =========================================================
# ---------------- PATH HELPERS ---------------------------
# =========================================================

def resource_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def app_data_dir():
    path = os.path.join(os.path.expanduser("~"), "Documents", "AI_Drowsiness_App")
    os.makedirs(path, exist_ok=True)
    return path

def driver_data_file():
    return os.path.join(app_data_dir(), "driver_data.json")

def alert_config_file():
    return os.path.join(app_data_dir(), "alert_config.json")

def camera_config_file():
    return os.path.join(app_data_dir(), "camera_config.json")

def load_json(path, default_data):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_data
    return default_data

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def normalize_whatsapp_number(number: str) -> str:
    return re.sub(r"\D", "", number or "")

# =========================================================
# ---------------- THEME ----------------------------------
# =========================================================

ACCENT = "#19D4FF"
ACCENT_2 = "#4F8FFF"
ACCENT_GOLD = "#FFB347"
TEXT_MAIN = "#F5F7FA"
TEXT_SOFT = "#A6B2C3"
TEXT_DIM = "#6F7E93"
DANGER_1 = "#8B2F43"
DANGER_2 = "#C94661"
SUCCESS_1 = "#15D1FF"
SUCCESS_2 = "#4B8DFF"

# =========================================================
# ---------------- UI HELPERS -----------------------------
# =========================================================

def add_shadow(widget, blur=35, x=0, y=8, color=QColor(0, 0, 0, 130)):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(x, y)
    shadow.setColor(color)
    widget.setGraphicsEffect(shadow)

def add_glow(widget, color=QColor(24, 210, 255, 90), blur=45):
    glow = QGraphicsDropShadowEffect()
    glow.setBlurRadius(blur)
    glow.setOffset(0, 0)
    glow.setColor(color)
    widget.setGraphicsEffect(glow)

def pill_button(text, bg1, bg2=None, hover1="#25E0FF", hover2="#5C9CFF", text_color="white"):
    btn = QPushButton(text)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(50)
    btn.setFont(QFont("Segoe UI", 11, QFont.Bold))

    if bg2 is None:
        bg2 = bg1

    btn.setStyleSheet(f"""
        QPushButton {{
            color: {text_color};
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 25px;
            padding: 8px 22px;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {bg1},
                stop:1 {bg2}
            );
        }}
        QPushButton:hover {{
            border: 1px solid rgba(255,255,255,0.18);
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {hover1},
                stop:1 {hover2}
            );
        }}
        QPushButton:pressed {{
            padding-top: 12px;
            padding-left: 26px;
        }}
    """)
    add_shadow(btn, blur=30, y=6)
    return btn


def animated_action_button(text, bg1, bg2, hover1, hover2, glow_color, text_color=TEXT_MAIN):
    btn = QPushButton(text)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(52)
    btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
    btn.setStyleSheet(f"""
        QPushButton {{
            color: {text_color};
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 25px;
            padding: 8px 22px;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {bg1},
                stop:1 {bg2}
            );
        }}
        QPushButton:hover {{
            border: 1px solid rgba(255,255,255,0.24);
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {hover1},
                stop:1 {hover2}
            );
        }}
        QPushButton:pressed {{
            padding-top: 12px;
            padding-left: 26px;
        }}
    """)
    return btn

def nav_button(text):
    btn = QPushButton(text)
    btn.setFixedHeight(42)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
    btn.setStyleSheet(f"""
        QPushButton {{
            color: {TEXT_MAIN};
            background-color: rgba(255,255,255,0.02);
            border: 1px solid rgba(24,210,255,0.28);
            border-radius: 21px;
            padding: 0 20px;
        }}
        QPushButton:hover {{
            border: 1px solid {ACCENT};
            background-color: rgba(24,210,255,0.10);
        }}
    """)
    return btn

def card_frame(radius=26, border_alpha=28):
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background-color: rgba(12, 22, 39, 0.96);
            border: 1px solid rgba(255,255,255,{border_alpha});
            border-radius: {radius}px;
        }}
    """)
    add_shadow(frame, blur=50, y=12)
    return frame

class HoverInfoCard(QFrame):
    def __init__(self, title_text, body_text, parent=None):
        super().__init__(parent)
        self._base_style = """
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(12, 22, 39, 0.97),
                    stop:1 rgba(13, 25, 45, 0.97)
                );
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 24px;
            }
        """
        self._hover_style = """
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(14, 28, 49, 0.99),
                    stop:0.5 rgba(12, 32, 56, 0.99),
                    stop:1 rgba(10, 24, 45, 0.99)
                );
                border: 1px solid rgba(72,220,255,0.36);
                border-radius: 24px;
            }
        """
        self.setStyleSheet(self._base_style)
        self.setMinimumHeight(152)
        self.setCursor(Qt.PointingHandCursor)

        self.glow = QGraphicsDropShadowEffect(self)
        self.glow.setBlurRadius(34)
        self.glow.setOffset(0, 10)
        self.glow.setColor(QColor(0, 0, 0, 125))
        self.setGraphicsEffect(self.glow)

        self.glow_anim = QPropertyAnimation(self.glow, b"blurRadius", self)
        self.glow_anim.setDuration(220)
        self.glow_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.layout_anim = QPropertyAnimation(self.glow, b"offset", self)
        self.layout_anim.setDuration(220)
        self.layout_anim.setEasingCurve(QEasingCurve.OutCubic)

        c_layout = QVBoxLayout(self)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(10)

        top = QLabel(title_text)
        top.setFont(QFont("Segoe UI", 10))
        top.setStyleSheet(f"color: {TEXT_SOFT}; border:none; background:transparent;")

        body = QLabel(body_text)
        body.setFont(QFont("Segoe UI", 14, QFont.Bold))
        body.setWordWrap(True)
        body.setStyleSheet(f"color: {TEXT_MAIN}; border:none; background:transparent;")

        c_layout.addWidget(top)
        c_layout.addWidget(body)
        c_layout.addStretch()

    def enterEvent(self, event):
        self.setStyleSheet(self._hover_style)
        self.glow.setColor(QColor(24, 210, 255, 72))
        self.glow_anim.stop()
        self.glow_anim.setStartValue(self.glow.blurRadius())
        self.glow_anim.setEndValue(56)
        self.glow_anim.start()
        self.layout_anim.stop()
        self.layout_anim.setStartValue(self.glow.offset())
        self.layout_anim.setEndValue(QPointF(0, 0))
        self.layout_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self._base_style)
        self.glow.setColor(QColor(0, 0, 0, 125))
        self.glow_anim.stop()
        self.glow_anim.setStartValue(self.glow.blurRadius())
        self.glow_anim.setEndValue(34)
        self.glow_anim.start()
        self.layout_anim.stop()
        self.layout_anim.setStartValue(self.glow.offset())
        self.layout_anim.setEndValue(QPointF(0, 10))
        self.layout_anim.start()
        super().leaveEvent(event)

def clean_info_card(title_text, body_text):
    return HoverInfoCard(title_text, body_text)

# =========================================================
# ---------------- ANIMATED BACKGROUND --------------------
# =========================================================

class AnimatedGradientWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.phase = 0.0
        self.phase2 = 0.0
        self.phase3 = 0.0
        self.pulse = 0.0
        self.orb_phase = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_background)
        self.timer.start(16)

    def animate_background(self):
        self.phase += 0.05
        self.phase2 += 0.036
        self.phase3 += 0.028
        self.pulse += 0.065
        self.orb_phase += 0.04
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#040B16"))
        gradient.setColorAt(0.22, QColor("#06152A"))
        gradient.setColorAt(0.58, QColor("#0A2341"))
        gradient.setColorAt(0.82, QColor("#081B31"))
        gradient.setColorAt(1.0, QColor("#0D1224"))
        painter.fillRect(self.rect(), gradient)

        painter.setPen(Qt.NoPen)

        width = self.width()
        height = self.height()
        pulse_wave = (np.sin(self.pulse) + 1.0) / 2.0
        drift_wave = (np.cos(self.orb_phase) + 1.0) / 2.0

        # left atmospheric cyan field
        left_gradient = QRadialGradient(
            -90 + (np.sin(self.phase) * 170),
            190 + (np.cos(self.phase2) * 110),
            500 + (pulse_wave * 90)
        )
        left_gradient.setColorAt(0.0, QColor(24, 210, 255, 60 + int(pulse_wave * 16)))
        left_gradient.setColorAt(0.35, QColor(18, 156, 220, 34))
        left_gradient.setColorAt(1.0, QColor(24, 210, 255, 0))
        painter.setBrush(left_gradient)
        painter.drawEllipse(-260, -10, 760, 760)

        # center deep blue orbital glow
        center_gradient = QRadialGradient(
            (width * 0.52) + (np.sin(self.phase2) * 150),
            120 + (np.cos(self.phase) * 80),
            350 + (np.sin(self.phase3) * 65)
        )
        center_gradient.setColorAt(0.0, QColor(76, 136, 255, 46))
        center_gradient.setColorAt(0.42, QColor(55, 100, 210, 24))
        center_gradient.setColorAt(1.0, QColor(76, 136, 255, 0))
        painter.setBrush(center_gradient)
        painter.drawEllipse(int(width * 0.28), -110, 520, 520)

        # right-bottom violet parallax glow
        violet_gradient = QRadialGradient(
            width - 120 + (np.cos(self.phase3) * 130),
            height - 110 + (np.sin(self.phase2) * 90),
            370 + (np.cos(self.phase) * 55)
        )
        violet_gradient.setColorAt(0.0, QColor(120, 96, 255, 38))
        violet_gradient.setColorAt(0.38, QColor(92, 76, 208, 20))
        violet_gradient.setColorAt(1.0, QColor(120, 96, 255, 0))
        painter.setBrush(violet_gradient)
        painter.drawEllipse(width - 430, height - 310, 560, 560)

        # warm floating highlight for depth
        gold_gradient = QRadialGradient(
            (width * 0.62) + (np.sin(self.phase * 1.4) * 120),
            180 + (np.cos(self.phase3) * 90),
            210 + (pulse_wave * 45)
        )
        gold_gradient.setColorAt(0.0, QColor(255, 190, 96, 28))
        gold_gradient.setColorAt(0.45, QColor(255, 156, 64, 14))
        gold_gradient.setColorAt(1.0, QColor(255, 190, 96, 0))
        painter.setBrush(gold_gradient)
        painter.drawEllipse(int(width * 0.42), 10, 320, 320)

        # subtle moving light haze
        haze_gradient = QLinearGradient(
            0,
            height * (0.18 + (np.sin(self.phase2) * 0.03)),
            width,
            height * (0.92 + (np.cos(self.phase3) * 0.02))
        )
        haze_gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
        haze_gradient.setColorAt(0.32, QColor(120, 196, 255, 14))
        haze_gradient.setColorAt(0.5, QColor(255, 255, 255, 16))
        haze_gradient.setColorAt(0.72, QColor(72, 162, 255, 12))
        haze_gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(haze_gradient)
        painter.drawRoundedRect(self.rect(), 0, 0)

        # faint drifting bloom near bottom to keep motion alive
        bloom_gradient = QRadialGradient(
            (width * 0.26) + (np.cos(self.phase * 1.1) * 120),
            height - 60 + (np.sin(self.phase3 * 1.2) * 25),
            220
        )
        bloom_gradient.setColorAt(0.0, QColor(32, 220, 255, 12))
        bloom_gradient.setColorAt(0.55, QColor(32, 220, 255, 4))
        bloom_gradient.setColorAt(1.0, QColor(32, 220, 255, 0))
        painter.setBrush(bloom_gradient)
        painter.drawEllipse(int(width * 0.08), height - 250, 360, 260)

        # clearly visible drifting neon orbs
        orb_specs = [
            (
                width * 0.18 + (np.sin(self.orb_phase) * 180),
                height * 0.72 + (np.cos(self.orb_phase * 1.2) * 45),
                26 + (pulse_wave * 8),
                QColor(36, 222, 255, 72)
            ),
            (
                width * 0.78 + (np.cos(self.orb_phase * 0.85) * 140),
                height * 0.22 + (np.sin(self.orb_phase * 1.3) * 60),
                18 + (drift_wave * 10),
                QColor(255, 196, 92, 58)
            ),
            (
                width * 0.60 + (np.sin(self.orb_phase * 1.5) * 120),
                height * 0.84 + (np.cos(self.orb_phase) * 35),
                20 + (pulse_wave * 7),
                QColor(145, 108, 255, 60)
            ),
        ]
        for orb_x, orb_y, orb_size, orb_color in orb_specs:
            orb_gradient = QRadialGradient(orb_x, orb_y, orb_size * 2.8)
            orb_gradient.setColorAt(0.0, orb_color)
            orb_gradient.setColorAt(0.4, QColor(orb_color.red(), orb_color.green(), orb_color.blue(), max(10, orb_color.alpha() // 3)))
            orb_gradient.setColorAt(1.0, QColor(orb_color.red(), orb_color.green(), orb_color.blue(), 0))
            painter.setBrush(orb_gradient)
            painter.drawEllipse(int(orb_x - orb_size * 2.2), int(orb_y - orb_size * 2.2), int(orb_size * 4.4), int(orb_size * 4.4))

        super().paintEvent(event)

class PremiumDialog(QDialog):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        
        self.setWindowOpacity(0)

        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(250)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()
        
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(500, 360)

        # ---------- main layout ----------
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ---------- glass card ----------
        self.card = QFrame()
        self.card.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(8,16,31,0.985),
                    stop:0.58 rgba(6,13,26,0.985),
                    stop:1 rgba(4,9,18,0.99)
                );
                border-radius: 26px;
                border: 1px solid rgba(130,180,255,0.16);
            }
        """)
        outer.addWidget(self.card)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(62)
        glow.setOffset(0, 0)
        glow.setColor(QColor(26, 170, 255, 88))
        self.card.setGraphicsEffect(glow)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(26, 20, 26, 22)
        layout.setSpacing(12)

        # ---------- top bar ----------
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2BD2FF;
                border: none;
                background: transparent;
                letter-spacing: 0.2px;
            }
        """)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        close_btn.setStyleSheet("""
            QPushButton {
                color: #F2F8FF;
                background-color: rgba(255,255,255,0.035);
                border: 1px solid rgba(255,255,255,0.11);
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.18);
                color: #FFFFFF;
            }
        """)
        close_btn.clicked.connect(self.close)

        top_bar.addWidget(title_label)
        top_bar.addStretch()
        top_bar.addWidget(close_btn)

        # ---------- divider ----------
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: rgba(107, 164, 255, 0.14); border:none;")

        # ---------- content ----------
        content_box = QTextEdit()
        content_box.setReadOnly(True)
        content_box.setFrameShape(QFrame.NoFrame)
        content_box.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_box.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: #E7EEF8;
                font: 11pt 'Segoe UI';
                line-height: 1.62;
                padding: 8px 4px 8px 2px;
                selection-background-color: rgba(43,210,255,0.24);
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.025);
                width: 10px;
                border-radius: 5px;
                margin: 6px 0 6px 0;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(42, 208, 255, 0.92),
                    stop:1 rgba(48, 132, 255, 0.92)
                );
                border-radius: 5px;
                min-height: 34px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        content_box.setFont(QFont("Segoe UI", 11))
        content_box.setText(content)

        # ---------- ok button ----------
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        ok_btn = QPushButton("Close")
        ok_btn.setFixedSize(122, 42)
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        ok_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #24CBFF,
                    stop:1 #4D8DFF
                );
                color: #03111C;
                border: none;
                border-radius: 21px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3ADCFF,
                    stop:1 #69A5FF
                );
            }
        """)
        ok_btn.clicked.connect(self.close)

        btn_row.addWidget(ok_btn)
        btn_row.addStretch()

        layout.addLayout(top_bar)
        layout.addWidget(divider)
        layout.addWidget(content_box)
        layout.addLayout(btn_row)

        # ---------- fade-in ----------
        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(220)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)

    def showEvent(self, event):
        super().showEvent(event)
        self.fade_anim.start()
        
class DialogOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(4, 10, 20, 70);")
        self.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())


class AnimatedLogoOrb(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ring_angle = 0.0
        self.setFixedSize(182, 182)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def set_ring_angle(self, angle):
        self.ring_angle = angle % 360.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        outer_rect = self.rect().adjusted(8, 8, -8, -8)
        inner_rect = self.rect().adjusted(18, 18, -18, -18)
        center = outer_rect.center()

        background = QRadialGradient(center, outer_rect.width() * 0.55)
        background.setColorAt(0.0, QColor(24, 44, 88, 252))
        background.setColorAt(0.56, QColor(10, 24, 46, 245))
        background.setColorAt(1.0, QColor(6, 12, 24, 235))
        painter.setPen(Qt.NoPen)
        painter.setBrush(background)
        painter.drawEllipse(outer_rect)

        base_pen = QPen(QColor(92, 220, 255, 72), 3.2)
        painter.setPen(base_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(outer_rect)

        orbit_gradient = QConicalGradient(center, self.ring_angle)
        orbit_gradient.setColorAt(0.00, QColor(255, 255, 255, 0))
        orbit_gradient.setColorAt(0.08, QColor(92, 232, 255, 235))
        orbit_gradient.setColorAt(0.18, QColor(34, 187, 255, 160))
        orbit_gradient.setColorAt(0.30, QColor(255, 255, 255, 0))
        orbit_gradient.setColorAt(1.00, QColor(255, 255, 255, 0))

        orbit_pen = QPen(orbit_gradient, 5.6)
        orbit_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(orbit_pen)
        painter.drawEllipse(outer_rect)

        inner_pen = QPen(QColor(255, 255, 255, 36), 1.1)
        painter.setPen(inner_pen)
        painter.drawEllipse(inner_rect)

        theta = math.radians(self.ring_angle)
        radius = outer_rect.width() / 2.0
        dot_x = center.x() + math.cos(theta) * radius
        dot_y = center.y() - math.sin(theta) * radius
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 214, 120, 230))
        painter.drawEllipse(int(dot_x) - 5, int(dot_y) - 5, 10, 10)

        super().paintEvent(event)


class TrendGraphWidget(QWidget):
    def __init__(self, title, line_color, fill_color, parent=None):
        super().__init__(parent)
        self.title = title
        self.values = []
        self.line_color = line_color
        self.fill_color = fill_color
        self.setMinimumHeight(72)

    def set_values(self, values):
        self.values = list(values)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(10, 20, 36, 210))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 18, 18)

        painter.setPen(QColor(170, 188, 208))
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.drawText(12, 20, self.title)

        chart_rect = self.rect().adjusted(10, 26, -10, -8)
        painter.setPen(QColor(255, 255, 255, 18))
        for step in range(3):
            y = chart_rect.top() + int((step / 2) * chart_rect.height())
            painter.drawLine(chart_rect.left(), y, chart_rect.right(), y)

        if len(self.values) < 2:
            return

        min_val = min(self.values)
        max_val = max(self.values)
        if abs(max_val - min_val) < 1e-6:
            max_val += 1.0
            min_val -= 1.0

        points = []
        for index, value in enumerate(self.values):
            x = chart_rect.left() + (index / (len(self.values) - 1)) * chart_rect.width()
            norm = (value - min_val) / (max_val - min_val)
            y = chart_rect.bottom() - (norm * chart_rect.height())
            points.append((x, y))

        path = None
        try:
            from PySide6.QtGui import QPainterPath
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            for x, y in points[1:]:
                path.lineTo(x, y)

            fill_path = QPainterPath(path)
            fill_path.lineTo(chart_rect.right(), chart_rect.bottom())
            fill_path.lineTo(chart_rect.left(), chart_rect.bottom())
            fill_path.closeSubpath()

            painter.setPen(Qt.NoPen)
            painter.setBrush(self.fill_color)
            painter.drawPath(fill_path)

            line_pen = QPen(self.line_color, 2.5)
            line_pen.setCapStyle(Qt.RoundCap)
            line_pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(line_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
        except Exception:
            line_pen = QPen(self.line_color, 2.5)
            painter.setPen(line_pen)
            for idx in range(len(points) - 1):
                painter.drawLine(
                    int(points[idx][0]), int(points[idx][1]),
                    int(points[idx + 1][0]), int(points[idx + 1][1])
                )
        
# =========================================================
# ---------------- DETECTOR ENGINE ------------------------
# =========================================================

class DetectorEngine:
    def __init__(self):
        self.cap = None
        self.prev = time.time()
        self.alarm = False
        self.alarm_thread = None

        self.drowsy_event_count = 0
        self.previous_drowsy_state = False
        self.whatsapp_alert_sent = False

        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        self.MOUTH = [13, 14, 78, 308]

        self.NOSE = 1
        self.CHIN = 152
        self.LEFT_FACE = 234
        self.RIGHT_FACE = 454

        self.EAR_THRESH = 0.23
        self.MAR_THRESH = 0.65
        self.HEAD_THRESH = 20
        self.FRAME_LIMIT = 20

        self.ear_buffer = deque(maxlen=10)
        self.mar_buffer = deque(maxlen=10)
        self.ear_history = deque(maxlen=60)
        self.mar_history = deque(maxlen=60)
        self.attention_history = deque(maxlen=60)

        self.eye_closed_frames = 0
        self.head_frames = 0
        self.attention_score = 100
        self.ear_avg = 0.0
        self.mar_avg = 0.0
        self.yaw = 0.0
        self.status = "ACTIVE"
        self.status_color = (0, 255, 0)
        self.alert_active = False
        self.blink_state = False
        self.blink_timer = time.time()
        self.alert_start_time = None
        self.ALARM_DELAY = 0.5
        self.fps = 0

        self.alarm_file = resource_path("assets/alarm.wav")

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def send_whatsapp_alert(self):
        alert_data = load_json(alert_config_file(), {
            "enabled": True,
            "owner_whatsapp": ""
        })
        if not alert_data.get("enabled", True):
            return False

        driver_data = load_json(driver_data_file(), {
            "name": "",
            "mobile": "",
            "age": ""
        })

        number = normalize_whatsapp_number(alert_data.get("owner_whatsapp", "").strip())
        if not number:
            return False

        timestamp = time.strftime("%d-%m-%Y %I:%M:%S %p")

        message = (
            f"ALERT: Driver drowsiness detected 3 times.\n\n"
            f"Time: {timestamp}\n"
            f"Driver Name: {driver_data.get('name', '')}\n"
            f"Driver Mobile: {driver_data.get('mobile', '')}\n"
            f"Driver Age: {driver_data.get('age', '')}\n"
            f"Attention Score: {self.attention_score}%\n"
        )

        encoded_message = quote(message)
        url = f"https://api.whatsapp.com/send?phone={number}&text={encoded_message}"
        opened = webbrowser.open(url)
        return opened

    def start(self):
        camera_data = load_json(camera_config_file(), {
            "camera_source": "0",
            "last_external_camera_source": ""
        })
        source = camera_data.get("camera_source", "0")

        if source.isdigit():
            source = int(source)

        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def stop(self):
        self.stop_alarm()
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    # ---------------- SOUND ----------------

    def _windows_alarm_loop(self):
        try:
            winsound.PlaySound(
                self.alarm_file,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP
            )
        except Exception:
            pass

    def _playsound_loop(self):
        while self.alarm:
            try:
                playsound(self.alarm_file)
            except Exception:
                time.sleep(0.7)

    def start_alarm(self):
        if self.alarm:
            return
        self.alarm = True

        if IS_WINDOWS and winsound is not None and os.path.exists(self.alarm_file):
            self._windows_alarm_loop()
        elif playsound is not None and os.path.exists(self.alarm_file):
            self.alarm_thread = threading.Thread(target=self._playsound_loop, daemon=True)
            self.alarm_thread.start()

    def stop_alarm(self):
        self.alarm = False
        if IS_WINDOWS and winsound is not None:
            try:
                winsound.PlaySound(None, 0)
            except Exception:
                pass

    # ---------------- METRICS ----------------

    def distance(self, a, b):
        return np.linalg.norm(a - b)

    def compute_EAR(self, lm, eye):
        v1 = self.distance(lm[eye[1]], lm[eye[5]])
        v2 = self.distance(lm[eye[2]], lm[eye[4]])
        h = self.distance(lm[eye[0]], lm[eye[3]])
        if h == 0:
            return 0.0
        return (v1 + v2) / (2 * h)

    def compute_MAR(self, lm):
        v = self.distance(lm[self.MOUTH[0]], lm[self.MOUTH[1]])
        h = self.distance(lm[self.MOUTH[2]], lm[self.MOUTH[3]])
        if h == 0:
            return 0.0
        return v / h

    def head_pose(self, frame, lm):
        try:
            size = frame.shape

            image_pts = np.array([
                lm[self.NOSE],
                lm[self.CHIN],
                lm[self.LEFT_FACE],
                lm[self.RIGHT_FACE]
            ], dtype="double")

            model_pts = np.array([
                (0, 0, 0),
                (0, -330, -65),
                (-225, 170, -135),
                (225, 170, -135)
            ], dtype="double")

            focal = size[1]
            center = (size[1] / 2, size[0] / 2)

            cam_matrix = np.array([
                [focal, 0, center[0]],
                [0, focal, center[1]],
                [0, 0, 1]
            ], dtype="double")

            dist_coeffs = np.zeros((4, 1))

            success, rot_vec, trans_vec = cv2.solvePnP(
                model_pts,
                image_pts,
                cam_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )

            if not success:
                return 0, 0, 0

            rmat, _ = cv2.Rodrigues(rot_vec)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
            pitch, yaw, roll = angles
            return pitch, yaw, roll
        except Exception:
            return 0, 0, 0

    def get_frame(self):
        if self.cap is None:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        current = time.time()
        time_diff = current - self.prev
        self.fps = 1 / time_diff if time_diff > 0 else 0
        self.prev = current

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(rgb)

        self.status = "ACTIVE"
        self.status_color = (0, 255, 0)

        if result.multi_face_landmarks:
            face = result.multi_face_landmarks[0]
            h, w, _ = frame.shape

            lm = np.array([
                (int(p.x * w), int(p.y * h))
                for p in face.landmark
            ])

            ear = (self.compute_EAR(lm, self.LEFT_EYE) + self.compute_EAR(lm, self.RIGHT_EYE)) / 2
            mar = self.compute_MAR(lm)

            self.ear_buffer.append(ear)
            self.mar_buffer.append(mar)

            self.ear_avg = float(np.mean(self.ear_buffer)) if self.ear_buffer else 0.0
            self.mar_avg = float(np.mean(self.mar_buffer)) if self.mar_buffer else 0.0

            pitch, self.yaw, roll = self.head_pose(frame, lm)

            if self.ear_avg < self.EAR_THRESH:
                self.eye_closed_frames += 1
            else:
                self.eye_closed_frames = 0

            if abs(self.yaw) > self.HEAD_THRESH:
                self.head_frames += 1
            else:
                self.head_frames = 0

            self.attention_score = 100
            self.attention_score -= min(40, self.eye_closed_frames * 2)
            self.attention_score -= min(30, self.head_frames * 2)
            if self.mar_avg > self.MAR_THRESH:
                self.attention_score -= 30
            self.attention_score = max(0, self.attention_score)
            self.ear_history.append(self.ear_avg)
            self.mar_history.append(self.mar_avg)
            self.attention_history.append(self.attention_score)

            if self.eye_closed_frames > self.FRAME_LIMIT:
                self.status = "DROWSY"
                self.status_color = (0, 0, 255)
                self.alert_active = True
            elif self.mar_avg > self.MAR_THRESH:
                self.status = "YAWNING"
                self.status_color = (0, 165, 255)
                self.alert_active = False
            elif self.head_frames > self.FRAME_LIMIT:
                self.status = "DISTRACTED"
                self.status_color = (255, 0, 255)
                self.alert_active = False
            else:
                self.alert_active = False

            if self.status != "ACTIVE":
                if self.alert_start_time is None:
                    self.alert_start_time = time.time()

                if time.time() - self.alert_start_time >= self.ALARM_DELAY:
                    self.start_alarm()
            else:
                self.alert_start_time = None
                self.stop_alarm()

            for p in self.LEFT_EYE + self.RIGHT_EYE:
                cv2.circle(frame, tuple(lm[p]), 1, (255, 255, 0), -1)

        current_drowsy_state = (self.status == "DROWSY")

        if current_drowsy_state and not self.previous_drowsy_state:
            self.drowsy_event_count += 1
            if self.drowsy_event_count >= 3 and not self.whatsapp_alert_sent:
                self.send_whatsapp_alert()
                self.whatsapp_alert_sent = True

        self.previous_drowsy_state = current_drowsy_state
        return frame
# =========================================================
# ---------------- CAMERA PAGE ----------------------------
# =========================================================

class CameraPage(QWidget):
    def __init__(self, stacked):
        super().__init__()
        self.stacked = stacked
        self.engine = DetectorEngine()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background:#000000;")
        root.addWidget(self.video_label)

        # top overlay
        self.top_bar = QFrame(self)
        self.top_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 16, 28, 180);
                border: none;
                border-radius: 0px;
            }
        """)
        self.top_bar.setFixedHeight(58)

        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(16, 4, 16, 4)
        top_layout.setSpacing(14)

        self.title_label = QLabel("AI Drowsiness Monitoring System")
        self.title_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.title_label.setStyleSheet("color: #F5F7FA;")

        self.status_label = QLabel("STATUS: ACTIVE")
        self.status_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.status_label.setStyleSheet("color: #00FF78;")

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.addWidget(self.title_label)
        text_col.addWidget(self.status_label)

        top_layout.addLayout(text_col)
        top_layout.addStretch()

        self.live_dot = QFrame(self.top_bar)
        self.live_dot.setFixedSize(12, 12)
        self.live_dot.setStyleSheet("""
            QFrame {
                background-color: #FF3B3B;
                border-radius: 6px;
                border: 1px solid rgba(255,255,255,0.20);
            }
        """)

        self.live_label = QLabel("LIVE")
        self.live_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.live_label.setStyleSheet("color: #FFD8D8; border:none; background:transparent;")

        live_row = QHBoxLayout()
        live_row.setSpacing(8)
        live_row.addWidget(self.live_dot, 0, Qt.AlignVCenter)
        live_row.addWidget(self.live_label, 0, Qt.AlignVCenter)
        top_layout.addLayout(live_row)

        self.top_bar.raise_()

        self.bottom_bar = QFrame(self)
        self.bottom_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(8, 14, 26, 195);
                border-top: 1px solid rgba(255,255,255,0.08);
                border-left: none;
                border-right: none;
                border-bottom: none;
            }
        """)
        bottom_bar_glow = QGraphicsDropShadowEffect()
        bottom_bar_glow.setBlurRadius(24)
        bottom_bar_glow.setOffset(0, -2)
        bottom_bar_glow.setColor(QColor(24, 210, 255, 18))
        self.bottom_bar.setGraphicsEffect(bottom_bar_glow)

        self.bottom_metrics = QFrame(self)
        self.bottom_metrics.setStyleSheet("""
            QFrame {
                background-color: rgba(8, 14, 26, 205);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 18px;
            }
        """)
        metrics_glow = QGraphicsDropShadowEffect()
        metrics_glow.setBlurRadius(18)
        metrics_glow.setOffset(0, 0)
        metrics_glow.setColor(QColor(24, 210, 255, 24))
        self.bottom_metrics.setGraphicsEffect(metrics_glow)

        metrics_layout = QHBoxLayout(self.bottom_metrics)
        metrics_layout.setContentsMargins(16, 10, 16, 10)

        self.bottom_metrics_label = QLabel("FPS: 0   EAR: 0.00   Yawn: 0.00")
        self.bottom_metrics_label.setAlignment(Qt.AlignCenter)
        self.bottom_metrics_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.bottom_metrics_label.setStyleSheet("color: #E8F3FF; border:none; background:transparent;")
        metrics_layout.addWidget(self.bottom_metrics_label)

        self.driver_info_bar = QFrame(self)
        self.driver_info_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(6, 16, 30, 224),
                    stop:0.55 rgba(10, 24, 43, 216),
                    stop:1 rgba(14, 36, 58, 208)
                );
                border: 1px solid rgba(73, 183, 255, 0.24);
                border-radius: 20px;
            }
        """)
        driver_glow = QGraphicsDropShadowEffect()
        driver_glow.setBlurRadius(22)
        driver_glow.setOffset(0, 0)
        driver_glow.setColor(QColor(24, 210, 255, 32))
        self.driver_info_bar.setGraphicsEffect(driver_glow)

        driver_layout = QHBoxLayout(self.driver_info_bar)
        driver_layout.setContentsMargins(18, 10, 18, 10)
        driver_layout.setSpacing(16)

        name_col = QVBoxLayout()
        name_col.setSpacing(1)

        self.driver_info_title = QLabel("DRIVER")
        self.driver_info_title.setFont(QFont("Bahnschrift SemiBold", 8, QFont.Bold))
        self.driver_info_title.setStyleSheet("color: #6FDFFF; letter-spacing: 1px; border:none; background:transparent;")

        self.driver_name_label = QLabel("Not Set")
        self.driver_name_label.setFont(QFont("Trebuchet MS", 11, QFont.Bold))
        self.driver_name_label.setStyleSheet("color: #F7FBFF; border:none; background:transparent;")

        name_col.addWidget(self.driver_info_title)
        name_col.addWidget(self.driver_name_label)

        score_col = QVBoxLayout()
        score_col.setSpacing(0)

        self.attention_title_label = QLabel("ATTENTION")
        self.attention_title_label.setAlignment(Qt.AlignRight)
        self.attention_title_label.setFont(QFont("Bahnschrift SemiBold", 8, QFont.Bold))
        self.attention_title_label.setStyleSheet("color: #8BE6A7; letter-spacing: 1px; border:none; background:transparent;")

        self.attention_value_label = QLabel("100%")
        self.attention_value_label.setAlignment(Qt.AlignRight)
        self.attention_value_label.setFont(QFont("Trebuchet MS", 13, QFont.Bold))
        self.attention_value_label.setStyleSheet("color: #D8FFF0; border:none; background:transparent;")

        score_col.addWidget(self.attention_title_label)
        score_col.addWidget(self.attention_value_label)

        driver_layout.addLayout(name_col, 3)
        driver_layout.addLayout(score_col, 1)

        # exit button
        self.exit_btn = QPushButton("EXIT", self)
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.setFixedSize(90, 38)
        self.exit_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.exit_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8B2F43,
                    stop:1 #C94661
                );
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 19px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A63C54,
                    stop:1 #DE5B79
                );
            }
        """)
        self.exit_btn.clicked.connect(self.back_to_home)

        self.top_bar.raise_()
        self.bottom_bar.raise_()
        self.driver_info_bar.raise_()
        self.bottom_metrics.raise_()
        self.exit_btn.raise_()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.top_bar.setGeometry(0, 0, self.width(), 58)
        bottom_bar_height = 58
        self.bottom_bar.setGeometry(0, self.height() - bottom_bar_height, self.width(), bottom_bar_height)
        driver_width = 320
        driver_height = 54
        self.driver_info_bar.setGeometry(
            18,
            self.height() - driver_height - 2,
            driver_width,
            driver_height
        )
        metrics_width = 320
        metrics_height = 46
        self.bottom_metrics.setGeometry(
            self.width() // 2 - metrics_width // 2,
            self.height() - metrics_height - 6,
            metrics_width,
            metrics_height
        )
        self.exit_btn.move(self.width() - 110, self.height() - 48)

    def start_camera(self):
        self.engine.start()
        self.engine.whatsapp_alert_sent = False
        self.engine.drowsy_event_count = 0
        self.engine.ear_history.clear()
        self.engine.mar_history.clear()
        self.engine.attention_history.clear()
        self.timer.start(30)

    def stop_camera(self):
        self.timer.stop()
        self.engine.stop()
        self.video_label.clear()

    def back_to_home(self):
        self.stop_camera()
        self.stacked.setCurrentIndex(0)

    def update_frame(self):
        frame = self.engine.get_frame()
        if frame is None:
            return

        # blinking alert text
        if self.engine.alert_active:
            if time.time() - self.engine.blink_timer > 0.5:
                self.engine.blink_state = not self.engine.blink_state
                self.engine.blink_timer = time.time()

            if self.engine.blink_state:
                cv2.putText(
                    frame,
                    "!! DROWSINESS ALERT !!",
                    (frame.shape[1] // 2 - 190, frame.shape[0] // 2),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1.0,
                    (0, 0, 255),
                    3,
                    cv2.LINE_AA
                )

        # green border
        glow_color = (0, 255, 150)
        cv2.rectangle(frame, (0, 0), (frame.shape[1] - 1, frame.shape[0] - 1), glow_color, 2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)

        self.video_label.setPixmap(
            pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
        )

        # update labels
        self.status_label.setText(f"STATUS: {self.engine.status}")
        if self.engine.status == "ACTIVE":
            self.status_label.setStyleSheet("color: #00FF78;")
        elif self.engine.status == "DROWSY":
            self.status_label.setStyleSheet("color: #FF3B3B;")
        elif self.engine.status == "YAWNING":
            self.status_label.setStyleSheet("color: #FFA726;")
        else:
            self.status_label.setStyleSheet("color: #FF60FF;")

        live_on = int(time.time() * 2) % 2 == 0
        if live_on:
            self.live_dot.setStyleSheet("""
                QFrame {
                    background-color: #FF3B3B;
                    border-radius: 6px;
                    border: 1px solid rgba(255,255,255,0.20);
                }
            """)
        else:
            self.live_dot.setStyleSheet("""
                QFrame {
                    background-color: rgba(255,59,59,0.22);
                    border-radius: 6px;
                    border: 1px solid rgba(255,255,255,0.10);
                }
            """)

        driver_data = load_json(driver_data_file(), {
            "name": "",
            "mobile": "",
            "age": ""
        })
        driver_name = driver_data.get("name", "").strip() or "Not Set"
        self.driver_name_label.setText(driver_name)

        score = self.engine.attention_score
        if score >= 80:
            score_color = "#8CFFB6"
        elif score >= 60:
            score_color = "#7CE5FF"
        elif score >= 40:
            score_color = "#FFD37A"
        else:
            score_color = "#FF8798"
        self.attention_value_label.setText(f"{score}%")
        self.attention_value_label.setStyleSheet(f"color: {score_color}; border:none; background:transparent;")

        self.bottom_metrics_label.setText(
            f"FPS: {int(self.engine.fps)}   "
            f"EAR: {self.engine.ear_avg:.2f}   "
            f"Yawn: {self.engine.mar_avg:.2f}"
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.back_to_home()



# =========================================================
# ---------------- LOADING PAGE ---------------------------
# =========================================================

class LoadingPage(AnimatedGradientWidget):
    def __init__(self, stacked):
        super().__init__()
        self.stacked = stacked
        self.progress_value = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        center = QVBoxLayout()
        center.setSpacing(18)
        center.setAlignment(Qt.AlignCenter)

        card = card_frame(radius=28, border_alpha=30)
        card.setFixedSize(760, 255)
        add_glow(card, QColor(24, 210, 255, 28), 48)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 34, 36, 34)
        card_layout.setSpacing(18)

        self.title = QLabel("Initializing AI Drowsiness Monitoring System")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title.setStyleSheet(f"color: {TEXT_MAIN}; border:none; background:transparent;")

        self.sub = QLabel("Loading computer vision engine, camera pipeline, and safety monitor...")
        self.sub.setAlignment(Qt.AlignCenter)
        self.sub.setWordWrap(True)
        self.sub.setFont(QFont("Segoe UI", 11))
        self.sub.setStyleSheet(f"color: {TEXT_SOFT}; border:none; background:transparent;")

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(20)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 10px;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #19D4FF,
                    stop:0.55 #3FE6FF,
                    stop:1 #4F8FFF
                );
            }
        """)
        add_glow(self.progress, QColor(24, 210, 255, 75), 30)

        self.percent = QLabel("0%")
        self.percent.setAlignment(Qt.AlignCenter)
        self.percent.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.percent.setStyleSheet(f"color: {TEXT_MAIN}; border:none; background:transparent;")

        self.status = QLabel("Preparing modules...")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFont(QFont("Segoe UI", 10))
        self.status.setStyleSheet(f"color: {TEXT_SOFT}; border:none; background:transparent;")

        card_layout.addWidget(self.title)
        card_layout.addWidget(self.sub)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.progress)
        card_layout.addWidget(self.percent)
        card_layout.addWidget(self.status)

        center.addWidget(card)
        root.addLayout(center)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

    def start_loading(self):
        self.progress_value = 0
        self.progress.setValue(0)
        self.percent.setText("0%")
        self.status.setText("Preparing modules...")
        self.stacked.setCurrentIndex(1)
        self.timer.start(28)

    def update_progress(self):
        self.progress_value += 2
        if self.progress_value > 100:
            self.progress_value = 100

        self.progress.setValue(self.progress_value)
        self.percent.setText(f"{self.progress_value}%")

        if self.progress_value < 25:
            self.status.setText("Loading premium launcher UI...")
        elif self.progress_value < 50:
            self.status.setText("Starting camera configuration...")
        elif self.progress_value < 75:
            self.status.setText("Initializing face mesh engine...")
        elif self.progress_value < 100:
            self.status.setText("Preparing live monitoring page...")
        else:
            self.timer.stop()
            self.stacked.setCurrentIndex(2)
            self.stacked.camera_page.start_camera()
            
FORM_CARD_STYLE = """
    QFrame {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(8,18,34,0.96),
            stop:1 rgba(6,12,24,0.96)
        );
        border-radius: 22px;
        border: 1px solid rgba(255,255,255,0.08);
    }
"""

FORM_INPUT_STYLE = """
    QLineEdit {
        background-color: rgba(255,255,255,0.035);
        color: #F3F8FF;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 10px;
        padding: 8px 12px;
        font: 10.5pt 'Segoe UI';
    }
    QLineEdit:focus {
        border: 1px solid rgba(25,212,255,0.55);
        background-color: rgba(25,212,255,0.05);
    }
"""

FORM_LABEL_STYLE = """
    QLabel {
        color: #DCE8F5;
        font: 10.5pt 'Segoe UI';
        border: none;
        background: transparent;
    }
"""

FORM_CLOSE_STYLE = """
    QPushButton {
        color: white;
        background-color: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 16px;
        font: 11pt 'Segoe UI';
    }
    QPushButton:hover {
        background-color: rgba(201,73,97,0.18);
        border: 1px solid rgba(201,73,97,0.45);
    }
"""

FORM_SAVE_STYLE = """
    QPushButton {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #19D4FF,
            stop:1 #4F8FFF
        );
        color: #04111C;
        border-radius: 20px;
        font-weight: bold;
        border: none;
    }
    QPushButton:hover {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #2CE0FF,
            stop:1 #67A0FF
        );
    }
"""


class DriverDetailsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(430, 300)

        data = load_json(driver_data_file(), {
            "name": "",
            "mobile": "",
            "age": ""
        })

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(FORM_CARD_STYLE)
        outer.addWidget(card)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(35)
        glow.setOffset(0, 0)
        glow.setColor(QColor(24, 210, 255, 60))
        card.setGraphicsEffect(glow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        top = QHBoxLayout()
        title = QLabel("Driver Details")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color:#19D4FF; border:none; background:transparent;")

        close_btn = QPushButton(chr(0x2715))
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(FORM_CLOSE_STYLE)
        close_btn.clicked.connect(self.close)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(close_btn)

        info = QLabel("Enter driver information for alert and profile usage.")
        info.setStyleSheet("""
            QLabel {
                color:#DCE8F5;
                font: 10pt 'Segoe UI';
                border:none;
                background:transparent;
            }
        """)

        form = QFormLayout()
        form.setSpacing(12)

        self.name_input = QLineEdit(data.get("name", ""))
        self.mobile_input = QLineEdit(data.get("mobile", ""))
        self.age_input = QLineEdit(data.get("age", ""))

        self.name_input.setStyleSheet(FORM_INPUT_STYLE)
        self.mobile_input.setStyleSheet(FORM_INPUT_STYLE)
        self.age_input.setStyleSheet(FORM_INPUT_STYLE)

        name_lbl = QLabel("Driver Name")
        mobile_lbl = QLabel("Mobile")
        age_lbl = QLabel("Age")
        name_lbl.setStyleSheet(FORM_LABEL_STYLE)
        mobile_lbl.setStyleSheet(FORM_LABEL_STYLE)
        age_lbl.setStyleSheet(FORM_LABEL_STYLE)

        form.addRow(name_lbl, self.name_input)
        form.addRow(mobile_lbl, self.mobile_input)
        form.addRow(age_lbl, self.age_input)

        save_btn = QPushButton("Save Details")
        save_btn.setMinimumHeight(42)
        save_btn.setStyleSheet(FORM_SAVE_STYLE)
        save_btn.clicked.connect(self.save_details)

        layout.addLayout(top)
        layout.addWidget(info)
        layout.addLayout(form)
        layout.addStretch()
        layout.addWidget(save_btn)

        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(220)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)

    def showEvent(self, event):
        super().showEvent(event)
        self.fade_anim.start()

    def save_details(self):
        data = {
            "name": self.name_input.text().strip(),
            "mobile": self.mobile_input.text().strip(),
            "age": self.age_input.text().strip()
        }
        save_json(driver_data_file(), data)
        self.accept()

# =========================================================
# ---------------- WELCOME PAGE ---------------------------
# =========================================================

class WelcomePage(AnimatedGradientWidget):
    def __init__(self, stacked):
        super().__init__()
        self.dialog_overlay = DialogOverlay(self)
        self.dialog_overlay.setGeometry(0, 0, self.width(), self.height())
        self.dialog_overlay.lower()
        self.stacked = stacked
        self.setMinimumSize(1280, 720)
        
        
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 34, 32, 28)
        root.setSpacing(18)

        top_bar = QHBoxLayout()
        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)

        self.brand_phase = 0.0
        self.brand = QLabel("AI Drowsiness Detection")
        self.brand.setFont(QFont("Bahnschrift SemiBold", 22, QFont.Bold))
        self.brand.setStyleSheet("color: #8FEFFF; border:none; letter-spacing: 0.5px;")

        self.brand_glow = QGraphicsDropShadowEffect()
        self.brand_glow.setBlurRadius(30)
        self.brand_glow.setOffset(0, 0)
        self.brand_glow.setColor(QColor(24, 210, 255, 130))
        self.brand.setGraphicsEffect(self.brand_glow)

        sub_brand = QLabel("Real-Time Driver Monitoring System")
        sub_brand.setFont(QFont("Segoe UI", 10))
        sub_brand.setStyleSheet(f"color: {TEXT_SOFT}; border:none;")

        brand_col.addWidget(self.brand)
        brand_col.addWidget(sub_brand)

        nav = QHBoxLayout()
        nav.setSpacing(14)

        self.about_btn_top = nav_button("About")
        self.features_btn_top = nav_button("Features")
        self.system_btn_top = nav_button("System")
        self.launch_btn_top = nav_button("Launch")

        self.about_btn_top.clicked.connect(lambda: self.handle_nav(self.about_btn_top, self.show_about))
        self.features_btn_top.clicked.connect(lambda: self.handle_nav(self.features_btn_top, self.show_features))
        self.system_btn_top.clicked.connect(lambda: self.handle_nav(self.system_btn_top, self.show_system))
        self.launch_btn_top.clicked.connect(lambda: self.handle_nav(self.launch_btn_top, self.goto_loading))

        nav.addWidget(self.about_btn_top)
        nav.addWidget(self.features_btn_top)
        nav.addWidget(self.system_btn_top)
        nav.addWidget(self.launch_btn_top)

        top_bar.addLayout(brand_col)
        top_bar.addStretch()
        top_bar.addLayout(nav)

        root.addLayout(top_bar)

        body = QHBoxLayout()
        body.setSpacing(22)

        left = QVBoxLayout()
        left.setSpacing(14)

        hero = QLabel("Build intelligent driver safety systems\nwith premium real-time monitoring.")
        hero.setWordWrap(True)
        hero.setFont(QFont("Segoe UI", 25, QFont.Bold))
        hero.setStyleSheet(f"color: {TEXT_MAIN}; border:none;")

        desc = QLabel(
            "This application detects driver drowsiness using facial landmarks, eye aspect ratio, "
            "mouth aspect ratio, and head pose estimation. It provides live monitoring, alert triggering, "
            "and a professional operator workflow."
        )
        desc.setWordWrap(True)
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet(f"color: {TEXT_SOFT}; line-height: 4.5; border:none;")

        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)

        self.start_btn = pill_button("Start Detection", SUCCESS_1, SUCCESS_2, "#2AE0FF", "#72A6FF", "#04111C")
        self.overview_btn = pill_button("Project Overview", "#0B1628", "#0B1628", "#13233D", "#162B48", TEXT_MAIN)
        self.exit_btn = pill_button("Exit", DANGER_1, DANGER_2, "#A93A56", "#D45371", TEXT_MAIN)

        add_glow(self.start_btn, QColor(24, 210, 255, 95), 45)
        add_glow(self.exit_btn, QColor(201, 73, 97, 65), 35)

        self.start_btn.clicked.connect(self.goto_loading)
        self.overview_btn.clicked.connect(self.show_overview)
        self.exit_btn.clicked.connect(QApplication.quit)

        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.overview_btn)
        btn_row.addWidget(self.exit_btn)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(18)
        cards_row.addWidget(clean_info_card("Core Module", "OpenCV + MediaPipe"))
        cards_row.addWidget(clean_info_card("Detection Logic", "EAR • MAR • Head Pose"))
        cards_row.addWidget(clean_info_card("Deployment", "PySide6 + Integrated Camera"))

        extra_btn_row = QHBoxLayout()
        extra_btn_row.setSpacing(14)

        self.connect_camera_btn = animated_action_button(
            "Connect Camera",
            "#0E2A46",
            "#1E6FA8",
            "#174567",
            "#2994D1",
            QColor(41, 177, 255, 95),
            "#F4FAFF"
        )

        self.whatsapp_btn = animated_action_button(
            "WhatsApp Alert",
            "#0A3D2F",
            "#16A36D",
            "#105745",
            "#1BCB88",
            QColor(39, 223, 141, 95),
            "#F4FFF9"
        )

        self.driver_btn = animated_action_button(
            "Driver Details",
            "#3C234F",
            "#9B47C9",
            "#59306F",
            "#BB66EA",
            QColor(201, 108, 255, 92),
            "#FFF8FF"
        )

        self.connect_camera_btn.clicked.connect(self.open_camera_source)
        self.whatsapp_btn.clicked.connect(self.open_whatsapp_alert)
        self.driver_btn.clicked.connect(self.open_driver_details)

        extra_btn_row.addWidget(self.connect_camera_btn)
        extra_btn_row.addWidget(self.whatsapp_btn)
        extra_btn_row.addWidget(self.driver_btn)

        self.driver_btn.clicked.connect(self.open_driver_details)

        left.addSpacing(30)
        left.addWidget(hero)
        left.addWidget(desc)
        left.addStretch(1)
        left.addLayout(btn_row)
        left.addSpacing(8)
        left.addLayout(cards_row)
        left.addSpacing(24)
        left.addLayout(extra_btn_row)
        left.addStretch(1)

        right_card = card_frame(radius=30, border_alpha=22)
        right_card.setMinimumWidth(500)
        add_glow(right_card, QColor(24, 210, 255, 18), 34)

        rc_layout = QVBoxLayout(right_card)
        rc_layout.setContentsMargins(26, 24, 26, 24)
        rc_layout.setSpacing(14)

        project_name = QLabel("AI Driver Drowsiness Detection")
        project_name.setFont(QFont("Segoe UI", 19, QFont.Bold))
        project_name.setStyleSheet(f"color: {TEXT_MAIN}; border:none;")

        project_sub = QLabel("Final Year Project  |  Computer Vision  |  Safety Monitoring")
        project_sub.setFont(QFont("Segoe UI", 11))
        project_sub.setStyleSheet(f"color: {TEXT_SOFT}; border:none;")

        college_name = QLabel("Sri Raaja Raajan College of Engineering & Technology")
        college_name.setFont(QFont("Segoe UI", 12, QFont.Bold))
        college_name.setStyleSheet("""
            QLabel {
                color: #FFBE4F;
                border: none;
                background: transparent;
                letter-spacing: 0.3px;
            }
        """)
        self.college_glow = QGraphicsDropShadowEffect()
        self.college_glow.setBlurRadius(18)
        self.college_glow.setOffset(0, 0)
        self.college_glow.setColor(QColor(255, 190, 79, 110))
        college_name.setGraphicsEffect(self.college_glow)

        logo_holder = QFrame()
        logo_holder.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(18,30,52,0.98),
                    stop:0.5 rgba(12,22,39,0.98),
                    stop:1 rgba(10,18,30,0.98)
                );
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 26px;
            }
        """)
        logo_holder.setMinimumHeight(190)
        self.logo_holder_glow = QGraphicsDropShadowEffect()
        self.logo_holder_glow.setBlurRadius(24)
        self.logo_holder_glow.setOffset(0, 0)
        self.logo_holder_glow.setColor(QColor(24, 210, 255, 18))
        logo_holder.setGraphicsEffect(self.logo_holder_glow)

        logo_layout = QVBoxLayout(logo_holder)
        logo_layout.setAlignment(Qt.AlignCenter)
        logo_layout.setContentsMargins(24, 16, 24, 16)

        self.logo_orb = AnimatedLogoOrb()

        self.logo_ring_glow = QGraphicsDropShadowEffect()
        self.logo_ring_glow.setBlurRadius(28)
        self.logo_ring_glow.setOffset(0, 0)
        self.logo_ring_glow.setColor(QColor(43, 203, 255, 72))
        self.logo_orb.setGraphicsEffect(self.logo_ring_glow)

        logo_orb_layout = QVBoxLayout(self.logo_orb)
        logo_orb_layout.setContentsMargins(16, 16, 16, 16)
        logo_orb_layout.setAlignment(Qt.AlignCenter)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(146, 146)
        self.logo_label.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 73px;
                padding: 4px;
            }
        """)

        logo_path = resource_path("assets/logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(132, 132, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pix)

        self.logo_glow = QGraphicsDropShadowEffect()
        self.logo_glow.setBlurRadius(24)
        self.logo_glow.setOffset(0, 0)
        self.logo_glow.setColor(QColor(255, 197, 92, 46))
        self.logo_label.setGraphicsEffect(self.logo_glow)

        self.logo_glow_phase = 0.0

        logo_orb_layout.addWidget(self.logo_label)
        logo_layout.addWidget(self.logo_orb, alignment=Qt.AlignCenter)

        team_title = QLabel("Project Team")
        team_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        team_title.setStyleSheet("""
            QLabel {
                color: #23D9FF;
                border: none;
                background: transparent;
                letter-spacing: 1px;
            }
        """)

        team_box = QFrame()
        team_box.setFixedHeight(148)
        team_box.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(16,28,48,0.95),
                    stop:1 rgba(10,18,30,0.96)
                );
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 20px;
            }
        """)
        add_shadow(team_box, blur=34, y=8)
        team_layout = QVBoxLayout(team_box)
        team_layout.setContentsMargins(18, 12, 18, 12)
        team_layout.setSpacing(4)   

        team_members = [
            "Bharath R",
            "Subalakshmi J",
            "Ushamalini K",
            "Dharnesh Priyan J"
        ]

        for member in team_members:
            row = QLabel(f"•  {member}")
            row.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            row.setStyleSheet("""
                QLabel {
                    color: #F1F7FF;
                    border: none;
                    background: transparent;
                    padding: 4px 8px;
                }
                QLabel:hover {
                    color: #35DDFF;
                    background-color: rgba(24, 210, 255, 0.05);
                    border-radius: 8px;
                }
            """)
            team_layout.addWidget(row)

        rc_layout.addWidget(project_name)
        rc_layout.addWidget(project_sub)
        rc_layout.addWidget(college_name)
        rc_layout.addWidget(logo_holder)
        rc_layout.addWidget(team_title)
        rc_layout.addWidget(team_box)
        rc_layout.addStretch()

        body.addLayout(left, 3)
        body.addWidget(right_card, 2)
        root.addLayout(body)

        self.set_active_nav(self.about_btn_top)
        self.logo_timer = QTimer(self)
        self.logo_timer.timeout.connect(self.animate_logo_glow)
        self.logo_timer.start(45)

        self.brand_timer = QTimer(self)
        self.brand_timer.timeout.connect(self.animate_brand_title)
        self.brand_timer.start(55)
    
    def open_driver_details(self):
        self.open_blurred_form_dialog(DriverDetailsDialog)

    def open_whatsapp_alert(self):
        self.open_blurred_form_dialog(WhatsAppDialog)

    def open_camera_source(self):
        self.open_blurred_form_dialog(CameraSourceDialog)

    def open_blurred_form_dialog(self, dialog_class):
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(12)
        self.setGraphicsEffect(blur)

        self.dialog_overlay.show()
        self.dialog_overlay.raise_()

        dialog = dialog_class(self)
        dialog.move(
            self.width() // 2 - dialog.width() // 2,
            self.height() // 2 - dialog.height() // 2
        )
        dialog.exec()

        self.setGraphicsEffect(None)
        self.dialog_overlay.hide()

    def show_blurred_dialog(self, title, content):
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(12)
        self.setGraphicsEffect(blur)

        self.dialog_overlay.show()
        self.dialog_overlay.raise_()

        dialog = PremiumDialog(title, content, self)
        dialog.move(
            self.width() // 2 - dialog.width() // 2,
            self.height() // 2 - dialog.height() // 2
        )
        dialog.exec()

        self.setGraphicsEffect(None)
        self.dialog_overlay.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "dialog_overlay"):
            self.dialog_overlay.setGeometry(0, 0, self.width(), self.height())

    def animate_logo_glow(self):
        if not hasattr(self, "logo_glow"):
            return

        self.logo_glow_phase += 0.16

        outer_wave = (np.sin(self.logo_glow_phase) + 1.0) / 2.0
        inner_wave = (np.sin(self.logo_glow_phase + 1.15) + 1.0) / 2.0
        holder_wave = (np.sin(self.logo_glow_phase + 2.1) + 1.0) / 2.0

        self.logo_glow.setBlurRadius(18 + (inner_wave * 16))
        self.logo_glow.setColor(QColor(255, 194, 84, 34 + int(inner_wave * 40)))

        self.logo_ring_glow.setBlurRadius(24 + (outer_wave * 22))
        self.logo_ring_glow.setColor(QColor(34, 213, 255, 45 + int(outer_wave * 70)))

        self.logo_holder_glow.setBlurRadius(22 + (holder_wave * 14))
        self.logo_holder_glow.setColor(QColor(24, 210, 255, 10 + int(holder_wave * 24)))
        inner_border_alpha = 30 + int(inner_wave * 28)

        self.logo_orb.set_ring_angle(self.logo_glow_phase * 55.0)

        self.logo_label.setStyleSheet(f"""
            QLabel {{
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,{inner_border_alpha});
                border-radius: 73px;
                padding: 4px;
            }}
        """)

    def animate_brand_title(self):
        if not hasattr(self, "brand") or not hasattr(self, "brand_glow"):
            return

        self.brand_phase += 0.12
        cyan_wave = (np.sin(self.brand_phase) + 1.0) / 2.0
        gold_wave = (np.sin(self.brand_phase + 1.7) + 1.0) / 2.0

        red = int(105 + (cyan_wave * 80) + (gold_wave * 40))
        green = int(210 + (cyan_wave * 30) - (gold_wave * 20))
        blue = int(255 - (cyan_wave * 20) + (gold_wave * 10))
        text_color = QColor(
            min(255, max(0, red)),
            min(255, max(0, green)),
            min(255, max(0, blue))
        )

        glow_red = int(30 + (cyan_wave * 90) + (gold_wave * 70))
        glow_green = int(170 + (cyan_wave * 50))
        glow_blue = int(255 - (gold_wave * 35))

        self.brand.setStyleSheet(
            f"color: {text_color.name()}; border:none; letter-spacing: 0.5px;"
        )
        self.brand_glow.setBlurRadius(26 + (cyan_wave * 20))
        self.brand_glow.setColor(
            QColor(
                min(255, max(0, glow_red)),
                min(255, max(0, glow_green)),
                min(255, max(0, glow_blue)),
                95 + int(cyan_wave * 85)
            )
        )

    def handle_nav(self, button, action):
        self.set_active_nav(button)
        action()

    def show_premium_dialog(self, title, content):
        self.dialog_overlay.show()
        self.dialog_overlay.raise_()

        dialog = PremiumDialog(title, content, self)
        dialog.move(
            self.width() // 2 - dialog.width() // 2,
            self.height() // 2 - dialog.height() // 2
        )
        dialog.exec()

        self.dialog_overlay.hide()

    def set_active_nav(self, active_button):
        nav_buttons = [self.about_btn_top, self.features_btn_top, self.system_btn_top, self.launch_btn_top]
        for btn in nav_buttons:
            if btn == active_button:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        color: #04111C;
                        background: qlineargradient(
                            x1:0, y1:0, x2:1, y2:0,
                            stop:0 {ACCENT},
                            stop:0.55 #31E2FF,
                            stop:1 {ACCENT_2}
                        );
                        border: 1px solid rgba(255,255,255,0.12);
                        border-radius: 21px;
                        padding: 0 20px;
                        font: 700 10pt 'Segoe UI';
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {TEXT_MAIN};
                        background-color: rgba(255,255,255,0.02);
                        border: 1px solid rgba(24,210,255,0.28);
                        border-radius: 21px;
                        padding: 0 20px;
                        font: 600 10pt 'Segoe UI';
                    }}
                    QPushButton:hover {{
                        border: 1px solid {ACCENT};
                        background-color: rgba(24,210,255,0.10);
                    }}
                """)

    def show_overview(self):
        self.show_blurred_dialog(
            "Project Overview",
            "Technologies Used:\n\n"
            "- Python\n"
            "- PySide6\n"
            "- OpenCV\n"
            "- MediaPipe Face Mesh\n"
            "- NumPy\n"
            "- Playsound / Winsound\n"
            "- Threading\n\n"
            "Modules:\n"
            "- Premium Launcher UI\n"
            "- Loading Screen\n"
            "- Integrated Camera Detection\n"
            "- EAR / MAR Analysis\n"
            "- Head Pose Detection\n"
            "- Alert and Alarm System"
        )

    def show_about(self):
        self.show_blurred_dialog(
            "About Project",
            "AI Driver Drowsiness Detection System\n\n"
            "This project is developed as a final-year Computer Science application "
            "for real-time driver monitoring using computer vision. "
            "It detects drowsiness, yawning, and distraction using facial landmark analysis."
        )

    def show_features(self):
        self.show_blurred_dialog(
            "Features",
            "- Real-time drowsiness detection\n"
            "- Yawning detection\n"
            "- Head distraction detection\n"
            "- Attention score monitoring\n"
            "- Audio warning system\n"
            "- Premium PySide6 launcher\n"
            "- Fullscreen integrated camera page"
        )

    def show_system(self):
        self.show_blurred_dialog(
            "System Details",
            "Workflow:\n\n"
            "Camera -> Face Mesh -> EAR / MAR / Head Pose -> Decision Logic -> Alarm -> Live Monitoring\n\n"
            "The launcher and camera view are integrated inside the same PySide6 application."
        )

    def goto_loading(self):
        self.stacked.loading_page.start_loading()

class CameraSourceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(460, 260)

        data = load_json(camera_config_file(), {
            "camera_source": "0",
            "last_external_camera_source": ""
        })
        saved_source = data.get("camera_source", "0").strip()
        self.saved_external_source = data.get("last_external_camera_source", "").strip()
        is_laptop_camera = saved_source == "0"
        initial_external_source = saved_source if not is_laptop_camera else self.saved_external_source

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(FORM_CARD_STYLE)
        outer.addWidget(card)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(35)
        glow.setOffset(0, 0)
        glow.setColor(QColor(24, 210, 255, 60))
        card.setGraphicsEffect(glow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        top = QHBoxLayout()
        title = QLabel("Connect Camera")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color:#19D4FF; border:none; background:transparent;")

        close_btn = QPushButton(chr(0x2715))
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(FORM_CLOSE_STYLE)
        close_btn.clicked.connect(self.close)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(close_btn)

        info = QLabel("Choose the camera source. Use laptop camera or save an external camera URL.")
        info.setWordWrap(True)
        info.setStyleSheet("""
            QLabel {
                color:#DCE8F5;
                font: 10pt 'Segoe UI';
                border:none;
                background:transparent;
            }
        """)

        form = QFormLayout()
        form.setSpacing(12)

        option_style = """
            QRadioButton {
                color: #EAF4FF;
                font: 10.5pt 'Segoe UI';
                spacing: 10px;
                background: transparent;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 1px solid rgba(255,255,255,0.22);
                background-color: rgba(255,255,255,0.04);
            }
            QRadioButton::indicator:checked {
                border: 1px solid rgba(25,212,255,0.82);
                background-color: rgba(25,212,255,0.72);
            }
        """

        self.laptop_radio = QRadioButton("Laptop Camera")
        self.external_radio = QRadioButton("External Camera URL")
        self.laptop_radio.setStyleSheet(option_style)
        self.external_radio.setStyleSheet(option_style)
        self.laptop_radio.setChecked(is_laptop_camera)
        self.external_radio.setChecked(not is_laptop_camera)
        self.laptop_radio.toggled.connect(self.update_source_mode)
        self.external_radio.toggled.connect(self.update_source_mode)

        choice_box = QVBoxLayout()
        choice_box.setSpacing(10)
        choice_box.addWidget(self.laptop_radio)
        choice_box.addWidget(self.external_radio)

        choice_lbl = QLabel("Choose Option")
        choice_lbl.setStyleSheet(FORM_LABEL_STYLE)
        form.addRow(choice_lbl, choice_box)

        self.source_input = QLineEdit(initial_external_source)
        self.source_input.setStyleSheet(FORM_INPUT_STYLE)
        self.source_input.setPlaceholderText("http://192.168.1.5:8080/video")

        self.source_lbl = QLabel("External Camera URL")
        self.source_lbl.setStyleSheet(FORM_LABEL_STYLE)

        form.addRow(self.source_lbl, self.source_input)

        save_btn = QPushButton("Save Camera Source")
        save_btn.setMinimumHeight(42)
        save_btn.setStyleSheet(FORM_SAVE_STYLE)
        save_btn.clicked.connect(self.save_source)

        layout.addLayout(top)
        layout.addWidget(info)
        layout.addLayout(form)
        layout.addStretch()
        layout.addWidget(save_btn)

        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(220)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.update_source_mode()

    def showEvent(self, event):
        super().showEvent(event)
        self.fade_anim.start()

    def update_source_mode(self):
        use_external = self.external_radio.isChecked()
        self.source_lbl.setVisible(use_external)
        self.source_input.setVisible(use_external)
        if use_external and not self.source_input.text().strip() and self.saved_external_source:
            self.source_input.setText(self.saved_external_source)

    def save_source(self):
        if self.laptop_radio.isChecked():
            source_value = "0"
        else:
            source_value = self.source_input.text().strip()
            if not source_value:
                QMessageBox.warning(
                    self,
                    "Missing Camera URL",
                    "Enter the external camera URL before saving."
                )
                return
            self.saved_external_source = source_value

        save_json(camera_config_file(), {
            "camera_source": source_value,
            "last_external_camera_source": self.saved_external_source
        })
        self.accept()


class WhatsAppDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(430, 360)

        data = load_json(alert_config_file(), {
            "enabled": True,
            "owner_whatsapp": ""
        })

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(FORM_CARD_STYLE)
        outer.addWidget(card)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(35)
        glow.setOffset(0, 0)
        glow.setColor(QColor(24, 210, 255, 60))
        card.setGraphicsEffect(glow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        top = QHBoxLayout()
        title = QLabel("WhatsApp Alert")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color:#19D4FF; border:none; background:transparent;")

        close_btn = QPushButton(chr(0x2715))
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(FORM_CLOSE_STYLE)
        close_btn.clicked.connect(self.close)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(close_btn)

        info = QLabel("Enter the WhatsApp number for alert messages.")
        info.setWordWrap(True)
        info.setStyleSheet("""
            QLabel {
                color:#DCE8F5;
                font: 10pt 'Segoe UI';
                border:none;
                background:transparent;
            }
        """)

        form = QFormLayout()
        form.setSpacing(12)

        option_style = """
            QRadioButton {
                color: #EAF4FF;
                font: 10.5pt 'Segoe UI';
                spacing: 10px;
                background: transparent;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 1px solid rgba(255,255,255,0.22);
                background-color: rgba(255,255,255,0.04);
            }
            QRadioButton::indicator:checked {
                border: 1px solid rgba(25,212,255,0.82);
                background-color: rgba(25,212,255,0.72);
            }
        """

        self.whatsapp_on_radio = QRadioButton("On")
        self.whatsapp_off_radio = QRadioButton("Off")
        self.whatsapp_on_radio.setStyleSheet(option_style)
        self.whatsapp_off_radio.setStyleSheet(option_style)
        self.whatsapp_on_radio.setChecked(data.get("enabled", True))
        self.whatsapp_off_radio.setChecked(not data.get("enabled", True))
        self.whatsapp_on_radio.toggled.connect(self.update_alert_mode)
        self.whatsapp_off_radio.toggled.connect(self.update_alert_mode)

        mode_box = QHBoxLayout()
        mode_box.setSpacing(18)
        mode_box.addWidget(self.whatsapp_on_radio)
        mode_box.addWidget(self.whatsapp_off_radio)
        mode_box.addStretch()

        self.number_input = QLineEdit(data.get("owner_whatsapp", ""))
        self.number_input.setPlaceholderText("Example: 919876543210")
        self.number_input.setStyleSheet(FORM_INPUT_STYLE)

        mode_lbl = QLabel("WhatsApp Alert")
        mode_lbl.setStyleSheet(FORM_LABEL_STYLE)
        number_lbl = QLabel("WhatsApp Number")
        number_lbl.setStyleSheet(FORM_LABEL_STYLE)

        form.addRow(mode_lbl, mode_box)
        form.addRow(number_lbl, self.number_input)

        save_btn = QPushButton("Save Number")
        save_btn.setMinimumHeight(42)
        save_btn.setStyleSheet(FORM_SAVE_STYLE)
        save_btn.clicked.connect(self.save_number)

        layout.addLayout(top)
        layout.addWidget(info)
        layout.addLayout(form)
        layout.addStretch()
        layout.addWidget(save_btn)

        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(220)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.update_alert_mode()

    def showEvent(self, event):
        super().showEvent(event)
        self.fade_anim.start()

    def update_alert_mode(self):
        enabled = self.whatsapp_on_radio.isChecked()
        self.number_input.setEnabled(enabled)

    def save_number(self):
        alerts_enabled = self.whatsapp_on_radio.isChecked()
        cleaned_number = normalize_whatsapp_number(self.number_input.text().strip())

        if alerts_enabled and len(cleaned_number) < 10:
            QMessageBox.warning(
                self,
                "Invalid WhatsApp Number",
                "Enter the WhatsApp number with country code, for example: 919876543210"
            )
            return

        save_json(alert_config_file(), {
            "enabled": alerts_enabled,
            "owner_whatsapp": cleaned_number
        })
        self.accept()

# =========================================================
# ---------------- APP CONTAINER --------------------------
# =========================================================

class AppContainer(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Drowsiness Detection")

        icon_path = resource_path("assets/ds.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.welcome = WelcomePage(self)
        self.loading_page = LoadingPage(self)
        self.camera_page = CameraPage(self)

        self.addWidget(self.welcome)      # index 0
        self.addWidget(self.loading_page) # index 1
        self.addWidget(self.camera_page)  # index 2

        self.setCurrentIndex(0)

# =========================================================
# ---------------- RUN APP --------------------------------
# =========================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("AI Drowsiness Detection")

    window = AppContainer()
    window.showFullScreen()

    sys.exit(app.exec())
