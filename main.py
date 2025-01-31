import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Optional
import json
import os
from zoneinfo import available_timezones
import webbrowser

class TimeZoneConverter:
    def __init__(self):
        self.load_favorites()
        self.all_timezones = sorted(list(available_timezones()))
        
        # Default time zones with cities
        self.time_zones = [
            {"city": "New York", "zone": "America/New_York"},
            {"city": "London", "zone": "Europe/London"},
            {"city": "Paris", "zone": "Europe/Paris"},
            {"city": "Tokyo", "zone": "Asia/Tokyo"},
            {"city": "Sydney", "zone": "Australia/Sydney"},
            {"city": "Dubai", "zone": "Asia/Dubai"},
            {"city": "Los Angeles", "zone": "America/Los_Angeles"},
            {"city": "Singapore", "zone": "Asia/Singapore"},
            {"city": "Hong Kong", "zone": "Asia/Hong_Kong"},
            {"city": "Berlin", "zone": "Europe/Berlin"}
        ]
        
        self.history: List[Dict] = []
        self.load_history()

    def load_favorites(self):
        try:
            with open('favorites.json', 'r') as f:
                self.favorites = json.load(f)
        except:
            self.favorites = []

    def save_favorites(self):
        with open('favorites.json', 'w') as f:
            json.dump(self.favorites, f)

    def load_history(self):
        try:
            with open('history.json', 'r') as f:
                self.history = json.load(f)
        except:
            self.history = []

    def save_history(self):
        with open('history.json', 'w') as f:
            json.dump(self.history, f)

    def convert_time(self, time_str: str, from_zone: str, to_zone: str) -> Optional[str]:
        try:
            # Parse the input time
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            
            # Set the source timezone
            source_tz = pytz.timezone(from_zone)
            dt = source_tz.localize(dt)
            
            # Convert to target timezone
            target_tz = pytz.timezone(to_zone)
            converted_time = dt.astimezone(target_tz)
            
            return converted_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            return None

    def get_current_time(self, timezone: str) -> str:
        tz = pytz.timezone(timezone)
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    def get_world_times(self) -> List[Dict]:
        zones = self.time_zones + [{"city": "Custom", "zone": tz} for tz in self.favorites]
        return [{
            "city": tz["city"],
            "timezone": tz["zone"],
            "time": self.get_current_time(tz["zone"]),
            "offset": datetime.now(pytz.timezone(tz["zone"])).strftime("%z")
        } for tz in zones]

    def add_to_history(self, from_zone: str, to_zone: str, from_time: str, to_time: str):
        self.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from_zone": from_zone,
            "to_zone": to_zone,
            "from_time": from_time,
            "to_time": to_time
        })
        self.save_history()

class ConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Zone Converter & World Clock")
        self.root.geometry("730x560")
        
        self.converter = TimeZoneConverter()
        
        # Configure style
        self.setup_styles()
        self.create_widgets()
        self.update_world_clocks()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure("Title.TLabel", font=('Arial', 14, 'bold'))
        style.configure("Clock.TLabel", font=('Arial', 12))
        style.configure("Bold.TButton", font=('Arial', 10, 'bold'))

    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Converter tab
        converter_tab = ttk.Frame(self.notebook)
        self.notebook.add(converter_tab, text='Converter')
        self.create_converter_widgets(converter_tab)

        # World Clock tab
        world_clock_tab = ttk.Frame(self.notebook)
        self.notebook.add(world_clock_tab, text='World Clocks')
        self.create_world_clock_widgets(world_clock_tab)

        # Settings tab
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text='Settings')
        self.create_settings_widgets(settings_tab)

    def create_converter_widgets(self, parent):
        # Converter frame
        converter_frame = ttk.LabelFrame(parent, text="Time Zone Converter", padding="10")
        converter_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # From timezone
        ttk.Label(converter_frame, text="From:", style="Title.TLabel").grid(row=0, column=0, padx=5, pady=5)
        self.from_zone = ttk.Combobox(converter_frame, 
            values=self.converter.all_timezones,
            width=30)
        self.from_zone.grid(row=0, column=1, padx=5, pady=5)
        self.from_zone.set(self.converter.time_zones[0]["zone"])

        # To timezone
        ttk.Label(converter_frame, text="To:", style="Title.TLabel").grid(row=0, column=2, padx=5, pady=5)
        self.to_zone = ttk.Combobox(converter_frame,
            values=self.converter.all_timezones,
            width=30)
        self.to_zone.grid(row=0, column=3, padx=5, pady=5)
        self.to_zone.set(self.converter.time_zones[1]["zone"])

        # Time entry with current time button
        time_frame = ttk.Frame(converter_frame)
        time_frame.grid(row=1, column=0, columnspan=4, pady=10)

        ttk.Label(time_frame, text="Time:", style="Title.TLabel").pack(side=tk.LEFT, padx=5)
        self.time_entry = ttk.Entry(time_frame, width=30)
        self.time_entry.pack(side=tk.LEFT, padx=5)
        self.time_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        ttk.Button(time_frame, text="Use Current Time", 
                  command=self.use_current_time).pack(side=tk.LEFT, padx=5)

        # Quick time adjustments
        adjust_frame = ttk.Frame(converter_frame)
        adjust_frame.grid(row=2, column=0, columnspan=4, pady=5)

        for hours in [-24, -12, -1, +1, +12, +24]:
            ttk.Button(adjust_frame, 
                      text=f"{hours:+d}h",
                      command=lambda h=hours: self.adjust_time(h)).pack(side=tk.LEFT, padx=2)

        # Convert button
        convert_btn = ttk.Button(converter_frame, text="Convert", 
                               command=self.convert, style="Bold.TButton")
        convert_btn.grid(row=3, column=0, columnspan=4, pady=10)

        # Result
        self.result_var = tk.StringVar()
        result_label = ttk.Label(converter_frame, textvariable=self.result_var,
                               style="Clock.TLabel")
        result_label.grid(row=4, column=0, columnspan=4, pady=10)

        # History section
        history_frame = ttk.LabelFrame(converter_frame, text="Conversion History", padding="5")
        history_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # History display
        self.history_text = tk.Text(history_frame, height=10, width=80)
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", 
                                command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=scrollbar.set)
        
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # History buttons
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Button(history_btn_frame, text="Clear History", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_btn_frame, text="Export History", 
                  command=self.export_history).pack(side=tk.LEFT, padx=5)

    def create_world_clock_widgets(self, parent):
        world_frame = ttk.Frame(parent)
        world_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Search frame
        search_frame = ttk.Frame(world_frame)
        search_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_world_clocks)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=5)

        # World clocks
        self.world_clock_frame = ttk.Frame(world_frame)
        self.world_clock_frame.pack(fill='both', expand=True)

        self.world_clock_labels = {}
        self.create_world_clock_display()

    def create_settings_widgets(self, parent):
        settings_frame = ttk.LabelFrame(parent, text="Settings", padding="10")
        settings_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Theme selection
        theme_frame = ttk.Frame(settings_frame)
        theme_frame.pack(fill='x', pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=5)
        themes = ['clam', 'alt', 'default']
        self.theme_var = tk.StringVar(value='clam')
        theme_combo = ttk.Combobox(theme_frame, values=themes, 
                                 textvariable=self.theme_var, state='readonly')
        theme_combo.pack(side=tk.LEFT, padx=5)
        self.theme_var.trace('w', self.change_theme)

        # Favorite time zones
        ttk.Label(settings_frame, text="Favorite Time Zones:", 
                 style="Title.TLabel").pack(anchor='w', pady=10)
        
        favorite_frame = ttk.Frame(settings_frame)
        favorite_frame.pack(fill='x')
        
        self.favorite_zone = ttk.Combobox(favorite_frame, 
                                        values=self.converter.all_timezones)
        self.favorite_zone.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(favorite_frame, text="Add to Favorites", 
                  command=self.add_favorite).pack(side=tk.LEFT, padx=5)

        # Display favorites
        self.favorites_list = tk.Listbox(settings_frame, height=5)
        self.favorites_list.pack(fill='x', pady=5)
        self.update_favorites_list()

        ttk.Button(settings_frame, text="Remove Selected", 
                  command=self.remove_favorite).pack(pady=5)

    def create_world_clock_display(self):
        # Clear existing labels
        for widget in self.world_clock_frame.winfo_children():
            widget.destroy()

        # Create headers
        ttk.Label(self.world_clock_frame, text="City", 
                 style="Title.TLabel").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.world_clock_frame, text="Time", 
                 style="Title.TLabel").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.world_clock_frame, text="Offset", 
                 style="Title.TLabel").grid(row=0, column=2, padx=5, pady=5)

        # Create clock displays
        self.world_clock_labels = {}
        world_times = self.converter.get_world_times()
        
        for i, wt in enumerate(world_times, 1):
            if self.search_var.get().lower() in wt['city'].lower() or \
               self.search_var.get().lower() in wt['timezone'].lower():
                ttk.Label(self.world_clock_frame, 
                         text=f"{wt['city']} ({wt['timezone']})").grid(row=i, column=0, padx=5, pady=2)
                
                time_label = ttk.Label(self.world_clock_frame, text="")
                time_label.grid(row=i, column=1, padx=5, pady=2)
                
                offset_label = ttk.Label(self.world_clock_frame, text=wt['offset'])
                offset_label.grid(row=i, column=2, padx=5, pady=2)
                
                self.world_clock_labels[wt['timezone']] = time_label

    def filter_world_clocks(self, *args):
        self.create_world_clock_display()

    def update_world_clocks(self):
        world_times = self.converter.get_world_times()
        for wt in world_times:
            if wt["timezone"] in self.world_clock_labels:
                self.world_clock_labels[wt["timezone"]].config(text=wt["time"])
        
        # Update every second
        self.root.after(1000, self.update_world_clocks)

    def use_current_time(self):
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def adjust_time(self, hours):
        try:
            current_time = datetime.strptime(self.time_entry.get(), "%Y-%m-%d %H:%M:%S")
            adjusted_time = current_time + timedelta(hours=hours)
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, adjusted_time.strftime("%Y-%m-%d %H:%M:%S"))
        except ValueError:
            messagebox.showerror("Error", "Invalid time format!")

    def convert(self):
        try:
            time_str = self.time_entry.get()
            from_zone = self.from_zone.get()
            to_zone = self.to_zone.get()

            result = self.converter.convert_time(time_str, from_zone, to_zone)
            
            if result:
                result_text = f"{time_str} {from_zone} = {result} {to_zone}"
                self.result_var.set(result_text)
                
                # Add to history
                self.converter.add_to_history(from_zone, to_zone, time_str, result)
                self.update_history_display()
            else:
                messagebox.showerror("Error", "Invalid conversion!")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_history_display(self):
        self.history_text.delete(1.0, tk.END)
        for entry in reversed(self.converter.history):
            history_entry = (f"{entry['timestamp']} - Converted:\n"
                           f"  {entry['from_time']} {entry['from_zone']}\n"
                           f"  → {entry['to_time']} {entry['to_zone']}\n\n")
            self.history_text.insert(tk.END, history_entry)

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the history?"):
            self.converter.history = []
            self.converter.save_history()
            self.history_text.delete(1.0, tk.END)

    def export_history(self):
        try:
            with open('conversion_history.txt', 'w') as f:
                for entry in self.converter.history:
                    f.write(f"{entry['timestamp']} - Converted:\n")
                    f.write(f"  {entry['from_time']} {entry['from_zone']}\n")
                    f.write(f"  → {entry['to_time']} {entry['to_zone']}\n\n")
            messagebox.showinfo("Success", "History exported to conversion_history.txt")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export history: {str(e)}")

    def change_theme(self, *args):
        style = ttk.Style()
        style.theme_use(self.theme_var.get())

    def add_favorite(self):
        zone = self.favorite_zone.get()
        if zone and zone not in self.converter.favorites:
            self.converter.favorites.append(zone)
            self.converter.save_favorites()
            self.update_favorites_list()
            self.create_world_clock_display()

    def remove_favorite(self):
        selection = self.favorites_list.curselection()
        if selection:
            zone = self.converter.favorites[selection[0]]
            self.converter.favorites.remove(zone)
            self.converter.save_favorites()
            self.update_favorites_list()
            self.create_world_clock_display()

    def update_favorites_list(self):
        self.favorites_list.delete(0, tk.END)
        for zone in self.converter.favorites:
            self.favorites_list.insert(tk.END, zone)

def main():
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()