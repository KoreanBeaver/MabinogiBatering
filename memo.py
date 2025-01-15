import tkinter as tk
from tkinter import ttk
import json
import os
import webbrowser

class CraftingChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crafting Checklist")
        self.trees = {}
        self.items = {}
        self.file_path = os.path.abspath("./checklist_data.json")  # 절대 경로로 설정
        self.load_data()  # 데이터 로드

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # 각 탭 생성 (탭 이름 수정)
        tab_names = ["Oasis", "Karu Forest", "Pera", "Calida"]  # 탭 이름 리스트
        for i, name in enumerate(tab_names, start=1):
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)  # 탭 이름 설정
            self.add_checkboxes(frame, i)

        reset_button = ttk.Button(root, text="Reset All", command=self.reset_all)
        reset_button.pack(pady=10)

    def add_checkboxes(self, frame, page_number):
        page_number = str(page_number)
        if page_number not in self.items.keys():
            self.items[page_number] = self.create_checklist_data(page_number)

        # Treeview 생성
        tree = ttk.Treeview(frame, columns=("Item", "Number", "Ingredient", "Quantity", "Check"), show="headings", height=15)
        tree.pack(fill="both", expand=True)
        tree.heading("Item", text="Item")
        tree.heading("Number", text="Number")
        tree.heading("Ingredient", text="Ingredient")
        tree.heading("Quantity", text="Quantity")
        tree.heading("Check", text="Check")
        tree.column("Item", anchor="center", width=120)
        tree.column("Number", anchor="center", width=80)
        tree.column("Ingredient", anchor="center", width=150)
        tree.column("Quantity", anchor="center", width=80)
        tree.column("Check", anchor="center", width=60)

        # Treeview 스타일 태그
        tree.tag_configure("main_item", font=("Arial", 12, "bold"))
        tree.tag_configure("sub_item", font=("Arial", 10))

        # 데이터 삽입
        for idx, item in enumerate(self.items[page_number]):
            check_symbol = "✔" if item["checked"] else "✘"
            main_row_id = tree.insert(
                "", "end", iid=f"{idx}_main",
                values=(item["item"], item["number"], "Click to see", "", check_symbol),
                tags=("main_item",)
            )

            # 하위 행 추가 (재료 세부 사항)
            for ingredient_idx, (ingredient, quantity) in enumerate(item["ingredients"]):
                ingredient_checked = item["ingredient_checks"][ingredient_idx]
                ingredient_symbol = "✔" if ingredient_checked else "✘"
                tree.insert(
                    main_row_id, "end", iid=f"{idx}_sub_{ingredient_idx}",
                    values=("", "", ingredient, quantity, ingredient_symbol),
                    tags=("sub_item",)
                )

        tree.bind("<Button-1>", lambda event, tree=tree, page_number=page_number: self.on_click(event, tree, str(page_number)))
        self.trees[str(page_number)] = tree

    def on_click(self, event, tree, page_number):
        region = tree.identify_region(event.x, event.y)
        column = tree.identify_column(event.x)
        row_id = tree.identify_row(event.y)

        if region == "cell" and column == "#5":  # Check 열 클릭
            if "_main" in row_id:  # 상위 항목 클릭
                self.toggle_check(tree, row_id, str(page_number))
            elif "_sub_" in row_id:  # 하위 항목 클릭
                self.toggle_sub_check(tree, row_id, str(page_number))

        elif region == "cell" and column == "#3":  # Ingredient 열 클릭
            if "_sub_" in row_id:
                self.open_link(tree, row_id, str(page_number))

    def toggle_check(self, tree, row_id, page_number):
        page_number = str(page_number)
        idx = int(row_id.split("_")[0])
        current_status = self.items[page_number][idx]["checked"]
        new_status = not current_status
        self.items[page_number][idx]["checked"] = new_status

        # 상위 항목 체크 변경
        check_symbol = "✔" if new_status else "✘"
        tree.set(row_id, column="Check", value=check_symbol)

        # 하위 항목 체크 상태 동기화
        for ingredient_idx in range(len(self.items[page_number][idx]["ingredients"])):
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

    def open_link(self, tree, row_id, page_number):
        main_idx, sub_idx = map(int, row_id.split("_")[0::2])
        ingredient_name = self.items[page_number][main_idx]["ingredients"][sub_idx][0]
        url = f"https://wiki.mabinogiworld.com/view/{ingredient_name.replace(' ', '_')}"
        webbrowser.open(url)

    def reset_all(self):
        for page_number, tree in self.trees.items():
            for idx in self.items[page_number]:
                idx["checked"] = False
                idx["ingredient_checks"] = [False] * len(idx["ingredients"])

            for row_id in tree.get_children():
                tree.set(row_id, column="Check", value="✘")
        self.save_data()

    def create_checklist_data(self, page_number):
        page_number = str(page_number)
        if page_number == "1":
            return [
                {"item": "Fine Sand", "number": 25, "ingredients": [["Braid", 50], ["Stamina 500 Potion", 75]], "checked": False, "ingredient_checks": [False, False]},
                {"item": "Prison Ghost Wings", "number": 15, "ingredients": [["Cotton Cushion Stuffing", 20], ["Finest Silk", 10]], "checked": False, "ingredient_checks": [False, False]},
                {"item": "Oasis Painting", "number": 10, "ingredients": [["Finest Leather Strap", 10], ["Tough Thread", 30]], "checked": False, "ingredient_checks": [False, False]},
                {"item": "Cactus Flower", "number": 8, "ingredients": [["Spirit Liqueur", 8], ["Silver Plate", 16], ["Fine Fabric", 32]], "checked": False, "ingredient_checks": [False, False, False]},
                {"item": "Giant Canine Fossil", "number": 3, "ingredients": [["Pet Playset", 3], ["Hay Bale", 9], ["Enchanted Firewood", 15]], "checked": False, "ingredient_checks": [False, False, False]}
            ]
        elif page_number == "2":
            return [
                {"item": "Mystic Stone", "number": 10, "ingredients": [["Shining Crystal", 5], ["Mana Dust", 15]], "checked": False, "ingredient_checks": [False, False]},
            ]
        elif page_number == "3":
            return [
                {"item": "Dragon Scale", "number": 8, "ingredients": [["Ancient Ore", 5], ["Magic Core", 12], ["Dragon Blood", 8]], "checked": False, "ingredient_checks": [False, False, False]},
                {"item": "Elven Bow", "number": 1, "ingredients": [["Enchanted Wood", 3], ["Silver Thread", 2]], "checked": False, "ingredient_checks": [False, False]},
            ]
        elif page_number == "4":
            return [
                {"item": "Healing Potion", "number": 50, "ingredients": [["Herbs", 30], ["Water", 20], ["Life Essence", 10]], "checked": False, "ingredient_checks": [False, False, False]},
                {"item": "Mana Potion", "number": 30, "ingredients": [["Mana Herb", 15], ["Essence of Magic", 10]], "checked": False, "ingredient_checks": [False, False]},
            ]
        else:
            return []

    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                self.items = json.load(file)
        else:
            self.items = {str(page): self.create_checklist_data(page) for page in range(1, 5)}
            self.save_data()

    def save_data(self):
        with open(self.file_path, "w") as file:
            json.dump(self.items, file, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = CraftingChecklistApp(root)
    root.mainloop()






