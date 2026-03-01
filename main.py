import cv2
import time
import numpy as np
import winsound
import sys
import mediapipe as mp
import threading
import os
import pandas as pd
from playsound import playsound
from collections import deque

FONT = cv2.FONT_HERSHEY_DUPLEX
FONT_SCALE_TITLE = 0.9
FONT_SCALE_TEXT = 0.7
THICKNESS = 2
font = cv2.FONT_HERSHEY_DUPLEX
scale = 0.8
thickness = 2
line = cv2.LINE_AA
FONT_TITLE = cv2.FONT_HERSHEY_DUPLEX
FONT_BODY  = cv2.FONT_HERSHEY_COMPLEX

TITLE_SIZE = 0.9
BODY_SIZE  = 0.65
THICK      = 2

# =========================================================
# ---------------- WINDOW SETTINGS ------------------------
# =========================================================

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

width, height = 1280, 720
# camera exit button (use width, not w)
exit_cam_btn = [width - 80, height - 33, width - 20, height - 7]
exit_cam_clicked = False
window_name = "AI Drowsiness Detection"

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

logo = cv2.imread(resource_path("assets/logo.png"))
if logo is not None:
    logo = cv2.resize(logo, (180, 180))

start_clicked = False
exit_clicked = False
mouse_pos = (0, 0)

