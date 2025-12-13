from datetime import datetime
from tkinter import filedialog, messagebox
from typing import Dict, Any

from src.data.manager import data_manager
from src.models.gear_export_model import GearConfigExport, GearExportData, GearSetExportData
from src.models.gear_models import GearSetSelection
from src.services.gear_preset_manager import GearPresetManager


class GearExportService:
    """驱动盘导出导入服务"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.preset_manager = GearPresetManager(self)

    def create_export_data(self) -> GearConfigExport:
        """创建导出数据"""
        from src.ui.tabs.gear_config_tab import GearConfigTab

        gear_tab: GearConfigTab = self.main_window.gear_tab
        gear_set_selection = self.main_window.gear_set_selection

        # 获取驱动盘数据
        gear_pieces = gear_tab.gear_slot_manager.get_all_gear_pieces()

        # 获取套装名称
        set_names = []
        for set_id in gear_set_selection.set_ids:
            gear_set = data_manager.get_gear_set(set_id)
            if gear_set:
                set_names.append(gear_set.name)

        # 创建套装数据
        gear_set_data = GearSetExportData(
            combination_type=gear_set_selection.combination_type,
            set_ids=gear_set_selection.set_ids,
            set_names=set_names
        )

        # 创建驱动盘数据
        gears_data = []
        for gear_piece in gear_pieces:
            gears_data.append(GearExportData.from_gear_piece(gear_piece))

        # 创建完整导出数据
        export_data = GearConfigExport(
            character_id=self.main_window.current_character_id,
            character_name=data_manager.get_character(
                self.main_window.current_character_id).name if self.main_window.current_character_id else "",
            weapon_id=self.main_window.current_weapon_id,
            weapon_name=data_manager.get_weapon(
                self.main_window.current_weapon_id).name if self.main_window.current_weapon_id else "",
            gears=gears_data,
            gear_set=gear_set_data,
            enhance_level=self.main_window.main_enhance_level.get()
        )

        return export_data

    def export_to_file(self):
        """导出到文件"""
        try:
            # 检查是否有配置
            gear_tab = self.main_window.gear_tab
            if not any(gear_piece.main_attribute for gear_piece in gear_tab.gear_slot_manager.get_all_gear_pieces()):
                messagebox.showwarning("导出警告", "没有配置驱动盘，无法导出！")
                return

            # 创建导出数据
            export_data = self.create_export_data()

            # 选择保存位置
            file_path = filedialog.asksaveasfilename(
                title="导出驱动盘配置",
                defaultextension=".json",
                filetypes=[
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ],
                initialfile=f"gear_config_{export_data.character_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            if file_path:
                # 保存文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(export_data.to_json())

                messagebox.showinfo("导出成功", f"驱动盘配置已导出到:\n{file_path}")
                self.main_window.update_status("驱动盘配置导出成功", "green")

        except Exception as e:
            messagebox.showerror("导出失败", f"导出过程中发生错误:\n{str(e)}")
            self.main_window.update_status(f"导出失败: {str(e)}", "red")

    def import_from_file(self):
        """从文件导入"""
        try:
            # 选择文件
            file_path = filedialog.askopenfilename(
                title="导入驱动盘配置",
                filetypes=[
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )

            if not file_path:
                return

            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                json_str = f.read()

            # 解析数据
            export_data = GearConfigExport.from_json(json_str)

            # 询问是否导入
            confirm_msg = f"是否导入以下配置？\n\n"
            confirm_msg += f"角色: {export_data.character_name}\n"
            confirm_msg += f"武器: {export_data.weapon_name}\n"
            confirm_msg += f"套装: {', '.join(export_data.gear_set.set_names)}\n"
            confirm_msg += f"驱动盘数量: {len(export_data.gears)}"

            if not messagebox.askyesno("确认导入", confirm_msg):
                return

            # 应用配置
            self.apply_export_data(export_data)

            messagebox.showinfo("导入成功", "驱动盘配置导入成功！")
            self.main_window.update_status("驱动盘配置导入成功", "green")

        except Exception as e:
            messagebox.showerror("导入失败", f"导入过程中发生错误:\n{str(e)}")
            self.main_window.update_status(f"导入失败: {str(e)}", "red")

    def apply_export_data(self, export_data: GearConfigExport):
        """应用导出数据到UI - 修复版本"""

        gear_tab = self.main_window.gear_tab

        print(f"\n=== 开始导入驱动盘配置 ===")
        print(f"版本: {export_data.version}")
        print(f"角色: {export_data.character_name} (ID: {export_data.character_id})")
        print(f"武器: {export_data.weapon_name} (ID: {export_data.weapon_id})")
        print(f"套装: {export_data.gear_set.combination_type}, IDs: {export_data.gear_set.set_ids}")
        print(f"强化等级: {export_data.enhance_level}")
        print(f"驱动盘数量: {len(export_data.gears)}")

        # 第一步：重置所有驱动盘
        print("[Import] 第一步：重置所有驱动盘")
        gear_tab.reset_all_gears()

        # 第二步：设置强化等级
        print(f"[Import] 第二步：设置强化等级为 {export_data.enhance_level}")
        self.main_window.main_enhance_level.set(export_data.enhance_level)

        # 第三步：应用套装配置
        print("[Import] 第三步：应用套装配置")
        gear_set_selection = GearSetSelection(
            combination_type=export_data.gear_set.combination_type,
            set_ids=export_data.gear_set.set_ids
        )
        self.main_window.gear_set_selection = gear_set_selection

        # 更新套装UI
        gear_tab.combination_type_var.set(export_data.gear_set.combination_type)
        gear_tab.selected_sets = export_data.gear_set.set_ids.copy()

        # 先更新套装下拉框列表
        gear_tab.update_combo_lists()

        # 然后设置选中的套装
        for i, set_id in enumerate(export_data.gear_set.set_ids):
            if i < len(gear_tab.set_combos):
                print(f"[Import] 设置套装{i + 1}: ID={set_id}")
                gear_tab.set_combos[i].set_selected_set_id(set_id)

        gear_tab.update_set_preview()

        # 第四步：应用驱动盘配置
        print("[Import] 第四步：应用驱动盘配置")
        for gear_data in export_data.gears:
            if 0 <= gear_data.slot_index < len(gear_tab.gear_slot_manager.slot_widgets):
                gear_widget = gear_tab.gear_slot_manager.slot_widgets[gear_data.slot_index]

                print(f"\n[Import] 导入驱动盘槽位 {gear_data.slot_index}:")
                print(f"  主属性: {gear_data.main_attribute.get('name', '无') if gear_data.main_attribute else '无'}")
                print(f"  副属性数量: {len(gear_data.sub_attributes)}")

                # 延迟一点点时间，确保UI更新
                self.main_window.root.update_idletasks()

                self._apply_gear_to_widget(gear_widget, gear_data)
            else:
                print(f"[Import] 警告: 无效的槽位索引 {gear_data.slot_index}")

        # 第五步：更新所有主属性显示
        print("[Import] 第五步：更新所有主属性显示")
        for gear_widget in gear_tab.gear_slot_manager.slot_widgets:
            gear_widget.update_main_attribute_value()

        # 第六步：更新副属性可用性
        print("[Import] 第六步：更新副属性可用性")
        for gear_widget in gear_tab.gear_slot_manager.slot_widgets:
            gear_widget.update_sub_attributes_availability()

        print("=== 导入完成 ===\n")

        # 更新状态
        self.main_window.update_status(f"已导入 {len(export_data.gears)} 个驱动盘配置", "blue")

    def _apply_gear_to_widget(self, gear_widget, gear_data: GearExportData):
        """应用单个驱动盘数据到UI组件"""
        # 应用主属性
        if gear_data.main_attribute:
            self._apply_main_attribute(gear_widget, gear_data.main_attribute)

        # 应用副属性
        for i, sub_attr_data in enumerate(gear_data.sub_attributes):
            if i < len(gear_widget.sub_widgets):
                self._apply_sub_attribute(gear_widget, i, sub_attr_data)

        # 更新副属性可用性
        gear_widget.update_sub_attributes_availability()

        # 更新主属性显示
        gear_widget.update_main_attribute_value()

    def _apply_main_attribute(self, gear_widget, main_attr_data: Dict[str, Any]):
        """应用主属性"""
        if not main_attr_data:
            return

        # 查找对应的主属性
        from src.config.manager import config_manager
        available_attrs = config_manager.slot_config.get_slot_main_attribute(gear_widget.slot_number)

        target_attr = None
        for attr in available_attrs:
            if self._attributes_match(attr, main_attr_data):
                target_attr = attr
                break

        if target_attr:
            gear_widget.main_attr_combo.set_selected_attribute(target_attr)
            print(f"[Import] 应用主属性到槽位 {gear_widget.slot_number}: {target_attr.name}")

    def _apply_sub_attribute(self, gear_widget, sub_index: int, sub_attr_data: Dict[str, Any]):
        """应用副属性 - 修复版本"""
        if not sub_attr_data:
            return

        widget = gear_widget.sub_widgets[sub_index]

        # 首先清空当前位置
        widget["combo"].set_selected_attribute(None)
        widget["spin_var"].set(0)
        widget["value_label"].config(text="0")

        if not sub_attr_data.get('name'):
            return  # 没有名称，跳过

        # 获取当前可用的副属性列表
        from src.config.manager import config_manager
        available_attrs = config_manager.slot_config.get_slot_sub_attribute()

        print(f"[Import] 查找副属性: {sub_attr_data.get('name')}")
        print(f"[Import] 可用副属性数量: {len(available_attrs)}")

        target_attr = None
        for attr in available_attrs:
            if self._attributes_match(attr, sub_attr_data):
                target_attr = attr
                print(f"[Import] 找到匹配的属性: {attr.name}")
                break

        if target_attr:
            try:
                # 设置副属性
                widget["combo"].set_selected_attribute(target_attr)
                widget["spin_var"].set(sub_attr_data.get('enhancement_level', 0))

                # 更新显示值
                enhancement_level = sub_attr_data.get('enhancement_level', 0)
                value = target_attr.calculate_value_at_level(enhancement_level)
                display_value = gear_widget.format_attribute_value(target_attr, value)
                widget["value_label"].config(text=display_value)

                print(f"[Import] 成功应用副属性: {target_attr.name}, 强化等级: {enhancement_level}")
            except Exception as e:
                print(f"[Import] 应用副属性时出错: {e}")
        else:
            print(f"[Import] 警告: 未找到匹配的副属性: {sub_attr_data.get('name')}")
            print(f"[Import] 详细数据: {sub_attr_data}")

    def _attributes_match(self, attr, attr_data: Dict[str, Any]) -> bool:
        """检查属性是否匹配"""
        try:
            if not attr_data:
                return False
            # 比较关键属性
            if attr.name != attr_data.get('name'):
                return False

            # 检查属性类型
            if hasattr(attr, 'attribute_type') and attr.attribute_type:
                if attr.attribute_type.value != attr_data.get('type'):
                    return False

            # 检查值类型
            if hasattr(attr, 'attribute_value_type') and attr.attribute_value_type:
                if attr.attribute_value_type.value != attr_data.get('value_type'):
                    return False

            # 检查数值（可选，用于进一步验证）
            if 'base' in attr_data:
                # 允许一定的浮点数误差
                if abs(attr.base - attr_data['base']) > 0.0001:
                    return False

            return True

        except Exception as e:
            print(f"[Import] 属性匹配错误: {e}")
            return False

    def copy_as_json(self):
        """复制为JSON到剪贴板"""
        try:
            export_data = self.create_export_data()
            json_str = export_data.to_json()

            # 复制到剪贴板
            self.main_window.root.clipboard_clear()
            self.main_window.root.clipboard_append(json_str)

            messagebox.showinfo("复制成功", "驱动盘配置已复制为JSON到剪贴板")
            self.main_window.update_status("配置已复制到剪贴板", "green")

        except Exception as e:
            messagebox.showerror("复制失败", f"复制过程中发生错误:\n{str(e)}")
            self.main_window.update_status(f"复制失败: {str(e)}", "red")

    def copy_as_base64(self):
        """复制为Base64到剪贴板（便于分享）"""
        try:
            export_data = self.create_export_data()
            base64_str = export_data.to_best_encode()

            # 复制到剪贴板
            self.main_window.root.clipboard_clear()
            self.main_window.root.clipboard_append(base64_str)

            messagebox.showinfo("复制成功", "驱动盘配置已编码为Base64并复制到剪贴板")
            self.main_window.update_status("配置已编码并复制到剪贴板", "green")

        except Exception as e:
            messagebox.showerror("复制失败", f"复制过程中发生错误:\n{str(e)}")
            self.main_window.update_status(f"复制失败: {str(e)}", "red")

    def paste_from_clipboard(self):
        """从剪贴板粘贴配置"""
        try:
            # 获取剪贴板内容
            clipboard_content = self.main_window.root.clipboard_get()
            content = clipboard_content.strip()

            if not clipboard_content.strip():
                messagebox.showwarning("粘贴失败", "剪贴板为空！")
                return

            export_data = None
            error_messages = []
            # 方法1：优先尝试Base64（推荐方案）
            try:
                export_data = GearConfigExport.from_best_encode(content)
                print("[Paste] 使用Base64解码成功")
            except Exception as e:
                error_messages.append(f"Base64解码失败: {str(e)[:50]}")

            # 方法2：尝试JSON
            if export_data is None:
                try:
                    export_data = GearConfigExport.from_json(content)
                    print("[Paste] 使用JSON解码成功")
                except Exception as e:
                    error_messages.append(f"JSON解码失败: {str(e)[:50]}")

            if export_data is None:
                # 输出调试信息
                print("[Paste] 所有解码尝试失败:")
                for msg in error_messages:
                    print(f"  {msg}")

                messagebox.showerror("粘贴失败",
                                     "无法识别的配置格式！\n\n" +
                                     "请确保复制的是：\n" +
                                     "1. Base64编码的配置（使用推荐方案导出）\n" +
                                     "2. 或JSON格式的配置")
                return

            # 询问是否导入
            self.apply_export_data(export_data)

            messagebox.showinfo("粘贴成功", "驱动盘配置已从剪贴板导入！")
            self.main_window.update_status("配置已从剪贴板导入", "green")

        except Exception as e:
            messagebox.showerror("粘贴失败", f"粘贴过程中发生错误:\n{str(e)}")
            self.main_window.update_status(f"粘贴失败: {str(e)}", "red")