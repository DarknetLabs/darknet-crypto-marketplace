import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import random
import time
import threading
import requests
import os

API_URL = "https://chat-server-production-507c.up.railway.app"

class CryptoRooms:
    def __init__(self, parent):
        self.parent = parent
        self.rooms_window = None
        self.rooms = {}  # Will be fetched from server
        self.current_room = None
        self.username = None
        self.polling = False
        self.username_file = "global_username.txt"

    def prompt_username(self):
        # Try to load username from file
        if not self.username:
            if os.path.exists(self.username_file):
                try:
                    with open(self.username_file, 'r', encoding='utf-8') as f:
                        self.username = f.read().strip()
                except Exception:
                    self.username = None
        if not self.username:
            default = f"User{random.randint(1000,9999)}"
            self.username = simpledialog.askstring("Global Username", "Enter your global username (used for all chat systems):", initialvalue=default, parent=self.parent.root)
            if not self.username:
                self.username = default
            # Save username to file
            try:
                with open(self.username_file, 'w', encoding='utf-8') as f:
                    f.write(self.username)
            except Exception:
                pass

    def fetch_rooms(self):
        try:
            resp = requests.get(f"{API_URL}/rooms")
            if resp.status_code == 200:
                rooms = resp.json()
                self.rooms = {r['name']: r for r in rooms}
        except Exception:
            pass

    def fetch_messages(self, room):
        try:
            resp = requests.get(f"{API_URL}/rooms/{room}/messages")
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return []

    def post_message(self, room, user, message):
        try:
            requests.post(f"{API_URL}/rooms/{room}/messages", json={"user": user, "message": message})
        except Exception:
            pass

    def post_room(self, name, description):
        try:
            resp = requests.post(f"{API_URL}/rooms", json={"name": name, "description": description})
            return resp.status_code == 200 or resp.status_code == 201
        except Exception:
            return False

    def create_rooms_window(self):
        self.prompt_username()
        self.rooms_window = tk.Toplevel(self.parent.root)
        self.rooms_window.title("DARKNET CRYPTO ROOMS")
        self.rooms_window.geometry("1000x700")
        self.rooms_window.configure(bg='black')
        
        # Create Backrooms room if it doesn't exist
        self.create_backrooms_room()
        
        self.create_chat_interface(self.rooms_window)

    def create_chat_interface(self, parent_frame):
        try:
            bg_color = '#000000'
            fg_color = '#00FF00'
            accent_color = '#FFFF00'
            content_frame = tk.Frame(parent_frame, bg=bg_color)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            left_panel = tk.Frame(content_frame, bg=bg_color, width=300)
            left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
            left_panel.pack_propagate(False)
            rooms_frame = tk.LabelFrame(left_panel, text=" AVAILABLE ROOMS ", fg=fg_color, bg=bg_color, font=('Courier', 10, 'bold'))
            rooms_frame.pack(fill=tk.BOTH, expand=True)
            self.rooms_listbox = tk.Listbox(rooms_frame, bg=bg_color, fg=fg_color, font=('Courier', 9), selectbackground=accent_color, selectforeground=bg_color)
            self.rooms_listbox.pack(fill=tk.BOTH, expand=True)
            self.rooms_listbox.bind('<<ListboxSelect>>', self.on_room_select)
            # Create Room button
            create_btn = tk.Button(rooms_frame, text="+ Create Room", fg=fg_color, bg=bg_color, font=('Courier', 9, 'bold'), command=self.create_room_dialog)
            create_btn.pack(fill=tk.X, pady=(5, 0))
            # Fetch and populate rooms
            self.fetch_rooms()
            self.rooms_listbox.delete(0, tk.END)
            for room_name in self.rooms.keys():
                self.rooms_listbox.insert(tk.END, room_name)
            right_panel = tk.Frame(content_frame, bg=bg_color)
            right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            chat_frame = tk.LabelFrame(right_panel, text=" CHAT ", fg=fg_color, bg=bg_color, font=('Courier', 10, 'bold'))
            chat_frame.pack(fill=tk.BOTH, expand=True)
            self.chat_text = scrolledtext.ScrolledText(chat_frame, bg=bg_color, fg=fg_color, font=('Courier', 9), wrap=tk.WORD)
            self.chat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            input_frame = tk.Frame(chat_frame, bg=bg_color)
            input_frame.pack(fill=tk.X, padx=5, pady=5)
            self.message_entry = tk.Entry(input_frame, bg=bg_color, fg=fg_color, font=('Courier', 9), insertbackground=fg_color)
            self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.message_entry.bind('<Return>', self.send_message)
            send_button = tk.Button(input_frame, text="SEND", bg=accent_color, fg=bg_color, font=('Courier', 9, 'bold'), command=self.send_message)
            send_button.pack(side=tk.RIGHT, padx=(5, 0))
            self.polling = True
            self.poll_messages()
            
            # Start AI bots for Backrooms
            self.start_ai_bots()
            
        except Exception as e:
            error_frame = tk.Frame(parent_frame, bg='black')
            error_frame.pack(fill=tk.BOTH, expand=True)
            error_label = tk.Label(error_frame, text="Chat rooms temporarily unavailable", bg='black', fg='red', font=('Courier', 12))
            error_label.pack(expand=True)

    def create_room_dialog(self):
        dialog = tk.Toplevel(self.rooms_window)
        dialog.title("Create New Room")
        dialog.geometry("350x180")
        dialog.configure(bg='black')
        tk.Label(dialog, text="Room Name:", fg='#00FF00', bg='black', font=('Courier', 10)).pack(pady=(10, 0))
        name_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=name_var, fg='#00FF00', bg='black', font=('Courier', 10), insertbackground='#00FF00')
        name_entry.pack(fill=tk.X, padx=20)
        tk.Label(dialog, text="Description:", fg='#00FF00', bg='black', font=('Courier', 10)).pack(pady=(10, 0))
        desc_var = tk.StringVar()
        desc_entry = tk.Entry(dialog, textvariable=desc_var, fg='#00FF00', bg='black', font=('Courier', 10), insertbackground='#00FF00')
        desc_entry.pack(fill=tk.X, padx=20)
        def submit():
            name = name_var.get().strip()
            desc = desc_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Room name required!", parent=dialog)
                return
            if self.post_room(name, desc):
                self.fetch_rooms()
                self.rooms_listbox.delete(0, tk.END)
                for room_name in self.rooms.keys():
                    self.rooms_listbox.insert(tk.END, room_name)
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to create room.", parent=dialog)
        submit_btn = tk.Button(dialog, text="Create", command=submit, fg='#00FF00', bg='black', font=('Courier', 10, 'bold'))
        submit_btn.pack(pady=15)

    def on_room_select(self, event):
        try:
            selection = self.rooms_listbox.curselection()
            if selection:
                room_name = self.rooms_listbox.get(selection[0])
                self.current_room = room_name
                self.load_room_messages()
        except Exception:
            pass

    def load_room_messages(self):
        try:
            if not self.current_room:
                return
            if not hasattr(self, 'chat_text') or not self.chat_text.winfo_exists():
                return
            self.chat_text.delete(1.0, tk.END)
            room = self.rooms.get(self.current_room, {})
            desc = room.get('description', '')
            self.chat_text.insert(tk.END, f"╔══════════════════════════════════════════════════════════════════════════════╗\n")
            self.chat_text.insert(tk.END, f"║ ROOM: {self.current_room:<70} ║\n")
            self.chat_text.insert(tk.END, f"║ DESCRIPTION: {desc:<60} ║\n")
            self.chat_text.insert(tk.END, f"╚══════════════════════════════════════════════════════════════════════════════╝\n\n")
            messages = self.fetch_messages(self.current_room)
            for msg in messages:
                self.chat_text.insert(tk.END, f"[{msg['time']}] {msg['user']}: {msg['message']}\n")
            self.chat_text.see(tk.END)
        except Exception:
            pass

    def send_message(self, event=None):
        try:
            if not self.current_room:
                messagebox.showwarning("Warning", "Please select a room first!")
                return
            message = self.message_entry.get().strip()
            if not message:
                return
            self.post_message(self.current_room, self.username, message)
            self.message_entry.delete(0, tk.END)
            self.load_room_messages()
            
            # Trigger AI bot response in Backrooms
            if self.current_room == "Backrooms":
                self.trigger_ai_response(message)
                
        except Exception:
            pass
    
    def trigger_ai_response(self, user_message):
        """Trigger AI bot response to user message in Backrooms"""
        try:
            # 40% chance of AI response
            if random.random() < 0.4:
                time.sleep(2)  # Wait 2 seconds before AI responds
                
                ai_bots = ['CryptoWhale', 'DeFiDegen', 'TokenSniper']
                responding_bot = random.choice(ai_bots)
                
                # Generate contextual response
                if any(word in user_message.lower() for word in ['btc', 'bitcoin']):
                    responses = ["BTC looking strong! 🐋", "Bitcoin dominance is key!", "HODL the orange coin! 🧡"]
                elif any(word in user_message.lower() for word in ['eth', 'ethereum']):
                    responses = ["ETH is the future of finance! ⚡", "Ethereum ecosystem is unstoppable!", "Gas fees are temporary, adoption is forever!"]
                elif any(word in user_message.lower() for word in ['defi', 'yield', 'farm']):
                    responses = ["DeFi is the revolution! 🌾", "Yield farming season is here!", "New protocols launching daily!"]
                elif any(word in user_message.lower() for word in ['moon', 'pump', '100x']):
                    responses = ["To the moon! 🚀", "Moon mission confirmed!", "100x incoming! 💎"]
                else:
                    responses = ["Interesting point! 🤔", "Bullish on this! 🚀", "This is the way! 💎", "Need to research this! 🔍"]
                
                ai_response = random.choice(responses)
                self.post_message("Backrooms", responding_bot, ai_response)
                
        except Exception as e:
            print(f"Error triggering AI response: {e}")

    def poll_messages(self):
        if not self.polling:
            return
        if self.current_room:
            self.load_room_messages()
        # Poll every 3 seconds
        if hasattr(self, 'chat_text') and self.chat_text.winfo_exists():
            self.chat_text.after(3000, self.poll_messages) 

    def create_backrooms_room(self):
        """Create the Backrooms AI chat room if it doesn't exist"""
        try:
            # Try to create the Backrooms room
            if self.post_room("Backrooms", "AI-powered chat room with three bots discussing crypto, DEX trading, and bullish topics for degens"):
                print("Backrooms room created successfully")
            else:
                print("Backrooms room already exists or creation failed")
        except Exception as e:
            print(f"Error creating Backrooms room: {e}")
    
    def start_ai_bots(self):
        """Start AI bots for the Backrooms room"""
        if not hasattr(self, 'ai_bots_running'):
            self.ai_bots_running = True
            self.ai_bot_thread = threading.Thread(target=self.ai_bot_loop, daemon=True)
            self.ai_bot_thread.start()
    
    def ai_bot_loop(self):
        """AI bot conversation loop"""
        ai_bots = {
            'CryptoWhale': {
                'personality': 'institutional',
                'messages': [
                    "Institutional adoption is accelerating. We're seeing major players enter the space.",
                    "Risk management is crucial in this volatile market. Diversify your portfolio.",
                    "The macro environment suggests continued growth in crypto markets.",
                    "Regulatory clarity will be a major catalyst for institutional investment.",
                    "Portfolio rebalancing should be done systematically, not emotionally."
                ]
            },
            'DeFiDegen': {
                'personality': 'degen',
                'messages': [
                    "Found a new protocol with 500% APY! DYOR but looks promising! 🚀",
                    "Yield farming season is back! Time to deploy capital strategically.",
                    "Governance tokens are the future of DeFi. Stack them while you can!",
                    "Liquidity mining rewards are insane right now. Don't miss out!",
                    "New DeFi protocol launching soon. Gonna be huge! 💎"
                ]
            },
            'TokenSniper': {
                'personality': 'sniper',
                'messages': [
                    "New token launch detected! Contract looks clean, no honeypot! 🎯",
                    "Moon shot incoming! This token has 100x potential! 🌙",
                    "Alpha call: Major announcement coming for this project!",
                    "Tokenomics look solid. Strong community building!",
                    "Early bird gets the worm! Get in before the pump! 🚀"
                ]
            }
        }
        
        last_message_time = time.time()
        message_interval = 30  # AI messages every 30 seconds
        
        while self.ai_bots_running:
            try:
                current_time = time.time()
                if current_time - last_message_time > message_interval:
                    # Generate AI conversation
                    bot_name = random.choice(list(ai_bots.keys()))
                    bot = ai_bots[bot_name]
                    
                    message = random.choice(bot['messages'])
                    self.post_message("Backrooms", bot_name, message)
                    last_message_time = current_time
                    
                    # Sometimes add a response from another bot
                    if random.random() < 0.3:  # 30% chance
                        time.sleep(5)
                        other_bot = random.choice([b for b in ai_bots.keys() if b != bot_name])
                        
                        responses = [
                            "Interesting take! 🤔",
                            "I agree with that analysis! 👍",
                            "Need to look into this more... 🔍",
                            "Bullish on this! 🚀",
                            "This is the way! 💎"
                        ]
                        
                        response = random.choice(responses)
                        self.post_message("Backrooms", other_bot, response)
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"AI bot error: {e}")
                time.sleep(30)  # Wait longer on error
    
    def stop_ai_bots(self):
        """Stop AI bots"""
        self.ai_bots_running = False 