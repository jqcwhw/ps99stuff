#!/usr/bin/env python3
# Roblox Data Scraper (Python version)
# A comprehensive tool to extract information from Roblox games, users, and assets

import re
import os
import sys
import json
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
from datetime import datetime
import pyperclip  # pip install pyperclip

class RobloxScraper:
    def __init__(self, master):
        self.master = master
        master.title("Roblox Data Scraper")
        master.geometry("600x620")
        master.configure(bg="#333333")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#333333')
        self.style.configure('TButton', background='#555555', foreground='white')
        self.style.configure('TLabel', background='#333333', foreground='white')
        self.style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), background='#333333', foreground='white')
        
        # Main frame
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(self.main_frame, text="Roblox Data Scraper", style='Header.TLabel').pack(pady=(0, 10))
        
        # Input frame
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Roblox URL or ID:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var, width=50)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Scrape Info", command=self.scrape_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Results", command=self.save_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="From Clipboard", command=self.extract_from_clipboard).pack(side=tk.LEFT, padx=5)
        
        # Checkbox frame
        checkbox_frame = ttk.Frame(self.main_frame)
        checkbox_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Scrape types
        self.scrape_game = tk.BooleanVar(value=True)
        self.scrape_user = tk.BooleanVar(value=True)
        self.scrape_group = tk.BooleanVar(value=True)
        self.scrape_asset = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(checkbox_frame, text="Games", variable=self.scrape_game).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(checkbox_frame, text="Users", variable=self.scrape_user).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(checkbox_frame, text="Groups", variable=self.scrape_group).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(checkbox_frame, text="Assets", variable=self.scrape_asset).pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.main_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, width=70, height=20, 
                                                     bg="#444444", fg="#00FF00", insertbackground="white")
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_text.insert(tk.END, "Enter a Roblox URL or ID to extract information.\n")
        
        # Status bar
        self.status_var = tk.StringVar(value="Status: Ready")
        status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set focus to entry
        self.input_entry.focus_set()
        master.bind('<Return>', lambda event: self.scrape_info())

    def append_result(self, text):
        """Append text to results"""
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END)
        self.master.update_idletasks()
    
    def set_status(self, text):
        """Update status bar text"""
        self.status_var.set(f"Status: {text}")
        self.master.update_idletasks()
    
    def clear_results(self):
        """Clear the results text area"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Enter a Roblox URL or ID to extract information.\n")
        self.input_var.set("")
    
    def save_results(self):
        """Save results to a file"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"RobloxInfo_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.results_text.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Results saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")
    
    def extract_id_from_url(self, url):
        """Extract Roblox IDs from URL"""
        # Game ID
        game_match = re.search(r'games/(\d+)', url)
        if game_match:
            return game_match.group(1), "game"
        
        # User ID
        user_match = re.search(r'users/(\d+)|profile/(\d+)', url)
        if user_match:
            return user_match.group(1) if user_match.group(1) else user_match.group(2), "user"
        
        # Group ID
        group_match = re.search(r'groups/(\d+)', url)
        if group_match:
            return group_match.group(1), "group"
        
        # Asset ID
        asset_match = re.search(r'catalog/(\d+)|asset/(\d+)', url)
        if asset_match:
            return asset_match.group(1) if asset_match.group(1) else asset_match.group(2), "asset"
        
        # If it's just a number, return it without type
        if url.isdigit():
            return url, "unknown"
        
        return None, None
    
    def scrape_info(self):
        """Main function to scrape Roblox info"""
        input_text = self.input_var.get().strip()
        if not input_text:
            self.append_result("Error: Please enter a Roblox URL or ID")
            return
        
        self.append_result(f"Scraping: {input_text}")
        
        # Extract ID and determine type
        roblox_id, id_type = self.extract_id_from_url(input_text)
        
        if not roblox_id:
            self.append_result("Error: Could not extract a valid Roblox ID from input")
            return
        
        self.append_result(f"Extracted ID: {roblox_id}")
        
        # Try different ID types if unknown
        if id_type == "unknown":
            self.append_result("Testing as multiple ID types...")
            
            if self.scrape_game.get():
                self.scrape_game_info(roblox_id)
            
            if self.scrape_user.get():
                self.scrape_user_info(roblox_id)
            
            if self.scrape_group.get():
                self.scrape_group_info(roblox_id)
            
            if self.scrape_asset.get():
                self.scrape_asset_info(roblox_id)
        else:
            # Specific type known
            if id_type == "game" and self.scrape_game.get():
                self.scrape_game_info(roblox_id)
            elif id_type == "user" and self.scrape_user.get():
                self.scrape_user_info(roblox_id)
            elif id_type == "group" and self.scrape_group.get():
                self.scrape_group_info(roblox_id)
            elif id_type == "asset" and self.scrape_asset.get():
                self.scrape_asset_info(roblox_id)
            else:
                self.append_result(f"Scraping for {id_type} type is disabled in settings")
    
    def make_request(self, url, headers=None):
        """Make a request with error handling"""
        try:
            if headers:
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.set_status(f"Request failed with status code {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            self.set_status(f"Request error: {str(e)}")
            return None
        except json.JSONDecodeError:
            self.set_status("Received invalid JSON response")
            return None
    
    def scrape_game_info(self, game_id):
        """Scrape information about a Roblox game"""
        self.append_result("\nChecking as Game/Place ID: " + game_id)
        self.set_status("Fetching game universe information...")
        
        # Get universe ID
        universe_url = f"https://apis.roblox.com/universes/v1/places/{game_id}/universe"
        universe_data = self.make_request(universe_url)
        
        if not universe_data or "universeId" not in universe_data:
            self.append_result("✗ Not a valid Game/Place ID")
            return
        
        universe_id = universe_data["universeId"]
        self.append_result("✓ VALID GAME/PLACE ID")
        self.append_result(f"  Place ID: {game_id}")
        self.append_result(f"  Universe ID: {universe_id}")
        
        # Get game details
        self.set_status("Fetching game details...")
        game_url = f"https://games.roblox.com/v1/games?universeIds={universe_id}"
        game_data = self.make_request(game_url)
        
        if game_data and "data" in game_data and len(game_data["data"]) > 0:
            game_info = game_data["data"][0]
            
            # Game name & description
            game_name = game_info.get("name", "Unknown")
            self.append_result(f"  Game Name: {game_name}")
            
            description = game_info.get("description", "")
            if description and len(description) > 0:
                # Truncate long descriptions
                if len(description) > 200:
                    description = description[:197] + "..."
                self.append_result(f"  Description: {description}")
            
            # Root place
            root_place_id = game_info.get("rootPlaceId", "Unknown")
            if root_place_id != game_id:
                self.append_result(f"  Root Place ID: {root_place_id}")
                self.append_result("  This appears to be a private server or alternate place")
            
            # Creator info
            creator = game_info.get("creator", {})
            creator_id = creator.get("id", "Unknown")
            creator_name = creator.get("name", "Unknown")
            creator_type = creator.get("type", "Unknown")
            
            self.append_result(f"  Creator ID: {creator_id}")
            self.append_result(f"  Creator Name: {creator_name}")
            self.append_result(f"  Creator Type: {creator_type}")
            
            # Player stats
            playing = game_info.get("playing", 0)
            visits = game_info.get("visits", 0)
            self.append_result(f"  Current Players: {playing}")
            self.append_result(f"  Total Visits: {visits}")
            
            # Dates
            created = game_info.get("created", "")
            updated = game_info.get("updated", "")
            if created:
                created_date = created.split("T")[0]
                self.append_result(f"  Created: {created_date}")
            if updated:
                updated_date = updated.split("T")[0]
                self.append_result(f"  Last Updated: {updated_date}")
            
            # Access methods
            self.append_result("\n  Access URLs:")
            self.append_result(f"  - https://www.roblox.com/games/{game_id}")
            self.append_result(f"  - https://www.roblox.com/games/{root_place_id}")
            
            # Private servers
            create_vip = game_info.get("createVipServersAllowed", False)
            self.append_result(f"  Private Servers Allowed: {'Yes' if create_vip else 'No'}")
    
    def scrape_user_info(self, user_id):
        """Scrape information about a Roblox user"""
        self.append_result("\nChecking as User ID: " + user_id)
        self.set_status("Fetching user information...")
        
        # Get user info
        user_url = f"https://users.roblox.com/v1/users/{user_id}"
        user_data = self.make_request(user_url)
        
        if not user_data or "name" not in user_data:
            self.append_result("✗ Not a valid User ID")
            return
        
        self.append_result("✓ VALID USER ID")
        
        # Basic info
        username = user_data.get("name", "Unknown")
        display_name = user_data.get("displayName", "Unknown")
        
        self.append_result(f"  User ID: {user_id}")
        self.append_result(f"  Username: {username}")
        self.append_result(f"  Display Name: {display_name}")
        
        # Account info
        created = user_data.get("created", "")
        if created:
            created_date = created.split("T")[0]
            self.append_result(f"  Account Created: {created_date}")
        
        is_banned = user_data.get("isBanned", False)
        if is_banned:
            self.append_result("  Account Status: BANNED")
        
        # Description
        description = user_data.get("description", "")
        if description and len(description) > 0:
            # Truncate long descriptions
            if len(description) > 200:
                description = description[:197] + "..."
            self.append_result(f"  Description: {description}")
        
        # User URLs
        self.append_result("\n  Access URLs:")
        self.append_result(f"  - https://www.roblox.com/users/{user_id}/profile")
        
        # Get user's games
        self.set_status("Fetching user's games...")
        games_url = f"https://games.roblox.com/v2/users/{user_id}/games?sortOrder=Desc&limit=10"
        games_data = self.make_request(games_url)
        
        if games_data and "data" in games_data and len(games_data["data"]) > 0:
            self.append_result("\n  User's Games:")
            for i, game in enumerate(games_data["data"]):
                if i >= 5:  # Limit to 5 games
                    self.append_result(f"  ... and {len(games_data['data']) - 5} more")
                    break
                
                game_name = game.get("name", "Unknown")
                game_id = game.get("id", "Unknown")
                place_id = game.get("rootPlace", {}).get("id", "Unknown")
                
                self.append_result(f"  - {game_name} (ID: {game_id})")
    
    def scrape_group_info(self, group_id):
        """Scrape information about a Roblox group"""
        self.append_result("\nChecking as Group ID: " + group_id)
        self.set_status("Fetching group information...")
        
        # Get group info
        group_url = f"https://groups.roblox.com/v1/groups/{group_id}"
        group_data = self.make_request(group_url)
        
        if not group_data or "name" not in group_data:
            self.append_result("✗ Not a valid Group ID")
            return
        
        self.append_result("✓ VALID GROUP ID")
        
        # Basic info
        group_name = group_data.get("name", "Unknown")
        self.append_result(f"  Group ID: {group_id}")
        self.append_result(f"  Group Name: {group_name}")
        
        # Member count
        member_count = group_data.get("memberCount", 0)
        self.append_result(f"  Member Count: {member_count}")
        
        # Owner info
        owner = group_data.get("owner")
        if owner:
            owner_id = owner.get("userId", "Unknown")
            owner_name = owner.get("username", "Unknown")
            
            self.append_result(f"  Owner ID: {owner_id}")
            self.append_result(f"  Owner Name: {owner_name}")
        else:
            self.append_result("  Owner: None (Group may be owned by Roblox)")
        
        # Description
        description = group_data.get("description", "")
        if description and len(description) > 0:
            # Truncate long descriptions
            if len(description) > 200:
                description = description[:197] + "..."
            self.append_result(f"  Description: {description}")
        
        # Group URLs
        self.append_result("\n  Access URLs:")
        self.append_result(f"  - https://www.roblox.com/groups/{group_id}")
        
        # Get group's games
        self.set_status("Fetching group's games...")
        games_url = f"https://games.roblox.com/v2/groups/{group_id}/games?sortOrder=Desc&limit=10"
        games_data = self.make_request(games_url)
        
        if games_data and "data" in games_data and len(games_data["data"]) > 0:
            self.append_result("\n  Group's Games:")
            for i, game in enumerate(games_data["data"]):
                if i >= 5:  # Limit to 5 games
                    self.append_result(f"  ... and {len(games_data['data']) - 5} more")
                    break
                
                game_name = game.get("name", "Unknown")
                game_id = game.get("id", "Unknown")
                
                self.append_result(f"  - {game_name} (ID: {game_id})")
    
    def scrape_asset_info(self, asset_id):
        """Scrape information about a Roblox asset"""
        self.append_result("\nChecking as Asset ID: " + asset_id)
        self.set_status("Fetching asset information...")
        
        # Get asset info
        asset_url = f"https://economy.roblox.com/v2/assets/{asset_id}/details"
        asset_data = self.make_request(asset_url)
        
        if not asset_data or "Name" not in asset_data:
            self.append_result("✗ Not a valid Asset ID")
            return
        
        self.append_result("✓ VALID ASSET ID")
        
        # Basic info
        asset_name = asset_data.get("Name", "Unknown")
        self.append_result(f"  Asset ID: {asset_id}")
        self.append_result(f"  Asset Name: {asset_name}")
        
        # Asset type
        asset_type = asset_data.get("AssetTypeId", 0)
        asset_type_name = self.get_asset_type_name(asset_type)
        self.append_result(f"  Asset Type: {asset_type_name} (ID: {asset_type})")
        
        # Creator info
        creator_id = asset_data.get("CreatorTargetId", "Unknown")
        creator_type = asset_data.get("CreatorType", "Unknown")
        creator_name = asset_data.get("Creator", {}).get("Name", "Unknown")
        
        self.append_result(f"  Creator ID: {creator_id}")
        self.append_result(f"  Creator Name: {creator_name}")
        self.append_result(f"  Creator Type: {creator_type}")
        
        # Sales info
        is_for_sale = asset_data.get("IsForSale", False)
        is_limited = asset_data.get("IsLimited", False) or asset_data.get("IsLimitedUnique", False)
        price = asset_data.get("PriceInRobux", 0)
        
        self.append_result(f"  For Sale: {'Yes' if is_for_sale else 'No'}")
        if is_for_sale:
            self.append_result(f"  Price: {price} Robux")
        
        self.append_result(f"  Limited Item: {'Yes' if is_limited else 'No'}")
        
        # Dates
        created = asset_data.get("Created", "")
        updated = asset_data.get("Updated", "")
        
        if created:
            created_date = created.split("T")[0]
            self.append_result(f"  Created: {created_date}")
        
        if updated:
            updated_date = updated.split("T")[0]
            self.append_result(f"  Last Updated: {updated_date}")
        
        # Asset URLs
        self.append_result("\n  Access URLs:")
        self.append_result(f"  - https://www.roblox.com/catalog/{asset_id}")
        self.append_result(f"  - https://www.roblox.com/library/{asset_id}")
    
    def extract_from_clipboard(self):
        """Extract Roblox IDs from clipboard"""
        clipboard_text = pyperclip.paste()
        if not clipboard_text:
            self.append_result("Clipboard is empty")
            return
        
        self.append_result("\nExtracting Roblox IDs from clipboard...")
        
        # Find all game/place IDs
        game_ids = re.findall(r'(?:games|places|place\?id=)\/(\d+)', clipboard_text)
        # Find all user IDs
        user_ids = re.findall(r'(?:users|profile)\/(\d+)', clipboard_text)
        # Find all group IDs
        group_ids = re.findall(r'groups\/(\d+)', clipboard_text)
        # Find all asset IDs
        asset_ids = re.findall(r'(?:catalog|asset|library)\/(\d+)', clipboard_text)
        
        # Remove duplicates
        game_ids = list(set(game_ids))
        user_ids = list(set(user_ids))
        group_ids = list(set(group_ids))
        asset_ids = list(set(asset_ids))
        
        # Also try to find raw numeric IDs that might be Roblox IDs
        raw_ids = re.findall(r'(?<!\d)(\d{8,19})(?!\d)', clipboard_text)
        raw_ids = [id for id in raw_ids if id not in game_ids and id not in user_ids and 
                  id not in group_ids and id not in asset_ids]
        raw_ids = list(set(raw_ids))
        
        # Check if we found any IDs
        total_ids = len(game_ids) + len(user_ids) + len(group_ids) + len(asset_ids) + len(raw_ids)
        
        if total_ids == 0:
            self.append_result("No Roblox IDs found in clipboard")
            return
        
        self.append_result(f"Found {total_ids} potential Roblox IDs")
        
        # Process found IDs
        if game_ids and self.scrape_game.get():
            self.append_result(f"\nFound {len(game_ids)} Game/Place IDs:")
            for id in game_ids[:3]:  # Limit to 3 to avoid too many requests
                self.input_var.set(id)
                self.scrape_game_info(id)
            if len(game_ids) > 3:
                self.append_result(f"...and {len(game_ids) - 3} more game IDs")
        
        if user_ids and self.scrape_user.get():
            self.append_result(f"\nFound {len(user_ids)} User IDs:")
            for id in user_ids[:3]:  # Limit to 3
                self.input_var.set(id)
                self.scrape_user_info(id)
            if len(user_ids) > 3:
                self.append_result(f"...and {len(user_ids) - 3} more user IDs")
        
        if group_ids and self.scrape_group.get():
            self.append_result(f"\nFound {len(group_ids)} Group IDs:")
            for id in group_ids[:3]:  # Limit to 3
                self.input_var.set(id)
                self.scrape_group_info(id)
            if len(group_ids) > 3:
                self.append_result(f"...and {len(group_ids) - 3} more group IDs")
        
        if asset_ids and self.scrape_asset.get():
            self.append_result(f"\nFound {len(asset_ids)} Asset IDs:")
            for id in asset_ids[:3]:  # Limit to 3
                self.input_var.set(id)
                self.scrape_asset_info(id)
            if len(asset_ids) > 3:
                self.append_result(f"...and {len(asset_ids) - 3} more asset IDs")
        
        if raw_ids:
            self.append_result(f"\nFound {len(raw_ids)} raw numeric IDs that might be Roblox IDs")
            self.append_result("These will need to be manually checked:")
            for id in raw_ids[:10]:  # Limit to 10
                self.append_result(f"- {id}")
            if len(raw_ids) > 10:
                self.append_result(f"...and {len(raw_ids) - 10} more")
    
    def get_asset_type_name(self, type_id):
        """Convert asset type ID to name"""
        asset_types = {
            1: "Image",
            2: "T-Shirt",
            3: "Audio",
            4: "Mesh",
            5: "Lua",
            6: "HTML",
            7: "Text",
            8: "Hat",
            9: "Place",
            10: "Model",
            11: "Shirt",
            12: "Pants",
            13: "Decal",
            16: "Avatar",
            17: "Head",
            18: "Face",
            19: "Gear",
            21: "Badge",
            22: "Group Emblem",
            24: "Animation",
            25: "Arms",
            26: "Legs",
            27: "Torso",
            28: "Right Arm",
            29: "Left Arm",
            30: "Left Leg",
            31: "Right Leg",
            32: "Package",
            33: "YouTube Video",
            34: "Game Pass",
            35: "App",
            37: "Code",
            38: "Plugin",
            39: "SolidModel",
            40: "MeshPart",
            41: "Hair Accessory",
            42: "Face Accessory",
            43: "Neck Accessory",
            44: "Shoulder Accessory",
            45: "Front Accessory",
            46: "Back Accessory",
            47: "Waist Accessory",
            48: "Climb Animation",
            49: "Death Animation",
            50: "Fall Animation",
            51: "Idle Animation",
            52: "Jump Animation",
            53: "Run Animation",
            54: "Swim Animation",
            55: "Walk Animation",
            56: "Pose Animation",
            59: "LocalizationTableManifest",
            60: "LocalizationTableTranslation",
            61: "Emote Animation",
            62: "Video",
            63: "TexturePack",
            64: "T-Shirt Accessory",
            65: "Shirt Accessory",
            66: "Pants Accessory",
            67: "Jacket Accessory",
            68: "Sweater Accessory",
            69: "Shorts Accessory",
            70: "Left Shoe Accessory",
            71: "Right Shoe Accessory",
            72: "Dress Skirt Accessory"
        }
        return asset_types.get(type_id, f"Unknown Type ({type_id})")

if __name__ == "__main__":
    # Setup the application
    root = tk.Tk()
    app = RobloxScraper(root)
    
    # Set icon if available
    try:
        root.iconbitmap("roblox_icon.ico")
    except:
        pass
    
    # Start the main loop
    root.mainloop()