import sys
try:
    from importlib.metadata import entry_points
    # 兼容不同版本的 Python
    eps = entry_points(group='console_scripts') if sys.version_info >= (3, 10) else entry_points().get('console_scripts', [])
    for ep in eps:
        if ep.name == 'copaw':
            print(f"\n✅ 找到了！copaw 的入口点是: {ep.value}\n")
            break
    else:
        print("未找到 copaw 的入口点。")
except Exception as e:
    print("发生错误:", e)