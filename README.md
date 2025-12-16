# 🏎️ 3D Car Racing Game (OpenGL / PyOpenGL)

A **3D endless car racing game** built using **Python**, **PyOpenGL**, and **GLUT**.  
The player races through a curved track, avoids obstacles and opponent cars, survives multiple timed levels, and wins by completing **Level 5**.

---
## 📥 How to Run the Game

1. **Download all files**
2. **Unzip the downloaded folder**
3. **Keep everything in one folder**
4. **Open a terminal inside the extracted folder**
5. **Run the game using the command below:**

```bash
python race.py
```

## 🎮 Features

### 🚗 3D Car Models
- Player and opponent cars with detailed bodies and rotating 3D wheels

### 🛣️ Endless Curved Track
- Dynamic track curvature with lane-based driving

### 🏁 Multiple Levels (1–5)
- Increasing difficulty, speed, obstacles, and opponents

### 🚧 Obstacle System
- Randomly spawning roadblocks

### 🤖 Opponent AI Cars
- Lane-based movement with recycling for endless gameplay

### 💥 Crash & Game Over Logic
- Game ends after **5 crashes**

### 🌧️ Rain Effect
- Toggleable screen-space rain overlay

### 🎥 Camera Controls
- Adjustable third-person camera angle

### 📊 HUD / UI
- Displays level, score, speed, crashes, and timer

---

## 🕹️ Controls

### Movement
- **J** – Move to left lane  
- **L** – Move to right lane  

### Camera & Speed
- **← / →** – Rotate camera  
- **↑** – Increase speed  
- **↓** – Decrease speed  

### Game Controls
- **A** – Turn rain ON  
- **B** – Turn rain OFF  
- **C** – Continue to next level  
- **R** – Restart game  
- **Q** – Quit game  

---

## 🏁 Gameplay Rules

- The car moves forward automatically.
- Avoid:
  - Red obstacle blocks
  - Opponent cars
- Each collision increases your **crash count**.
- **Game Over** occurs after **5 crashes**.
- Levels are **time-based** with increasing duration.
- Difficulty increases with:
  - More obstacles
  - More opponents
  - Higher speed

### 🏆 Win Condition
- Complete **Level 5**

---

## 🧰 Requirements

- **Python 3.8+**
- **PyOpenGL**
- **PyOpenGL_accelerate** (recommended)

---

Restart the game at any time by pressing **R**.

---

## 🧠 Learning Objectives

This project demonstrates the following concepts:

- PyOpenGL rendering
- 3D transformations and camera control
- Collision detection
- Game state management
- Real-time animation using the GLUT idle loop

---

## 📜 License

Developed by **Ummay Maimona Chaman** with two teammates as part of the **CSE423 Lab Project**.

This project is open for **educational and personal use**.

Feel free to contact me for any improvements or suggestions.   :) 
