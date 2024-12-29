import tkinter as tk
from tkinter import ttk
import json
import os


class CraftingChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crafting Checklist")
        self.trees = {}  # 각 탭의 Treeview를 저장
        self.items = {}  # 각 탭의 데이터를 저장
        self.file_path = "checklist_data.json"
        self.load_data()  # JSON 데이터 불러오기

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # 각 탭 생성
        for i in range(1, 5):
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=f"Page {i}")
            self.add_checkboxes(frame, i)

        # Reset 버튼 추가
        reset_button = ttk.Button(root, text="Reset All", command=self.reset_all)
        reset_button.pack(pady=10)

    def add_checkboxes(self, frame, page_number):
        # 데이터 초기화
        if page_number not in self.items:
            self.items[page_number] = self.create_checklist_data(page_number)

        # Treeview 생성
        tree = ttk.Treeview(frame, columns=("Item", "Number", "Ingredients", "Check"), show="headings", height=10)
        tree.pack(fill="both", expand=True)
        tree.heading("Item", text="Item")
        tree.heading("Number", text="Number")
        tree.heading("Ingredients", text="Ingredients")
        tree.heading("Check", text="Check")
        tree.column("Item", anchor="center", width=120)
        tree.column("Number", anchor="center", width=80)
        tree.column("Ingredients", anchor="center", width=200)
        tree.column("Check", anchor="center", width=60)

        # 데이터 삽입
        for idx, item in enumerate(self.items[page_number]):
            check_symbol = "✔" if item["checked"] else "✘"
            tree.insert("", "end", iid=idx, values=(item["item"], item["number"], item["ingredients"], check_symbol))

        # 이벤트 바인딩
        tree.bind("<Button-1>", lambda event, tree=tree, page_number=page_number: self.on_click(event, tree, page_number))

        self.trees[page_number] = tree

    def on_click(self, event, tree, page_number):
        region = tree.identify_region(event.x, event.y)
        if region == "cell":
            column = tree.identify_column(event.x)
            if column == "#4":  # Check 열 클릭
                row_id = tree.identify_row(event.y)
                if row_id:
                    self.toggle_check(tree, row_id, page_number)

    def toggle_check(self, tree, row_id, page_number):
        idx = int(row_id)
        current_status = self.items[page_number][idx]["checked"]
        new_status = not current_status
        self.items[page_number][idx]["checked"] = new_status
        check_symbol = "✔" if new_status else "✘"
        tree.set(row_id, column="Check", value=check_symbol)
        self.save_data()  # 변경 내용 저장

    def reset_all(self):
        for page_number, tree in self.trees.items():
            for idx in self.items[page_number]:
                idx["checked"] = False
            for row_id in tree.get_children():
                tree.set(row_id, column="Check", value="✘")
        self.save_data()  # 초기화 상태 저장

    def create_checklist_data(self, page_number):
        # 각 탭별 초기 데이터 생성
        if page_number == 1:  # 첫 번째 탭
            return [
                {"item": "Fine Sand", "number": 25, "ingredients": "Braid, Stamina 500 Potion", "checked": False},
                {"item": "Prison Ghost Wings", "number": 15, "ingredients": "Cotton Cushion, Finest Silk", "checked": False},
                {"item": "Oasis Painting", "number": 10, "ingredients": "Finest Leather Strap, Tough Thread", "checked": False},
                {"item": "Cactus Flower", "number": 8, "ingredients": "Spirit Liqueur", "checked": False},
                {"item": "Giant Canine Fossil", "number": 3, "ingredients": "Pet Playset, Hay Bale", "checked": False},
            ]
        elif page_number == 2:  # 두 번째 탭
            return [
                {"item": "Wooden Table", "number": 25, "ingredients": "Shyllien x 50, Shrimp Taming Bait x 100", "checked": False},
                {"item": "Wooden Craft", "number": 5, "ingredients": "Fire Essence, Mystic Cloth", "checked": False},
                {"item": "Ancient Relic", "number": 7, "ingredients": "Enchanted Wood, Silver Thread", "checked": False},
                {"item": "Elven Lantern", "number": 3, "ingredients": "Moonlight Shard, Mystic Cloth", "checked": False},
                {"item": "Dragon Claw", "number": 1, "ingredients": "Ancient Core, Sapphire", "checked": False},
            ]
        elif page_number == 3:  # 세 번째 탭
            return [
                {"item": "Healing Potion", "number": 50, "ingredients": "Herbs, Water", "checked": False},
                {"item": "Mana Potion", "number": 30, "ingredients": "Mana Herb, Essence of Magic", "checked": False},
                {"item": "Stamina Elixir", "number": 20, "ingredients": "Energizing Fruit, Fresh Milk", "checked": False},
                {"item": "Revival Stone", "number": 5, "ingredients": "Phoenix Feather, Sacred Water", "checked": False},
                {"item": "Shield Charm", "number": 10, "ingredients": "Iron Ingot, Magic Stone", "checked": False},
            ]
        elif page_number == 4:  # 네 번째 탭
            return [
                {"item": "Dragon Scale", "number": 8, "ingredients": "Ancient Ore, Magic Core", "checked": False},
                {"item": "Elven Bow", "number": 1, "ingredients": "Enchanted Wood, Silver Thread", "checked": False},
                {"item": "Knight's Sword", "number": 2, "ingredients": "Iron Blade, Leather Grip", "checked": False},
                {"item": "Wizard's Staff", "number": 3, "ingredients": "Magic Crystal, Oak Wood", "checked": False},
                {"item": "Golden Crown", "number": 1, "ingredients": "Gold Ingot, Sapphire Gem", "checked": False},
            ]
        else:
            return []

    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                self.items = json.load(file)
        else:
            self.items = {}

    def save_data(self):
        with open(self.file_path, "w") as file:
            json.dump(self.items, file)


if __name__ == "__main__":
    root = tk.Tk()
    app = CraftingChecklistApp(root)
    root.mainloop()