# 🔹 Smaller Buttons
start_btn = [width//2 - 90, 560, width//2 + 90, 600]
exit_btn  = [width//2 - 90, 620, width//2 + 90, 660]

# ---------- Rounded Button ----------
def draw_button(img, text, rect, base_color):
    x1, y1, x2, y2 = rect
    radius = 15

    hover = x1 < mouse_pos[0] < x2 and y1 < mouse_pos[1] < y2

    color = base_color
    if hover:
        color = (min(base_color[0]+40,255),
                 min(base_color[1]+40,255),
                 min(base_color[2]+40,255))

    overlay = img.copy()

    cv2.rectangle(overlay, (x1+radius, y1), (x2-radius, y2), color, -1)
    cv2.rectangle(overlay, (x1, y1+radius), (x2, y2-radius), color, -1)

    cv2.circle(overlay, (x1+radius, y1+radius), radius, color, -1)
    cv2.circle(overlay, (x2-radius, y1+radius), radius, color, -1)
    cv2.circle(overlay, (x1+radius, y2-radius), radius, color, -1)
    cv2.circle(overlay, (x2-radius, y2-radius), radius, color, -1)

    img[:] = overlay

    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
    text_x = x1 + (x2-x1)//2 - text_size[0]//2
    text_y = y1 + (y2-y1)//2 + text_size[1]//2

    cv2.putText(img, text, (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255,255,255), 2)

# ---------- Mouse ----------
def mouse_callback(event, x, y, flags, param):

    global start_clicked, exit_clicked, mouse_pos, exit_cam_btn, exit_cam_clicked

    mouse_pos = (x, y)

    if event == cv2.EVENT_LBUTTONDOWN:

        if start_btn[0] < x < start_btn[2] and start_btn[1] < y < start_btn[3]:
            start_clicked = True

        if exit_btn[0] < x < exit_btn[2] and exit_btn[1] < y < exit_btn[3]:
            exit_clicked = True

        # camera exit
        if exit_cam_btn[0] < x < exit_cam_btn[2] and exit_cam_btn[1] < y < exit_cam_btn[3]:
            exit_cam_clicked = True

cv2.setMouseCallback(window_name, mouse_callback)

# ================= INTRO LOOP =================
while True:
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Logo
    if logo is not None:
        frame[100:280, width//2 - 90:width//2 + 90] = logo

    # Title
    title = "AI BASED DROWSINESS DETECTION"
    text_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_DUPLEX, 1.3, 3)[0]
    text_x = width//2 - text_size[0]//2

    cv2.putText(frame,
                title,
                (text_x, 350),
                cv2.FONT_HERSHEY_DUPLEX,
                1.3, (0,255,255), 3)

    # Team Members
    members = ["BY Team members :                                          ", "Bharath R", "Subalakshmi J","Ushamalini K","Dharnesh Priyan J"]

    y = 400
    for m in members:
        text_size = cv2.getTextSize(m, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        text_x = width//2 - text_size[0]//2
        cv2.putText(frame,
                    m,
                    (text_x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255,255,255), 2)
        y += 30

    # Buttons
    draw_button(frame, "START", start_btn, (0, 150, 0))
    draw_button(frame, "EXIT", exit_btn, (0, 0, 150))

    cv2.imshow(window_name, frame)

    if exit_clicked:
        cv2.destroyAllWindows()
        sys.exit()

    if start_clicked:

    # -------- FADE OUT EFFECT --------
        for alpha in np.linspace(1, 0, 50):
            fade_frame = (frame * alpha).astype(np.uint8)
            cv2.imshow(window_name, fade_frame)
            cv2.waitKey(15)

        break

    if cv2.waitKey(30) & 0xFF == 27:
        break

# ================= LOADING SCREEN =================
for i in range(101):
    loading_frame = np.zeros((height, width, 3), dtype=np.uint8)

    text = "Starting AI Drowsiness System..."
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    text_x = width//2 - text_size[0]//2

    cv2.putText(loading_frame,
                text,
                (text_x, 320),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (255,255,255), 2)

    # Loading Bar Background
    cv2.rectangle(loading_frame,
                  (width//2 - 250, 380),
                  (width//2 + 250, 420),
                  (80,80,80), -1)

    # Progress
    cv2.rectangle(loading_frame,
                  (width//2 - 250, 380),
                  (width//2 - 250 + 5*i, 420),
                  (0,255,0), -1)

    percent = f"{i}%"
    cv2.putText(loading_frame,
                percent,
                (width//2 - 30, 460),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (255,255,255), 2)

    cv2.imshow(window_name, loading_frame)
    cv2.waitKey(20)



# =========================================================
# ---------------- CAMERA SECTION -------------------------
# =========================================================



# ================= RESOURCE PATH =================
def resource_path(relative):
    try:
        base = sys._MEIPASS
    except:
        base = os.path.abspath(".")
    return os.path.join(base, relative)

ALARM_FILE = resource_path("assets/alarm.wav")



# ================= MEDIAPIPE =================
mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ================= CAMERA =================
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

# ================= LANDMARK INDEX =================

LEFT_EYE = [33,160,158,133,153,144]
RIGHT_EYE = [362,385,387,263,373,380]

MOUTH = [13,14,78,308]

NOSE=1
CHIN=152
LEFT_FACE=234
RIGHT_FACE=454

# ================= THRESHOLDS =================

EAR_THRESH = 0.23
MAR_THRESH = 0.65
HEAD_THRESH = 20

FRAME_LIMIT = 20

# smoothing buffers
ear_buffer = deque(maxlen=10)
mar_buffer = deque(maxlen=10)

eye_closed_frames=0
head_frames=0

alarm=False

attention_score=100

log=[]

# ================= SOUND =================

def alarm_loop():
    global alarm
    while alarm:
        playsound(ALARM_FILE)

# ================= METRICS =================

def distance(a,b):
    return np.linalg.norm(a-b)

def compute_EAR(lm,eye):

    v1=distance(lm[eye[1]],lm[eye[5]])
    v2=distance(lm[eye[2]],lm[eye[4]])
    h=distance(lm[eye[0]],lm[eye[3]])

    return (v1+v2)/(2*h)

def compute_MAR(lm):

    v=distance(lm[MOUTH[0]],lm[MOUTH[1]])
    h=distance(lm[MOUTH[2]],lm[MOUTH[3]])

    return v/h

# ================= HEAD POSE =================

def head_pose(frame, lm):

    try:
        size = frame.shape

        image_pts = np.array([
            lm[NOSE],
            lm[CHIN],
            lm[LEFT_FACE],
            lm[RIGHT_FACE]
        ], dtype="double")

        if image_pts.shape[0] < 4:
            return 0, 0, 0

        model_pts = np.array([
            (0,0,0),
            (0,-330,-65),
            (-225,170,-135),
            (225,170,-135)
        ], dtype="double")

        focal = size[1]
        center = (size[1]/2, size[0]/2)

        cam_matrix = np.array([
            [focal,0,center[0]],
            [0,focal,center[1]],
            [0,0,1]
        ], dtype="double")

        dist_coeffs = np.zeros((4,1))

        success, rot_vec, trans_vec = cv2.solvePnP(
            model_pts,
            image_pts,
            cam_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return 0,0,0

        rmat,_ = cv2.Rodrigues(rot_vec)

        angles,_,_,_,_,_ = cv2.RQDecomp3x3(rmat)

        pitch,yaw,roll = angles

        return pitch,yaw,roll

    except:
        return 0,0,0

# ================= FPS =================

prev=time.time()

# ================= MAIN LOOP =================

# Camera window EXIT button
ear_avg = 0
mar_avg = 0
w = width
h = height
alert_active = False
blink_state = False
blink_timer = time.time()
 
while True:
    ret, frame = cap.read()
    if not ret:
        break

    current = time.time()
    time_diff = current - prev

    if time_diff > 0:
        fps = 1 / time_diff
    else:
        fps = 0
    prev = current
    
    frame=cv2.flip(frame,1)

    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    result=face_mesh.process(rgb)

    status="ACTIVE"
    color=(0,255,0)


    if result.multi_face_landmarks:

        face=result.multi_face_landmarks[0]

        h,w,_=frame.shape

        lm=np.array([
            (int(p.x*w),int(p.y*h))
            for p in face.landmark
        ])

        ear=(compute_EAR(lm,LEFT_EYE)+compute_EAR(lm,RIGHT_EYE))/2
        mar=compute_MAR(lm)

        ear_buffer.append(ear)
        mar_buffer.append(mar)

        ear_avg=np.mean(ear_buffer)
        mar_avg=np.mean(mar_buffer)

        pitch,yaw,roll=head_pose(frame,lm)

        # eye detection
        if ear_avg<EAR_THRESH:
            eye_closed_frames+=1
        else:
            eye_closed_frames=0

        # head detection
        if abs(yaw)>HEAD_THRESH:
            head_frames+=1
        else:
            head_frames=0

        # attention score model
        attention_score=100

        attention_score -= min(40,eye_closed_frames*2)
        attention_score -= min(30,head_frames*2)

        if mar_avg>MAR_THRESH:
            attention_score-=30

        attention_score=max(0,attention_score)

        # state machine
        if eye_closed_frames>FRAME_LIMIT:

            status="DROWSY"
            color=(0,0,255)

        elif mar_avg>MAR_THRESH:

            status="YAWNING"
            color=(0,165,255)

        elif head_frames>FRAME_LIMIT:

            status="DISTRACTED"
            color=(255,0,255)

        # alarm control
        if status!="ACTIVE":

            if not alarm:

                alarm=True

                threading.Thread(
                    target=alarm_loop,
                    daemon=True
                ).start()
        else:
            alarm=False

        # logging
        log.append({

            "time":time.strftime("%H:%M:%S"),

            "EAR":ear_avg,

            "MAR":mar_avg,

            "Yaw":yaw,

            "Attention":attention_score,

            "Status":status
        })

        # draw mesh points
        for p in LEFT_EYE+RIGHT_EYE:
            cv2.circle(frame,tuple(lm[p]),1,(255,255,0),-1)

    # ---- Top Bar ----
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 60), (15, 15, 15), -1)
    frame = cv2.addWeighted(overlay, 0.55, frame, 0.15, 0)

    # ================= HUD =================

   

    cv2.putText(frame,f"STATUS: {status}",
                (30,40),
                cv2.FONT_HERSHEY_DUPLEX,
                0.7,
                color,
                2)

    cv2.putText(frame,
                f"ATTENTION: {attention_score}%",
                (1080,85),
                cv2.FONT_HERSHEY_DUPLEX,
                0.7,
                (0,255,255),
                2)

    cv2.putText(frame,
                f"EAR: {ear_avg:.2f}",
                (30,85),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255,255,255),
                2)

    cv2.putText(frame,
                f"MAR: {mar_avg:.2f}",
                (30,115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255,255,255),
                2)

  
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q') or exit_cam_clicked:
        break







    # ================= PROFESSIONAL UI =================



    # ---- Centered Title (Reduced Size) ----
    title = "AI Drowsiness Monitoring System"
    text_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)[0]
    text_x = w//2 - text_size[0]//2

    cv2.putText(frame,
                title,
                (text_x, 38),
                cv2.FONT_HERSHEY_DUPLEX,
                0.65, (0, 220, 255), 2)

    # ---- LIVE Indicator ----
    cv2.circle(frame, (w - 70, 30), 8, (0, 0, 255), -1)
    cv2.putText(frame,
                "LIVE",
                (w - 50, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (255, 255, 255), 2)



    # ---- Bottom Bar ----
    overlay2 = frame.copy()
    cv2.rectangle(overlay2, (0, h-35), (w, h), (15, 15, 15), -1)
    frame = cv2.addWeighted(overlay2, 0.55, frame, 0.15, 0)

    """
    cv2.putText(frame,
                "Press Q to Exit",
                (20, h-15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45, (255, 255, 255), 2)
    """
    
    # ---- FPS ----
    cv2.putText(frame,
                f"FPS : {int(fps)}",
                (20, h - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48, (0, 255, 0), 2) 
   # exit button 
    x1, y1, x2, y2 = exit_cam_btn

    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,180), -1)

    cv2.putText(frame,
                "EXIT",
                (x1+15, y1+18),
                cv2.FONT_HERSHEY_DUPLEX,
                0.48,(255,255,255),2)

    # ---- Blinking Warning ----
    if alert_active:
        if time.time() - blink_timer > 0.5:
            blink_state = not blink_state
            blink_timer = time.time()

        if blink_state:
            cv2.putText(frame,
                        " !! DROWSINESS ALERT !!",
                        (w//2 - 220, h//2),
                        cv2.FONT_HERSHEY_DUPLEX,
                        1.0, (0, 0, 255), 3)

    # ---- Border Glow ----
    glow_color = (0, 255, 150)
    cv2.rectangle(frame, (0, 0), (w-1, h-1), glow_color, 2)
    for i in range(1, 4):
        cv2.rectangle(frame, (i, i), (w-i-1, h-i-1), glow_color, 1)

    cv2.imshow(window_name, frame)



    key = cv2.waitKey(1) & 0xFF

    if key == ord('q') or exit_cam_clicked:
        break



cap.release()

cv2.destroyAllWindows()