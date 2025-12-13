import json
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Dict

from src.config.manager import config_manager
from src.models.gear_export_model import GearConfigExport


class GearPresetManager:
    """驱动盘预设管理器"""

    def __init__(self, export_service):
        self.export_service = export_service
        self.main_window = export_service.main_window

    def get_preset_list(self) -> List[Dict[str, str]]:
        """获取预设列表"""
        presets = []

        for json_file in config_manager.file.presets_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    presets.append({
                        'name': json_file.stem,
                        'path': str(json_file),
                        'character': data.get('character_name', '未知'),
                        'time': data.get('export_time', '')
                    })
            except:
                continue

        # 按时间排序
        presets.sort(key=lambda x: x['time'], reverse=True)
        return presets

    def save_as_preset(self, preset_name: str = None):
        """保存为预设"""
        try:
            if not preset_name:
                # 弹出输入对话框
                from tkinter import simpledialog
                preset_name = simpledialog.askstring(
                    "保存预设",
                    "请输入预设名称:",
                    parent=self.main_window.root
                )

                if not preset_name:
                    return

            # 创建导出数据
            export_data = self.export_service.create_export_data()

            # 保存文件
            file_path = config_manager.file.presets_dir / f"{preset_name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(export_data.to_json())

            messagebox.showinfo("保存成功", f"预设 '{preset_name}' 已保存！")
            self.main_window.update_status(f"预设 '{preset_name}' 已保存", "green")

        except Exception as e:
            messagebox.showerror("保存失败", f"保存预设失败:\n{str(e)}")
            self.main_window.update_status(f"保存预设失败: {str(e)}", "red")

    def load_preset(self, preset_name: str):
        """加载预设"""
        try:
            file_path = config_manager.file.presets_dir / f"{preset_name}.json"

            if not file_path.exists():
                messagebox.showerror("加载失败", f"预设 '{preset_name}' 不存在！")
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                json_str = f.read()

            export_data = GearConfigExport.from_json(json_str)
            self.export_service.apply_export_data(export_data)

            messagebox.showinfo("加载成功", f"预设 '{preset_name}' 已加载！")

        except Exception as e:
            messagebox.showerror("加载失败", f"加载预设失败:\n{str(e)}")

    def delete_preset(self, preset_name: str):
        """删除预设"""
        try:
            file_path = config_manager.file.presets_dir / f"{preset_name}.json"

            if file_path.exists():
                if messagebox.askyesno("确认删除", f"确定要删除预设 '{preset_name}' 吗？"):
                    file_path.unlink()
                    messagebox.showinfo("删除成功", f"预设 '{preset_name}' 已删除！")
                    self.main_window.update_status(f"预设 '{preset_name}' 已删除", "blue")
            else:
                messagebox.showerror("删除失败", f"预设 '{preset_name}' 不存在！")

        except Exception as e:
            messagebox.showerror("删除失败", f"删除预设失败:\n{str(e)}")

    def show_preset_manager(self):
        """显示预设管理器窗口"""
        preset_window = tk.Toplevel(self.main_window.root)
        preset_window.title("驱动盘预设管理器")
        preset_window.geometry("600x400")

        # 获取预设列表
        presets = self.get_preset_list()

        # 创建列表框架
        list_frame = ttk.Frame(preset_window)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 列表标题
        ttk.Label(list_frame, text="预设列表", font=("", 12, "bold")).pack(anchor='w', pady=(0, 10))

        # 预设列表
        from tkinter import Listbox, Scrollbar

        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill='both', expand=True)

        scrollbar = Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')

        listbox = Listbox(listbox_frame, yscrollcommand=scrollbar.set, height=15)
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=listbox.yview)

        # 添加预设到列表
        for preset in presets:
            display_text = f"{preset['name']} - 角色: {preset['character']} - 时间: {preset['time'][:19]}"
            listbox.insert('end', display_text)
            listbox.itemconfig('end', {'bg': '#f0f0f0' if listbox.size() % 2 == 0 else 'white'})

        # 按钮框架
        button_frame = ttk.Frame(preset_window)
        button_frame.pack(fill='x', padx=10, pady=10)

        # 加载按钮
        ttk.Button(
            button_frame,
            text="加载选中预设",
            command=lambda: self._load_selected_preset(listbox, presets),
            width=15
        ).pack(side='left', padx=(0, 10))

        # 删除按钮
        ttk.Button(
            button_frame,
            text="删除选中预设",
            command=lambda: self._delete_selected_preset(listbox, presets),
            width=15
        ).pack(side='left', padx=(0, 10))

        # 关闭按钮
        ttk.Button(
            button_frame,
            text="关闭",
            command=preset_window.destroy
        ).pack(side='right')

    def _load_selected_preset(self, listbox, presets):
        """加载选中的预设"""
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("未选择", "请先选择一个预设！")
            return

        preset_index = selection[0]
        if 0 <= preset_index < len(presets):
            self.load_preset(presets[preset_index]['name'])

    def _delete_selected_preset(self, listbox, presets):
        """删除选中的预设"""
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("未选择", "请先选择一个预设！")
            return

        preset_index = selection[0]
        if 0 <= preset_index < len(presets):
            self.delete_preset(presets[preset_index]['name'])
            # 刷新列表
            listbox.delete(0, 'end')
            new_presets = self.get_preset_list()
            for preset in new_presets:
                display_text = f"{preset['name']} - 角色: {preset['character']} - 时间: {preset['time'][:19]}"
                listbox.insert('end', display_text)