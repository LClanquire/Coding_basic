import json
import os

DATA_FILE = "grammar_knowledge.json"

class GrammarKeeper:
    def __init__(self):
        self.knowledge = {}
        self.load_data()
    
    def load_data(self):
        """从文件加载已有数据，文件损坏时保留已有数据"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.knowledge = json.load(f)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ 数据文件损坏，已保留当前内存数据")
                print(f"   错误信息：{e}")
                # 不覆盖 self.knowledge，保留内存里的旧数据
        else:
            self.knowledge = {}
    
    def save_data(self):
        """保存数据到文件"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
    
    def multi_line_input(self, prompt):
        """多行输入函数：输入 EOF 单独一行结束"""
        print(prompt)
        print("（输入完成后，在新的一行输入 EOF 结束）")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == 'EOF':
                    break
                lines.append(line)
            except EOFError:
                break
        return '\n'.join(lines).strip()
    
    def add_entry(self, keyword, explanation):
        """添加或更新语法点"""
        if keyword in self.knowledge:
            print(f"⚠️ 已存在关键词 '{keyword}'，是否覆盖？(y/n)")
            if input().lower() != 'y':
                return
        self.knowledge[keyword] = {
            'explanation': explanation,
            'count': 0
        }
        self.save_data()
        print(f"✅ 已添加：{keyword}")
    
    def edit_entry(self, keyword):
        """修改已有的语法点"""
        if keyword not in self.knowledge:
            print(f"❌ 未找到 '{keyword}'")
            return
        
        print(f"\n当前解释：")
        print(self.knowledge[keyword]['explanation'])
        print("\n" + "-"*40)
        
        new_exp = self.multi_line_input("输入新的解释：")
        
        if new_exp:
            self.knowledge[keyword]['explanation'] = new_exp
            self.save_data()
            print(f"✅ 已更新：{keyword}")
        else:
            print("⏸️ 未做任何修改（输入为空）")
    
    def search(self, keyword):
        """搜索并计数"""
        found = False
        for k, v in self.knowledge.items():
            if keyword.lower() in k.lower():
                found = True
                v['count'] += 1
                print(f"\n🔍 [{k}] (查询次数: {v['count']})")
                print(v['explanation'])
        if not found:
            print(f"❌ 未找到 '{keyword}' 相关语法点")
        self.save_data()
    
    def show_hot(self):
        """显示最常查询的3条"""
        if not self.knowledge:
            print("📭 知识库为空")
            return
        sorted_items = sorted(self.knowledge.items(), key=lambda x: x[1]['count'], reverse=True)
        print("\n🔥 最常查询的语法点：")
        for k, v in sorted_items[:3]:
            print(f"   [{k}] 查询 {v['count']} 次")
    
    def list_all(self):
        """列出所有语法点"""
        if not self.knowledge:
            print("📭 知识库为空")
            return
        print("\n📚 所有语法点：")
        for k, v in self.knowledge.items():
            print(f"   • {k} (查询 {v['count']} 次)")
    
    def run(self):
        """主循环"""
        while True:
            print("\n" + "="*40)
            print("📘 语法知识库")
            print("  1. 添加语法点 (add)")
            print("  2. 搜索语法点 (search)")
            print("  3. 修改语法点 (edit)")
            print("  4. 查看热门 (hot)")
            print("  5. 列出全部 (list)")
            print("  6. 退出 (exit)")
            print("  7. 刷新数据(reload)")
            cmd = input("输入命令: ").strip().lower()
            
            if cmd == 'add':
                kw = input("输入关键词: ").strip()
                exp = self.multi_line_input("输入解释：")
                self.add_entry(kw, exp)
            elif cmd == 'search':
                kw = input("输入搜索关键词: ").strip()
                self.search(kw)
            elif cmd == 'edit':
                kw = input("输入要修改的关键词: ").strip()
                self.edit_entry(kw)
            elif cmd == 'hot':
                self.show_hot()
            elif cmd == 'list':
                self.list_all()
            elif cmd=='reload':
                self.load_data()
                print("🔄 已重新加载数据文件")
            elif cmd in ['exit', 'quit']:
                print("👋 再见！")
                break
            else:
                print("⚠️ 无效命令，请重试")

if __name__ == "__main__":
    app = GrammarKeeper()
    app.run()