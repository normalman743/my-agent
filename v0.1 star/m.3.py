from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont, QFontMetrics, QRadialGradient, QLinearGradient, QPainterPath
import sys
import math
import random
from datetime import datetime

if sys.platform == "darwin":
    from ctypes import c_void_p
    import objc
    from AppKit import NSWindowCollectionBehaviorCanJoinAllSpaces

class UltraTechAIPet(QWidget):
    """超科技AI桌宠 - 炫酷增强版"""
    mood_changed = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.radius = 45
        self.current_mood = "normal"
        self.animation_time = 0
        self.energy_particles = []
        self.energy_waves = []
        self.orbit_particles = []
        self.data_streams = []
        self.arc_particles = []
        self.hex_grid = []
        self.scan_angle = 0
        self.energy_beams = []
        self.circuit_lines = []
        self.mouse_pos = QPoint(0, 0)
        self.eye_target = QPoint(0, 0)
        self.blink_timer = 0
        self.is_blinking = False
        self.float_offset = QPoint(0, 0)
        self.base_position = QPoint(0, 0)
        self.mouse_distance = 999
        self.intensity_boost = 0.01
        self.drag_position = QPoint()
        self.chat_bubble = None
        self.input_bubble = None
        self.init_ui()
        self.init_effects()
        self.set_on_all_spaces()

    def set_on_all_spaces(self):
        try:
            from ctypes import pythonapi, c_void_p, py_object
            pythonapi.PyCapsule_GetPointer.restype = c_void_p
            pythonapi.PyCapsule_GetPointer.argtypes = [py_object, c_void_p]
            ptr = pythonapi.PyCapsule_GetPointer(self.winId(), None)
            ns_win = objc.objc_object(c_void_p=ptr)
            ns_win.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
        except Exception as e:
            print("设置所有桌面可见失败：", e)

    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
            # 不要加 Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFixedSize(200, 200)
        self.move(300, 300)
        self.base_position = self.pos()
        self.setMouseTracking(True)
    def init_effects(self):
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.update_all_effects)
        self.render_timer.start(16)
        self.init_particles()
        self.init_tech_elements()
    def init_particles(self):
        for i in range(18):
            angle = i * (2 * math.pi / 18)
            particle = {
                'angle': angle,
                'distance': 70 + random.uniform(-8, 8),
                'speed': 0.02 + random.uniform(-0.008, 0.008),
                'size': random.uniform(2, 4),
                'alpha': random.uniform(0.6, 1.0),
                'pulse_phase': random.uniform(0, 2 * math.pi),
                'type': 'orbit'
            }
            particle['current_alpha'] = particle['alpha']
            self.orbit_particles.append(particle)
        for i in range(12):
            particle = {
                'x': random.uniform(-35, 35),
                'y': random.uniform(-35, 35),
                'size': random.uniform(1, 3),
                'alpha': random.uniform(0.4, 0.8),
                'pulse_phase': random.uniform(0, 2 * math.pi),
                'pulse_speed': random.uniform(0.05, 0.2),
                'type': 'energy'
            }
            particle['current_alpha'] = particle['alpha']
            self.energy_particles.append(particle)
        for i in range(25):
            stream = {
                'angle': random.uniform(0, 2 * math.pi),
                'distance': random.uniform(80, 150),
                'speed': random.uniform(0.5, 2.0),
                'size': random.uniform(0.5, 1.5),
                'alpha': random.uniform(0.3, 0.7),
                'trail_length': random.randint(3, 8),
                'trail_positions': [],
                'color_shift': random.uniform(0, 2 * math.pi)
            }
            self.data_streams.append(stream)
        for i in range(8):
            arc = {
                'start_angle': random.uniform(0, 2 * math.pi),
                'end_angle': random.uniform(0, 2 * math.pi),
                'start_distance': random.uniform(55, 75),
                'end_distance': random.uniform(55, 75),
                'life': 0,
                'max_life': random.uniform(0.3, 0.8),
                'intensity': random.uniform(0.5, 1.0)
            }
            self.arc_particles.append(arc)
    def init_tech_elements(self):
        for ring in range(3):
            for i in range(6 * max(1, ring)):
                if ring == 0:
                    hex_elem = {'x': 0, 'y': 0, 'size': 15, 'alpha': 0.8, 'pulse_phase': 0}
                else:
                    angle = i * (2 * math.pi / (6 * ring))
                    distance = ring * 30
                    hex_elem = {
                        'x': distance * math.cos(angle),
                        'y': distance * math.sin(angle),
                        'size': 10 + ring * 2,
                        'alpha': 0.6 - ring * 0.2,
                        'pulse_phase': random.uniform(0, 2 * math.pi)
                    }
                self.hex_grid.append(hex_elem)
        for i in range(6):
            beam = {
                'angle': i * (2 * math.pi / 6),
                'length': 60,
                'width': 3,
                'alpha': 0.7,
                'pulse_phase': random.uniform(0, 2 * math.pi),
                'rotation_speed': 0.01
            }
            self.energy_beams.append(beam)
        for i in range(12):
            circuit = {
                'start_angle': i * (2 * math.pi / 12),
                'length': random.uniform(20, 40),
                'segments': random.randint(3, 6),
                'alpha': random.uniform(0.4, 0.8),
                'pulse_speed': random.uniform(0.02, 0.08)
            }
            self.circuit_lines.append(circuit)
    def update_all_effects(self):
        self.animation_time += 0.016
        self.update_mouse_proximity()
        self.update_floating()
        self.update_particles()
        self.update_eye_tracking()
        self.update_blinking()
        self.update_energy_waves()
        self.update_tech_elements()
        self.update_data_streams()
        self.update_arc_particles()
        self.apply_floating()
        self.update()

    def update_mouse_proximity(self):
        try:
            global_mouse = QApplication.instance().desktop().cursor().pos()
            pet_center = self.geometry().center()
            dx = global_mouse.x() - pet_center.x()
            dy = global_mouse.y() - pet_center.y()
            self.mouse_distance = math.sqrt(dx*dx + dy*dy)
            if self.mouse_distance < 200:
                proximity_factor = 1 - (self.mouse_distance / 200)
                self.intensity_boost = 1.0 + proximity_factor * 0.5
            else:
                self.intensity_boost = 1.0
        except:
            self.intensity_boost = 1.0
    def update_floating(self):
        float_x = 3 * math.sin(self.animation_time * 0.8) * self.intensity_boost
        float_y = 2 * math.sin(self.animation_time * 1.2) * self.intensity_boost
        self.float_offset = QPoint(int(float_x), int(float_y))
    def update_particles(self):
        for particle in self.orbit_particles:
            particle['angle'] += particle['speed'] * self.intensity_boost
            particle['pulse_phase'] += 0.1 * self.intensity_boost
            pulse = 0.6 + 0.4 * math.sin(particle['pulse_phase'])
            particle['current_alpha'] = particle['alpha'] * pulse * self.intensity_boost
        for particle in self.energy_particles:
            particle['pulse_phase'] += particle['pulse_speed'] * self.intensity_boost
            pulse = 0.5 + 0.5 * math.sin(particle['pulse_phase'])
            particle['current_alpha'] = particle['alpha'] * pulse * self.intensity_boost
    def update_tech_elements(self):
        self.scan_angle += 0.03 * self.intensity_boost
        if self.scan_angle > 2 * math.pi:
            self.scan_angle = 0
        for hex_elem in self.hex_grid:
            hex_elem['pulse_phase'] += 0.05 * self.intensity_boost
        for beam in self.energy_beams:
            beam['angle'] += beam['rotation_speed'] * self.intensity_boost
            beam['pulse_phase'] += 0.08 * self.intensity_boost
    def update_data_streams(self):
        for stream in self.data_streams:
            stream['distance'] -= stream['speed'] * self.intensity_boost
            if stream['distance'] < 45:
                stream['distance'] = random.uniform(120, 180)
                stream['angle'] = random.uniform(0, 2 * math.pi)
                stream['trail_positions'] = []
            new_x = stream['distance'] * math.cos(stream['angle'])
            new_y = stream['distance'] * math.sin(stream['angle'])
            stream['trail_positions'].append((new_x, new_y))
            if len(stream['trail_positions']) > stream['trail_length']:
                stream['trail_positions'].pop(0)
    def update_arc_particles(self):
        for arc in self.arc_particles:
            arc['life'] += 0.016
            if arc['life'] > arc['max_life']:
                arc['life'] = 0
                arc['start_angle'] = random.uniform(0, 2 * math.pi)
                arc['end_angle'] = random.uniform(0, 2 * math.pi)
                arc['start_distance'] = random.uniform(50, 80)
                arc['end_distance'] = random.uniform(50, 80)
                arc['max_life'] = random.uniform(0.2, 0.6)
    def update_eye_tracking(self):
        try:
            global_mouse = QApplication.instance().desktop().cursor().pos()
            pet_center = self.geometry().center()
            dx = global_mouse.x() - pet_center.x()
            dy = global_mouse.y() - pet_center.y()
            distance = math.sqrt(dx*dx + dy*dy)
            eye_range = 8
            if distance > 0:
                factor = min(distance / 300, 1.0)
                target_x = (dx / distance) * eye_range * factor
                target_y = (dy / distance) * eye_range * factor
                target_x = max(-eye_range, min(eye_range, target_x))
                target_y = max(-eye_range, min(eye_range, target_y))
                self.eye_target = QPoint(int(target_x), int(target_y))
            else:
                self.eye_target = QPoint(0, 0)
        except:
            self.eye_target = QPoint(0, 0)
    def update_blinking(self):
        self.blink_timer += 0.016
        blink_interval = 3 - self.intensity_boost
        if self.blink_timer > max(1, blink_interval) and not self.is_blinking:
            self.is_blinking = True
            self.blink_timer = 0
        if self.is_blinking and self.blink_timer > 0.12:
            self.is_blinking = False
            self.blink_timer = 0
    def update_energy_waves(self):
        self.energy_waves = [wave for wave in self.energy_waves if wave['life'] < wave['max_life']]
        for wave in self.energy_waves:
            wave['life'] += 0.016
            progress = wave['life'] / wave['max_life']
            wave['radius'] = wave['max_radius'] * progress
            wave['alpha'] = int(255 * (1 - progress) * 0.8 * self.intensity_boost)
    def apply_floating(self):
        if self.drag_position.isNull():
            new_pos = self.base_position + self.float_offset
            if self.pos() != new_pos:
                self.move(new_pos)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        center_x = self.width() // 2
        center_y = self.height() // 2
        self.draw_ultra_outer_effects(painter, center_x, center_y)
        self.draw_tech_elements(painter, center_x, center_y)
        self.draw_data_streams(painter, center_x, center_y)
        self.draw_enhanced_orbit_particles(painter, center_x, center_y)
        self.draw_arc_particles(painter, center_x, center_y)
        self.draw_ultra_core(painter, center_x, center_y)
        self.draw_inner_effects(painter, center_x, center_y)
        self.draw_enhanced_eyes(painter, center_x, center_y)
        self.draw_energy_waves(painter, center_x, center_y)
        self.draw_lens_flare(painter, center_x, center_y)
    def draw_ultra_outer_effects(self, painter, x, y):
        """绘制超炫外围光环 - 8层强光"""
        base_intensity = self.intensity_boost
        for i in range(8):
            ring_radius = self.radius + 15 + i * 8
            alpha = int(60 * (1 - i * 0.1) * base_intensity)
            color_shift = math.sin(self.animation_time * 2 + i * 0.5) * 0.3 + 0.7
            r = int(100 + 100 * color_shift)
            g = int(200 + 55 * color_shift)
            b = 255
            gradient = QRadialGradient(x, y, ring_radius)
            gradient.setColorAt(0.75, QColor(r//3, g//3, b//3, 0))
            gradient.setColorAt(0.9, QColor(r, g, b, alpha))
            gradient.setColorAt(0.95, QColor(255, 255, 255, int(alpha * 1.2)))
            gradient.setColorAt(1.0, QColor(r, g, b, 0))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - ring_radius, y - ring_radius,
                              ring_radius * 2, ring_radius * 2)
    def draw_tech_elements(self, painter, x, y):
        """绘制科技元素"""
        # 1. 雷达扫描线
        scan_length = 80 * self.intensity_boost
        scan_end_x = x + scan_length * math.cos(self.scan_angle)
        scan_end_y = y + scan_length * math.sin(self.scan_angle)
        scan_gradient = QLinearGradient(x, y, scan_end_x, scan_end_y)
        scan_gradient.setColorAt(0, QColor(0, 255, 255, int(200 * self.intensity_boost)))
        scan_gradient.setColorAt(0.7, QColor(100, 255, 255, int(150 * self.intensity_boost)))
        scan_gradient.setColorAt(1, QColor(0, 255, 255, 0))
        painter.setPen(QPen(QBrush(scan_gradient), 3))
        painter.drawLine(x, y, int(scan_end_x), int(scan_end_y))
        # 2. 六边形网格
        for hex_elem in self.hex_grid:
            hex_x = x + hex_elem['x']
            hex_y = y + hex_elem['y']
            pulse = 0.5 + 0.5 * math.sin(hex_elem['pulse_phase'])
            alpha = int(hex_elem['alpha'] * 255 * pulse * self.intensity_boost)
            self.draw_hexagon(painter, hex_x, hex_y, hex_elem['size'], QColor(0, 255, 200, alpha))
        # 3. 能量光束
        for beam in self.energy_beams:
            beam_start_x = x + 20 * math.cos(beam['angle'])
            beam_start_y = y + 20 * math.sin(beam['angle'])
            beam_end_x = x + (20 + beam['length']) * math.cos(beam['angle'])
            beam_end_y = y + (20 + beam['length']) * math.sin(beam['angle'])
            pulse = 0.7 + 0.3 * math.sin(beam['pulse_phase'])
            alpha = int(beam['alpha'] * 255 * pulse * self.intensity_boost)
            beam_gradient = QLinearGradient(beam_start_x, beam_start_y, beam_end_x, beam_end_y)
            beam_gradient.setColorAt(0, QColor(255, 255, 100, alpha))
            beam_gradient.setColorAt(0.5, QColor(100, 255, 255, alpha))
            beam_gradient.setColorAt(1, QColor(255, 255, 100, alpha//2))
            painter.setPen(QPen(QBrush(beam_gradient), beam['width']))
            painter.drawLine(int(beam_start_x), int(beam_start_y), int(beam_end_x), int(beam_end_y))

    def draw_hexagon(self, painter, x, y, size, color):
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.append(QPoint(int(px), int(py)))
        painter.setPen(QPen(color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(points)

    def draw_data_streams(self, painter, x, y):
        for stream in self.data_streams:
            if len(stream['trail_positions']) > 1:
                for i, (trail_x, trail_y) in enumerate(stream['trail_positions']):
                    trail_alpha = int(stream['alpha'] * 255 * (i / len(stream['trail_positions'])) * self.intensity_boost)
                    color_phase = stream['color_shift'] + self.animation_time
                    r = int(100 + 100 * math.sin(color_phase))
                    g = int(255)
                    b = int(200 + 55 * math.cos(color_phase))
                    painter.setBrush(QBrush(QColor(r, g, b, trail_alpha)))
                    painter.setPen(Qt.NoPen)
                    size = stream['size'] * (1 + i * 0.1)
                    painter.drawEllipse(int(x + trail_x - size), int(y + trail_y - size), int(size * 2), int(size * 2))

    def draw_enhanced_orbit_particles(self, painter, x, y):
        for particle in self.orbit_particles:
            px = x + particle['distance'] * math.cos(particle['angle'])
            py = y + particle['distance'] * math.sin(particle['angle'])
            alpha = int(255 * particle['current_alpha'])
            size = particle['size'] * self.intensity_boost
            core_gradient = QRadialGradient(px, py, size)
            core_gradient.setColorAt(0, QColor(255, 255, 255, alpha))
            core_gradient.setColorAt(0.3, QColor(200, 255, 255, alpha))
            core_gradient.setColorAt(0.7, QColor(100, 200, 255, alpha//2))
            core_gradient.setColorAt(1, QColor(50, 150, 255, 0))
            painter.setBrush(QBrush(core_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(px - size), int(py - size), int(size * 2), int(size * 2))
            if self.intensity_boost > 1.2:
                glow_size = size * 3
                glow_gradient = QRadialGradient(px, py, glow_size)
                glow_gradient.setColorAt(0, QColor(255, 255, 255, alpha//4))
                glow_gradient.setColorAt(0.5, QColor(150, 255, 255, alpha//6))
                glow_gradient.setColorAt(1, QColor(100, 200, 255, 0))
                painter.setBrush(QBrush(glow_gradient))
                painter.drawEllipse(int(px - glow_size), int(py - glow_size), int(glow_size * 2), int(glow_size * 2))

    def draw_arc_particles(self, painter, x, y):
        for arc in self.arc_particles:
            if arc['life'] < arc['max_life']:
                start_x = x + arc['start_distance'] * math.cos(arc['start_angle'])
                start_y = y + arc['start_distance'] * math.sin(arc['start_angle'])
                end_x = x + arc['end_distance'] * math.cos(arc['end_angle'])
                end_y = y + arc['end_distance'] * math.sin(arc['end_angle'])
                progress = arc['life'] / arc['max_life']
                alpha = int(255 * (1 - progress) * arc['intensity'] * self.intensity_boost)
                for i in range(3):
                    offset = random.uniform(-2, 2)
                    mid_x = (start_x + end_x) / 2 + offset
                    mid_y = (start_y + end_y) / 2 + offset
                    arc_color = QColor(100 + i*50, 200 + i*25, 255, alpha//(i+1))
                    painter.setPen(QPen(arc_color, 2))
                    path = QPainterPath()
                    path.moveTo(start_x, start_y)
                    path.quadTo(mid_x, mid_y, end_x, end_y)
                    painter.drawPath(path)

    def draw_ultra_core(self, painter, x, y):
        pulse = 0.9 + 0.1 * math.sin(self.animation_time * 4) * self.intensity_boost
        current_radius = self.radius * pulse
        for i in range(5):
            glow_radius = current_radius + 12 + i * 5
            glow_alpha = int(80 * (1 - i * 0.15) * pulse * self.intensity_boost)
            glow_gradient = QRadialGradient(x, y, glow_radius)
            if i == 0:
                glow_gradient.setColorAt(0.6, QColor(255, 255, 255, 0))
                glow_gradient.setColorAt(0.8, QColor(255, 255, 255, glow_alpha))
                glow_gradient.setColorAt(0.95, QColor(200, 255, 255, glow_alpha))
                glow_gradient.setColorAt(1.0, QColor(100, 200, 255, 0))
            else:
                glow_gradient.setColorAt(0.7, QColor(150, 220, 255, 0))
                glow_gradient.setColorAt(0.9, QColor(100, 200, 255, glow_alpha))
                glow_gradient.setColorAt(1.0, QColor(50, 150, 255, 0))
            painter.setBrush(QBrush(glow_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x - glow_radius), int(y - glow_radius), int(glow_radius * 2), int(glow_radius * 2))
        main_gradient = QRadialGradient(x - 15, y - 15, current_radius * 1.3)
        main_gradient.setColorAt(0, QColor(255, 255, 255, 220))
        main_gradient.setColorAt(0.1, QColor(240, 255, 255, 235))
        main_gradient.setColorAt(0.3, QColor(200, 240, 255, 245))
        main_gradient.setColorAt(0.6, QColor(150, 200, 255, 250))
        main_gradient.setColorAt(0.85, QColor(100, 160, 240, 255))
        main_gradient.setColorAt(1.0, QColor(50, 120, 200, 255))
        border_intensity = 0.9 + 0.4 * math.sin(self.animation_time * 6) * self.intensity_boost
        border_alpha = int(150 + 100 * border_intensity)
        border_color = QColor(200, 255, 255, border_alpha)
        painter.setBrush(QBrush(main_gradient))
        painter.setPen(QPen(border_color, 4))
        painter.drawEllipse(int(x - current_radius), int(y - current_radius), int(current_radius * 2), int(current_radius * 2))
        highlight1 = QRadialGradient(x - 18, y - 18, 40)
        highlight1.setColorAt(0, QColor(255, 255, 255, int(200 * self.intensity_boost)))
        highlight1.setColorAt(0.4, QColor(255, 255, 255, int(120 * self.intensity_boost)))
        highlight1.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(highlight1))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(x - 30, y - 30, 50, 45)
        highlight2 = QRadialGradient(x - 25, y - 25, 25)
        highlight2.setColorAt(0, QColor(240, 255, 255, int(150 * self.intensity_boost)))
        highlight2.setColorAt(1, QColor(200, 255, 255, 0))
        painter.setBrush(QBrush(highlight2))
        painter.drawEllipse(x - 35, y - 35, 30, 25)
        core_pulse = 0.6 + 0.5 * math.sin(self.animation_time * 8) * self.intensity_boost
        core_size = 8 * core_pulse
        core_gradient = QRadialGradient(x - 10, y - 10, core_size)
        core_gradient.setColorAt(0, QColor(255, 255, 255, int(255 * core_pulse)))
        core_gradient.setColorAt(0.5, QColor(240, 255, 255, int(200 * core_pulse)))
        core_gradient.setColorAt(1, QColor(200, 240, 255, int(150 * core_pulse)))
        painter.setBrush(QBrush(core_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(x - 10 - core_size//2), int(y - 10 - core_size//2), int(core_size), int(core_size))

    def draw_inner_effects(self, painter, x, y):
        for particle in self.energy_particles:
            px = x + particle['x']
            py = y + particle['y']
            dx = particle['x']
            dy = particle['y']
            if dx*dx + dy*dy <= (self.radius - 5) * (self.radius - 5):
                alpha = int(255 * particle['current_alpha'])
                size = particle['size'] * self.intensity_boost
                particle_gradient = QRadialGradient(px, py, size)
                particle_gradient.setColorAt(0, QColor(255, 255, 255, alpha))
                particle_gradient.setColorAt(0.5, QColor(220, 255, 255, alpha))
                particle_gradient.setColorAt(1, QColor(180, 220, 255, alpha//2))
                painter.setBrush(QBrush(particle_gradient))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(int(px - size), int(py - size), int(size * 2), int(size * 2))

    def draw_enhanced_eyes(self, painter, x, y):
        intensity_offset = self.intensity_boost * 3
        left_socket_x = x - 15 + self.eye_target.x() * intensity_offset
        left_socket_y = y - 8 + self.eye_target.y() * intensity_offset
        right_socket_x = x + 15 + self.eye_target.x() * intensity_offset
        right_socket_y = y - 8 + self.eye_target.y() * intensity_offset
        if self.is_blinking:
            glow_color = QColor(200, 255, 255, int(200 * self.intensity_boost))
            painter.setPen(QPen(glow_color, 4, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(int(left_socket_x - 6), int(left_socket_y), int(left_socket_x + 6), int(left_socket_y))
            painter.drawLine(int(right_socket_x - 6), int(right_socket_y), int(right_socket_x + 6), int(right_socket_y))
        else:
            eye_size = int(10 * self.intensity_boost)
            pupil_size = int(6 * self.intensity_boost)
            glow_size = eye_size + int(6 * self.intensity_boost)
            glow_gradient = QRadialGradient(left_socket_x, left_socket_y, glow_size)
            glow_gradient.setColorAt(0, QColor(200, 255, 255, int(100 * self.intensity_boost)))
            glow_gradient.setColorAt(1, QColor(150, 220, 255, 0))
            painter.setBrush(QBrush(glow_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(left_socket_x - glow_size), int(left_socket_y - glow_size), glow_size * 2, glow_size * 2)
            painter.drawEllipse(int(right_socket_x - glow_size), int(right_socket_y - glow_size), glow_size * 2, glow_size * 2)
            eye_gradient = QRadialGradient(left_socket_x, left_socket_y, eye_size)
            eye_gradient.setColorAt(0, QColor(255, 255, 255, 240))
            eye_gradient.setColorAt(1, QColor(250, 255, 255, 220))
            painter.setBrush(QBrush(eye_gradient))
            painter.setPen(QPen(QColor(220, 255, 255, int(150 * self.intensity_boost)), 2))
            painter.drawEllipse(int(left_socket_x - eye_size//2), int(left_socket_y - eye_size//2), eye_size, eye_size)
            painter.drawEllipse(int(right_socket_x - eye_size//2), int(right_socket_y - eye_size//2), eye_size, eye_size)
            pupil_gradient = QRadialGradient(0, 0, pupil_size)
            pupil_gradient.setColorAt(0, QColor(50, 100, 150, 240))
            pupil_gradient.setColorAt(0.7, QColor(80, 120, 180, 250))
            pupil_gradient.setColorAt(1, QColor(30, 80, 130, 255))
            painter.setBrush(QBrush(pupil_gradient))
            painter.setPen(Qt.NoPen)
            left_pupil_x = left_socket_x + self.eye_target.x()
            left_pupil_y = left_socket_y + self.eye_target.y()
            painter.drawEllipse(int(left_pupil_x - pupil_size//2), int(left_pupil_y - pupil_size//2), pupil_size, pupil_size)
            right_pupil_x = right_socket_x + self.eye_target.x()
            right_pupil_y = right_socket_y + self.eye_target.y()
            painter.drawEllipse(int(right_pupil_x - pupil_size//2), int(right_pupil_y - pupil_size//2), pupil_size, pupil_size)
            highlight_alpha = int(255 * self.intensity_boost)
            highlight_color = QColor(255, 255, 255, highlight_alpha)
            painter.setBrush(QBrush(highlight_color))
            highlight_size = int(4 * self.intensity_boost)
            painter.drawEllipse(int(left_pupil_x - highlight_size//2), int(left_pupil_y - highlight_size//2), highlight_size, highlight_size)
            painter.drawEllipse(int(right_pupil_x - highlight_size//2), int(right_pupil_y - highlight_size//2), highlight_size, highlight_size)
            if self.intensity_boost > 1.5:
                secondary_highlight = QColor(255, 255, 255, highlight_alpha//2)
                painter.setBrush(QBrush(secondary_highlight))
                sec_size = int(3 * self.intensity_boost)
                painter.drawEllipse(int(left_pupil_x + 2), int(left_pupil_y + 2), sec_size, sec_size)
                painter.drawEllipse(int(right_pupil_x + 2), int(right_pupil_y + 2), sec_size, sec_size)

    def draw_energy_waves(self, painter, x, y):
        for wave in self.energy_waves:
            if wave['alpha'] > 0:
                for i in range(3):
                    wave_alpha = wave['alpha'] // (i + 1)
                    wave_width = 3 + i
                    wave_color = QColor(100 + i*30, 200 + i*25, 255, wave_alpha)
                    painter.setPen(QPen(wave_color, wave_width))
                    painter.setBrush(Qt.NoBrush)
                    radius = wave['radius'] + i * 5
                    painter.drawEllipse(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))

    def draw_lens_flare(self, painter, x, y):
        if self.intensity_boost > 1.5:
            flare_size = int(30 * self.intensity_boost)
            flare_alpha = int(60 * (self.intensity_boost - 1))
            flare_gradient = QRadialGradient(x, y, flare_size)
            flare_gradient.setColorAt(0, QColor(255, 255, 255, flare_alpha))
            flare_gradient.setColorAt(0.3, QColor(200, 255, 255, flare_alpha//2))
            flare_gradient.setColorAt(1, QColor(150, 220, 255, 0))
            painter.setBrush(QBrush(flare_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - flare_size, y - flare_size, flare_size * 2, flare_size * 2)
            if self.intensity_boost > 2.0:
                flare_color = QColor(255, 255, 255, flare_alpha//2)
                painter.setPen(QPen(flare_color, 3))
                beam_length = int(40 * self.intensity_boost)
                painter.drawLine(x - beam_length, y, x + beam_length, y)
                painter.drawLine(x, y - beam_length, x, y + beam_length)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            # 多重能量爆发
            for i in range(3):
                wave = {
                    'radius': i * 10,
                    'max_radius': 100 + i * 20,
                    'life': i * 0.1,
                    'max_life': 1.2 + i * 0.3,
                    'alpha': 255 - i * 50
                }
                self.energy_waves.append(wave)
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.drag_position.isNull():
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            self.base_position = new_pos
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = QPoint()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.show_chat_bubble("科技问候！✨⚡")
            event.accept()

    def contextMenuEvent(self, event):
        # 右键弹出输入框
        self.show_input_bubble()
        event.accept()

    def show_input_bubble(self):
        if hasattr(self, 'input_bubble') and self.input_bubble:
            self.input_bubble.close()
        self.input_bubble = InputBubble(self)
        pet_pos = self.pos()
        bubble_x = pet_pos.x() + 100
        bubble_y = pet_pos.y() - 40
        self.input_bubble.move(bubble_x, bubble_y)
        self.input_bubble.show()

    def show_chat_bubble(self, message):
        # 简单气泡实现，可根据需要美化
        if self.chat_bubble:
            self.chat_bubble.close()
        self.chat_bubble = ChatBubble(message, self)
        pet_pos = self.pos()
        bubble_x = pet_pos.x() + 100
        bubble_y = pet_pos.y() - 80
        self.chat_bubble.move(bubble_x, bubble_y)
        self.chat_bubble.show()

class ChatBubble(QWidget):
    def __init__(self, message, parent_pet):
        super().__init__()
        self.message = message
        self.parent_pet = parent_pet
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 自动计算宽高
        font = QFont("Consolas", 12, QFont.Bold)
        metrics = QFontMetrics(font)
        # 限制最大宽度，自动换行
        max_width = 320
        text_rect = metrics.boundingRect(0, 0, max_width, 1000, Qt.TextWordWrap, self.message)
        bubble_width = min(max(text_rect.width() + 40, 180), max_width + 40)
        bubble_height = max(text_rect.height() + 28, 50)
        self.setFixedSize(bubble_width, bubble_height)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.setSingleShot(True)
        self.timer.start(2500)
        self.font = font

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(10, 10, -10, -10)
        painter.setBrush(QColor(40, 60, 80, 220))
        painter.setPen(QPen(QColor(150, 200, 255, 200), 2))
        painter.drawRoundedRect(rect, 15, 15)
        painter.setPen(QColor(220, 255, 255))
        painter.setFont(self.font)
        # 支持自动换行
        painter.drawText(rect.adjusted(10, 8, -10, -8), Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignVCenter, self.message)

class InputBubble(QWidget):
    def __init__(self, parent_pet):
        super().__init__()
        self.parent_pet = parent_pet
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(260, 54)
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("和我聊聊吧...")
        self.input.setGeometry(15, 12, 220, 30)
        self.input.setStyleSheet("""
            QLineEdit {
                background: rgba(40,60,80,220);
                border: 2px solid #96d9ff;
                border-radius: 12px;
                color: #e0ffff;
                font: bold 14px 'Consolas';
                padding-left: 8px;
                selection-background-color: #2ecfff;
            }
        """)
        self.input.returnPressed.connect(self.send_message)
        self.input.setFocus()

    def send_message(self):
        text = self.input.text().strip()
        if text:
            self.parent_pet.show_chat_bubble(f"你：{text}")
            QTimer.singleShot(400, lambda: self.parent_pet.show_chat_bubble(f"AI：{self.fake_ai_reply(text)}"))
            self.input.clear()

    def fake_ai_reply(self, user_text):
        if "天气" in user_text:
            return "今天天气晴朗，适合出门哦！🌞"
        elif "你好" in user_text:
            return "你好呀！很高兴见到你 😊"
        elif "时间" in user_text:
            return f"现在时间是 {datetime.now().strftime('%H:%M:%S')}"
        elif "你是谁" in user_text:
            return "我是你的超科技AI桌宠Star，随时为你服务！🤖"
        else:
            replies = [
                "我在这里，有什么可以帮你？",
                "收到！让我想想……",
                "这个问题有点难呢，但我会努力！",
                "你可以再详细描述一下吗？",
                "AI桌宠正在努力学习中~"
            ]
            return random.choice(replies)

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    ai_pet = UltraTechAIPet()
    ai_pet.show()
    print("🚀 超科技AI桌宠启动成功！")
    print("⚡ 主要特性:")
    print("  🔵 8层超亮外围光环（纯白+电蓝）")
    print("  🔷 六边形网格 + 雷达扫描线")
    print("  ⚡ 25个数据流粒子 + 拖尾效果")
    print("  🌟 18个轨道粒子 + 超强光晕")
    print("  ⚡ 电弧粒子系统")
    print("  🔆 能量光束 + 电路纹路")
    print("  💫 镜头光晕 + 十字光芒")
    print("  👁️ 增强眼神跟踪 + 发光瞳孔")
    print("  💬 科技感对话气泡（支持多轮对话）")
    print("🖱️ 交互：")
    print("  - 拖拽：移动位置")
    print("  - 单击：多重能量爆发")
    print("  - 双击：科技问候")
    print("  - 右键：AI对话（悬浮输入框，多轮气泡回复）")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()