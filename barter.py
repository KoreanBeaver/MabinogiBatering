import tkinter as tk
from tkinter import ttk
import json
import os


class CraftingChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crafting Checklist")
        self.trees = {}
        self.items = {}
        self.file_path = "checklist_data.json"
        self.load_data()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # 각 탭 생성
        for i in range(1, 5):
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=f"Page {i}")
            self.add_checkboxes(frame, i)

        reset_button = ttk.Button(root, text="Reset All", command=self.reset_all)
        reset_button.pack(pady=10)

    def add_checkboxes(self, frame, page_number):
        if page_number not in self.items:
            self.items[page_number] = self.create_checklist_data(page_number)

        # Treeview 생성
        tree = ttk.Treeview(frame, columns=("Item", "Number", "Ingredients", "Check"), show="headings", height=15)
        tree.pack(fill="both", expand=True)
        tree.heading("Item", text="Item")
        tree.heading("Number", text="Number")
        tree.heading("Ingredients", text="Ingredients")
        tree.heading("Check", text="Check")
        tree.column("Item", anchor="center", width=120)
        tree.column("Number", anchor="center", width=80)
        tree.column("Ingredients", anchor="center", width=200)
        tree.column("Check", anchor="center", width=60)

        # Treeview 스타일 태그
        tree.tag_configure("main_item", font=("Arial", 12, "bold"))  # 상위 항목 폰트 스타일
        tree.tag_configure("sub_item", font=("Arial", 10))          # 하위 항목 폰트 스타일

        # 데이터 삽입
        for idx, item in enumerate(self.items[page_number]):
            check_symbol = "✔" if item["checked"] else "✘"
            main_row_id = tree.insert(
                "", "end", iid=f"{idx}_main",
                values=(item["item"], item["number"], "Click to see", check_symbol),
                tags=("main_item",)  # 상위 항목 태그 적용
            )

            # 하위 행 추가 (재료 세부 사항)
            ingredients = item["ingredients"].split(", ")  # 쉼표로 나눔
            for ingredient_idx, ingredient in enumerate(ingredients):
                ingredient_checked = item.get("ingredient_checks", [False] * len(ingredients))[ingredient_idx]
                ingredient_symbol = "✔" if ingredient_checked else "✘"
                tree.insert(
                    main_row_id, "end", iid=f"{idx}_sub_{ingredient_idx}",
                    values=("", "", ingredient, ingredient_symbol),
                    tags=("sub_item",)  # 하위 항목 태그 적용
                )

        tree.bind("<Button-1>", lambda event, tree=tree, page_number=page_number: self.on_click(event, tree, page_number))
        self.trees[page_number] = tree

    def on_click(self, event, tree, page_number):
        region = tree.identify_region(event.x, event.y)
        column = tree.identify_column(event.x)
        row_id = tree.identify_row(event.y)

        if region == "cell" and column == "#4":  # Check 열 클릭
            if "_main" in row_id:  # 상위 항목 클릭
                self.toggle_check(tree, row_id, page_number)
            elif "_sub_" in row_id:  # 하위 항목 클릭
                self.toggle_sub_check(tree, row_id, page_number)

        elif region == "cell" and column == "#3" and "_main" in row_id:  # Ingredients 열 클릭
            self.toggle_expand(tree, row_id)

    def toggle_check(self, tree, row_id, page_number):
        idx = int(row_id.split("_")[0])
        current_status = self.items[page_number][idx]["checked"]
        new_status = not current_status
        self.items[page_number][idx]["checked"] = new_status

        # 상위 항목 체크 변경
        check_symbol = "✔" if new_status else "✘"
        tree.set(row_id, column="Check", value=check_symbol)

        # 하위 항목 체크 상태 동기화
        ingredients = self.items[page_number][idx]["ingredients"].split(", ")
        for ingredient_idx in range(len(ingredients)):
            sub_row_id = f"{idx}_sub_{ingredient_idx}"
            self.items[page_number][idx]["ingredient_checks"][ingredient_idx] = new_status
            tree.set(sub_row_id, column="Check", value=check_symbol)

        self.save_data()

    def toggle_sub_check(self, tree, row_id, page_number):
        main_idx, sub_idx = map(int, row_id.split("_")[0::2])
        current_status = self.items[page_number][main_idx]["ingredient_checks"][sub_idx]
        new_status = not current_status
        self.items[page_number][main_idx]["ingredient_checks"][sub_idx] = new_status

        # 하위 항목 체크 상태 변경
        check_symbol = "✔" if new_status else "✘"
        tree.set(row_id, column="Check", value=check_symbol)

        # 모든 하위 항목이 체크되었는지 확인
        all_checked = all(self.items[page_number][main_idx]["ingredient_checks"])
        self.items[page_number][main_idx]["checked"] = all_checked
        main_check_symbol = "✔" if all_checked else "✘"
        tree.set(f"{main_idx}_main", column="Check", value=main_check_symbol)

        self.save_data()

    def toggle_expand(self, tree, row_id):
        # 하위 행 토글
        if tree.item(row_id, "open"):
            tree.item(row_id, open=False)
        else:
            tree.item(row_id, open=True)

    def reset_all(self):
        for page_number, tree in self.trees.items():
            for idx in self.items[page_number]:
                idx["checked"] = False
                idx["ingredient_checks"] = [False] * len(idx["ingredients"].split(", "))
            for row_id in tree.get_children():
                if row_id.endswith("_main"):
                    tree.set(row_id, column="Check", value="✘")
                elif "_sub_" in row_id:
                    tree.set(row_id, column="Check", value="✘")
        self.save_data()

    def create_checklist_data(self, page_number):
        if page_number == 1:
            return [
                {"item": "Fine Sand", "number": 25, "ingredients": "Braid, Stamina 500 Potion", "checked": False, "ingredient_checks": [False, False]},
                {"item": "Prison Ghost Wings", "number": 15, "ingredients": "Cotton Cushion, Finest Silk", "checked": False, "ingredient_checks": [False, False]},
                {"item": "Prison Ghost Wings", "number": 15, "ingredients": "Cotton Cushion, Finest Silk,", "checked": False, "ingredient_checks": [False, False]}
            ]
        elif page_number == 2:
            return [
                {"item": "Mystic Stone", "number": 10, "ingredients": "Shining Crystal, Mana Dust", "checked": False, "ingredient_checks": [False, False]},
                {"item": "Phoenix Feather", "number": 5, "ingredients": "Fire Essence, Mystic Cloth", "checked": False, "ingredient_checks": [False, False]},
            ]
        elif page_number == 3:
            return [
                {"item": "Dragon Scale", "number": 8, "ingredients": "Ancient Ore, Magic Core", "checked": False, "ingredient_checks": [False, False]},
                {"item": "Elven Bow", "number": 1, "ingredients": "Enchanted Wood, Silver Thread", "checked": False, "ingredient_checks": [False, False]},
            ]
        elif page_number == 4:
            return [
                {"item": "Healing Potion", "number": 50, "ingredients": "Herbs, Water", "checked": False, "ingredient_checks": [False, False]},
                {"item": "Mana Potion", "number": 30, "ingredients": "Mana Herb, Essence of Magic", "checked": False, "ingredient_checks": [False, False]},
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
























