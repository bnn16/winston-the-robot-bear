import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional
import queue
import threading

logger = logging.getLogger(__name__)


class PersistentStatusWindow:
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.main_frame: Optional[ttk.Frame] = None
        self.status_label: Optional[ttk.Label] = None
        self.text_widget: Optional[tk.Text] = None
        self.animation_counter = 0
        self.update_queue = queue.Queue()
        self.current_state = "waiting"
        self._animation_id = None
        self.recording_trigger = threading.Event()
        self.recording_stop = threading.Event()
        self.is_recording = False
        self.voice_assistant_callback = None
        
    def create_window(self):
        self.root = tk.Tk()
        self.root.title("Winston the Robot Bear 🐻")
        self.root.geometry("800x600")
        
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
        
        self.root.attributes('-topmost', True)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.root.bind('<Return>', self._on_enter_pressed)
        self.root.focus_set()
        
        self.root.configure(bg='#1e1e1e')
        
        self.main_frame = tk.Frame(self.root, bg='#1e1e1e', padx=30, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(
            self.main_frame,
            text="🐻 Winston the Robot Bear",
            font=("Helvetica", 28, "bold"),
            fg='#ffffff',
            bg='#1e1e1e'
        )
        title_label.pack(pady=(0, 25))
        
        self.status_label = tk.Label(
            self.main_frame,
            text="⌨️ Press ENTER to record...",
            font=("Helvetica", 18),
            fg='#00ff88',
            bg='#1e1e1e'
        )
        self.status_label.pack(pady=(0, 25))
        
        text_container = tk.Frame(
            self.main_frame, 
            bg='#2d2d2d',
            highlightbackground='#444444',
            highlightthickness=2
        )
        text_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_widget = tk.Text(
            text_container,
            wrap=tk.WORD,
            font=("Consolas", 14),
            padx=20,
            pady=20,
            background="#2d2d2d",
            foreground="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            highlightthickness=0,
            selectbackground="#4a4a4a",
            selectforeground="#ffffff"
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(
            text_container,
            command=self.text_widget.yview,
            bg='#2d2d2d',
            activebackground='#4a4a4a',
            troughcolor='#1e1e1e'
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=scrollbar.set)
        
        self.text_widget.config(state=tk.DISABLED)
        
        self._check_updates()
        
    def _on_closing(self):
        self.root.iconify()
        
    def _on_enter_pressed(self, event):
        """Handle Enter key press to start/stop recording."""
        if self.current_state == "waiting":
            self.recording_trigger.set()
        elif self.is_recording:
            self.recording_stop.set()
            logger.info("Enter pressed - stopping recording")
        
    def _check_updates(self):
        try:
            while True:
                update = self.update_queue.get_nowait()
                method = update.get("method")
                
                if method == "set_waiting":
                    self._set_waiting_state()
                elif method == "set_command_detected":
                    self._set_command_detected_state(update.get("text", ""))
                elif method == "set_recording":
                    self._set_recording_state()
                elif method == "set_thinking":
                    self._set_thinking_state()
                elif method == "set_response":
                    self._set_response_state(update.get("text", ""))
                elif method == "set_speaking":
                    self._set_speaking_state()
                    
        except queue.Empty:
            pass
            
        self.root.after(50, self._check_updates)
        
    def _set_waiting_state(self):
        self.current_state = "waiting"
        self.is_recording = False
        self.status_label.config(text="⌨️ Press ENTER to record...", fg='#00ff88')
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", "Press ENTER in this window to start recording your command! 🎤\n\nMake sure this window is focused and press ENTER when ready.")
        self.text_widget.config(state=tk.DISABLED)
        self._stop_animation()
        
    def _set_command_detected_state(self, command_text: str):
        self.current_state = "command_detected"
        self.status_label.config(text="🎤 Command detected:", fg='#00ccff')
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", f"You said:\n\n\"{command_text}\"")
        self.text_widget.config(state=tk.DISABLED)
        
    def _set_recording_state(self):
        self.current_state = "recording"
        self.is_recording = True
        self.status_label.config(text="🔴 Recording... Press ENTER to stop", fg='#ff0000')
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", "🔴 Recording in progress...\n\nSpeak your command now!\n\nPress ENTER again to stop recording.")
        self.text_widget.config(state=tk.DISABLED)
        
    def _set_thinking_state(self):
        self.current_state = "thinking"
        self.status_label.config(text="🤔 Thinking...", fg='#ffaa00')
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.config(state=tk.DISABLED)
        self._start_thinking_animation()
        
    def _set_response_state(self, response_text: str):
        self.current_state = "response"
        self._stop_animation()
        self.status_label.config(text="💭 Here's what I think:", fg='#00aaff')
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", response_text)
        self.text_widget.config(state=tk.DISABLED)
        
    def _set_speaking_state(self):
        if self.current_state == "response":
            self.status_label.config(text="🔊 Speaking...", fg='#ff66cc')
            
    def _start_thinking_animation(self):
        self._animate_thinking()
        
    def _stop_animation(self):
        if self._animation_id:
            self.root.after_cancel(self._animation_id)
            self._animation_id = None
            
    def _animate_thinking(self):
        if self.current_state != "thinking":
            return
            
        dots = "." * (self.animation_counter % 4)
        self.status_label.config(text=f"🤔 Thinking{dots}", fg='#ffaa00')
        self.animation_counter += 1
        
        self._animation_id = self.root.after(500, self._animate_thinking)
        
    def show_waiting(self):
        self.update_queue.put({"method": "set_waiting"})
        
    def show_command_detected(self, command_text: str):
        self.update_queue.put({"method": "set_command_detected", "text": command_text})
        
    def show_recording(self):
        self.update_queue.put({"method": "set_recording"})
        
    def show_thinking(self):
        self.update_queue.put({"method": "set_thinking"})
        
    def show_response(self, response_text: str):
        self.update_queue.put({"method": "set_response", "text": response_text})
        
    def show_speaking(self):
        self.update_queue.put({"method": "set_speaking"})
        
    def wait_for_recording_trigger(self):
        """Wait for the recording trigger to be set, then clear it."""
        self.recording_trigger.wait()
        self.recording_trigger.clear()
        
    def wait_for_recording_stop(self, timeout=None):
        """Wait for the recording stop trigger."""
        return self.recording_stop.wait(timeout)
        
    def clear_recording_stop(self):
        """Clear the recording stop event."""
        self.recording_stop.clear()
        
    def run(self):
        self.root.mainloop()


_window_instance: Optional[PersistentStatusWindow] = None


def initialize_window():
    global _window_instance
    _window_instance = PersistentStatusWindow()
    _window_instance.create_window()
    return _window_instance


def get_window() -> Optional[PersistentStatusWindow]:
    return _window_instance


def show_waiting():
    if _window_instance:
        _window_instance.show_waiting()


def show_command_detected(command_text: str):
    if _window_instance:
        _window_instance.show_command_detected(command_text)


def show_recording():
    """Show recording state."""
    if _window_instance:
        _window_instance.show_recording()


def show_thinking():
    if _window_instance:
        _window_instance.show_thinking()


def show_response(response_text: str):
    if _window_instance:
        _window_instance.show_response(response_text)


def show_speaking():
    if _window_instance:
        _window_instance.show_speaking()


def wait_for_recording_trigger():
    """Wait for the user to press Enter to start recording."""
    if _window_instance:
        _window_instance.wait_for_recording_trigger()


def wait_for_recording_stop(timeout=None):
    """Wait for the user to press Enter to stop recording."""
    if _window_instance:
        return _window_instance.wait_for_recording_stop(timeout)
    return False


def clear_recording_stop():
    """Clear the recording stop event."""
    if _window_instance:
        _window_instance.clear_recording_stop()


def close_popup():
    show_waiting()